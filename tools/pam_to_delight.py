#!/usr/bin/env python3
"""Move Pam's HarvestCraft 2 food recipes onto Farmer's Delight stations (for Hands-On Delight).

Reads the recipes straight out of the Pam's Food Core / Food Extended jars and writes a datapack
into kubejs/data:

  * pot / saucepan / bakeware / skillet  -> farmersdelight:cooking (cooking pot, <= 6 ingredients)
      - more than 6 ingredients          -> cutting-board assembly (Hands-On Delight)
      - skillet with bread or toast      -> cutting-board assembly (stacked like a sandwich)
      - skillet with a single ingredient -> campfire_cooking (cooked on the FD skillet)
  * cutting board / mixing bowl / juicer / grinder (2+ ingredients)
                                         -> cutting-board assembly: a tool-free shapeless recipe in the
                                            farmersdelight namespace, which Hands-On Delight picks up and
                                            removes from players' crafting grids
  * any tool with a single ingredient, roller, whole pizza -> slices
                                         -> farmersdelight:cutting with a knife
  * every original recipe that was converted, plus Pam's tool items, is disabled (neoforge:false)

Re-run after updating Pam's mods:
    python3 -I tools/pam_to_delight.py <instance mods dir> kubejs/data
"""
import glob
import json
import os
import shutil
import sys
import zipfile

HEATED = {"c:tool_pot", "c:tool_saucepan", "c:tool_bakeware", "c:tool_skillet"}
BOARD = {"c:tool_cuttingboard", "c:tool_mixingbowl", "c:tool_juicer", "c:tool_grinder", "c:tool_roller"}
POT_MAX = 6
DISABLE_TOOLS = True  # Pam's tool items have no use left once every recipe moves to a station

KNIFE = [{"type": "farmersdelight:item_ability", "action": "knife_dig"}, {"tag": "c:tools/knife"}]
DRINK_WORDS = ("juice", "smoothie", "tea", "coffee", "milkshake", "soda", "latte", "lemonade", "cider",
               "cocoa", "chocolatemilk", "punch", "shake", "soymilk", "eggnog", "wine", "beer")
DISABLED = {"neoforge:conditions": [{"type": "neoforge:false"}]}
OURS = ["farmersdelight/recipe/pamhc2", "handson_delight", "pamhc2foodcore", "pamhc2foodextended"]


def load_recipes(mods_dir):
    recipes = {}
    for jar in sorted(glob.glob(os.path.join(mods_dir, "pamhc2food*.jar"))):
        with zipfile.ZipFile(jar) as z:
            for name in z.namelist():
                if name.startswith("data/") and "/recipe/" in name and name.endswith(".json"):
                    # some of Pam's files carry trailing junk after the object
                    recipes[name[len("data/"):]] = json.JSONDecoder().raw_decode(z.read(name).decode())[0]
    if not recipes:
        sys.exit(f"no pamhc2food*.jar recipes found in {mods_dir}")
    return recipes


def is_tool(ing):
    return isinstance(ing, dict) and str(ing.get("tag", "")).startswith("c:tool_")


def tab(result_id):
    return "drinks" if any(w in result_id.split(":")[1] for w in DRINK_WORDS) else "meals"


def cooking(ings, result):
    return {"type": "farmersdelight:cooking", "ingredients": ings, "result": result,
            "cookingtime": 200, "experience": 0.35, "recipe_book_tab": tab(result["id"])}


def cutting(ing, result):
    return {"type": "farmersdelight:cutting", "ingredients": [ing], "tool": KNIFE,
            "result": [{"item": {"id": result["id"], "count": result.get("count", 1)}}]}


def board(ings, result):
    return {"type": "minecraft:crafting_shapeless", "category": "misc", "ingredients": ings, "result": result}


def skillet(ing, result):
    return {"type": "minecraft:campfire_cooking", "category": "food", "ingredient": ing, "result": result,
            "cookingtime": 200, "experience": 0.35}


def convert(path, r):
    """-> (station, new recipe) or None to leave the recipe alone."""
    if r.get("type") != "minecraft:crafting_shapeless":
        return None
    ings = r["ingredients"]
    tools = [i["tag"] for i in ings if is_tool(i)]
    rest = [i for i in ings if not is_tool(i)]
    result = r["result"]
    if not tools:
        # whole pizza -> slices: slice it on the board
        if len(rest) == 1 and "pizzaslice" in result["id"]:
            return "knife", cutting(rest[0], result)
        return None
    tool = tools[0]
    if len(rest) == 1:
        if tool == "c:tool_skillet":
            return "skillet", skillet(rest[0], result)
        if tool in HEATED:
            return "pot", cooking(rest, result)
        return "knife", cutting(rest[0], result)
    all_same = all(i == rest[0] for i in rest)
    if tool == "c:tool_skillet" and not all_same and any(
            str(i.get("tag", i.get("item", ""))).split(":")[-1] in ("bread", "toast") for i in rest):
        # grilled sandwiches and toast toppings: stacked on the board like Farmer's Delight's own
        return "board", board(rest, result)
    if tool in HEATED or all_same:
        # Hands-On Delight skips board recipes made of one kind of thing, so those go in the pot
        if len(rest) <= POT_MAX:
            return "pot", cooking(rest, result)
        return "board", board(rest, result)
    if tool in BOARD:
        return "board", board(rest, result)
    raise ValueError(f"unknown tool {tool} in {path}")


def write(out, rel, data):
    p = os.path.join(out, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    mods_dir, out = sys.argv[1], sys.argv[2]
    recipes = load_recipes(mods_dir)
    for d in OURS:
        shutil.rmtree(os.path.join(out, d), ignore_errors=True)

    counts, board_results, left = {}, set(), []
    for path, r in sorted(recipes.items()):
        ns, _, name = path.partition("/recipe/")
        if DISABLE_TOOLS and ns == "pamhc2foodcore" and name.startswith("tool_"):
            write(out, path, DISABLED)
            counts["tool disabled"] = counts.get("tool disabled", 0) + 1
            continue
        conv = convert(path, r)
        if conv is None:
            left.append(path)
            continue
        station, new = conv
        write(out, f"farmersdelight/recipe/pamhc2/{ns}/{name}", new)
        write(out, path, DISABLED)
        counts[station] = counts.get(station, 0) + 1
        if station == "board":
            board_results.add(new["result"]["id"])

    # board dishes whose result is not food (dough, butter, ...) still have to leave the crafting grid
    write(out, "handson_delight/tags/item/assembled.json",
          {"replace": False, "values": [{"id": i, "required": False} for i in sorted(board_results)]})

    print(f"{len(recipes)} recipes read")
    for k in ("pot", "board", "knife", "skillet", "tool disabled"):
        print(f"  {k:14} {counts.get(k, 0)}")
    print(f"  {'left alone':14} {len(left)} (smelting/smoking/campfire, sugar, seeds, fresh water/milk)")


if __name__ == "__main__":
    main()

#!/usr/bin/env bash
# Run from your pack folder (the one with pack.toml in it).
# Sets side = "client" on mods that only run on the client,
# then refreshes the index so the hashes match.

client_mods=(
  sodium
  irisshaders
  continuity
  colorwheel
  controlling
  searchables
  mouse-tweaks
  skin-layers-3d
  betterf3
  sound-physics-remastered
  extreme-sound-muffler
  mod-name-tooltip
  better-advanced-tooltips
  memory-settings
  xaeros-minimap
  overflowing-bars
  lambdynamiclights
)

missing=()

for slug in "${client_mods[@]}"; do
  file="mods/$slug.pw.toml"
  if [[ -f "$file" ]]; then
    sed -i 's/^side = .*/side = "client"/' "$file"
    echo "client: $slug"
  else
    missing+=("$slug")
  fi
done

packwiz refresh

if (( ${#missing[@]} )); then
  echo
  echo "Couldn't find these files (name may differ, check mods/ folder):"
  printf '  %s\n' "${missing[@]}"
fi

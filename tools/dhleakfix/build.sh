#!/bin/bash
# Builds dhleakfix-<ver>.jar against the ATLauncher CreatePack instance (Mixin + NeoForge libs; DH is targeted by name, not compiled against).
# Usage: tools/dhleakfix/build.sh   -> writes tools/dhleakfix/build/dhleakfix-1.0.0.jar
set -e
cd "$(dirname "$0")"
I=~/.var/app/com.atlauncher.ATLauncher/data/instances/CreatePack
L=~/.var/app/com.atlauncher.ATLauncher/data/libraries
CP="$L/net/fabricmc/sponge-mixin/0.15.2+mixin.0.8.7/sponge-mixin-0.15.2+mixin.0.8.7.jar:$L/net/neoforged/fancymodloader/loader/4.0.43/loader-4.0.43.jar"
rm -rf build && mkdir -p build/classes
javac -nowarn --release 21 -proc:none -cp "$CP" -d build/classes $(find src -name '*.java')
cp -r res/* build/classes/
(cd build/classes && jar --create --file ../dhleakfix-1.0.0.jar .)
echo "built build/dhleakfix-1.0.0.jar"

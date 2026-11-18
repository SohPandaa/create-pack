#!/bin/bash
# Builds balloonshaderfix-<ver>.jar against the ATLauncher CreatePack instance (Iris jar + NeoForge libs).
# Usage: tools/balloonshaderfix/build.sh   -> writes tools/balloonshaderfix/build/balloonshaderfix-1.0.0.jar
set -e
cd "$(dirname "$0")"
I=~/.var/app/com.atlauncher.ATLauncher/data/instances/CreatePack
L=~/.var/app/com.atlauncher.ATLauncher/data/libraries
CP="$(ls $I/mods/iris-neoforge-*.jar):$L/net/fabricmc/sponge-mixin/0.15.2+mixin.0.8.7/sponge-mixin-0.15.2+mixin.0.8.7.jar:$L/net/neoforged/fancymodloader/loader/4.0.43/loader-4.0.43.jar"
rm -rf build && mkdir -p build/classes
javac -nowarn --release 21 -proc:none -cp "$CP" -d build/classes $(find src -name '*.java')
cp -r res/* build/classes/
(cd build/classes && jar --create --file ../balloonshaderfix-1.0.0.jar .)
echo "built build/balloonshaderfix-1.0.0.jar"

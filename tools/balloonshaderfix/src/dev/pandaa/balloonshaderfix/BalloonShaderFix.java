package dev.pandaa.balloonshaderfix;

import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;

/**
 * Create Aeronautics draws a hot-air "heat" overlay for balloons into its own framebuffer and blends it
 * over the screen with a depth test against minecraft:main. With an Iris shader pack active, the main
 * depth buffer doesn't hold the shader pack's scene depth, so the overlay lands in the wrong place and
 * shows up as a pale ghost copy of the balloon. This mod skips that overlay while a shader pack is in use.
 */
@Mod(BalloonShaderFix.MOD_ID)
public final class BalloonShaderFix {
    public static final String MOD_ID = "balloonshaderfix";

    private static Boolean irisLoaded;

    public BalloonShaderFix() {
    }

    public static boolean shaderPackActive() {
        if (irisLoaded == null) {
            irisLoaded = ModList.get().isLoaded("iris");
        }
        return irisLoaded && IrisCheck.shaderPackInUse();
    }
}

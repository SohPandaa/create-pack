package dev.pandaa.balloonshaderfix;

import net.irisshaders.iris.api.v0.IrisApi;

/** Kept separate so Iris classes are only loaded when Iris is installed. */
final class IrisCheck {
    private IrisCheck() {
    }

    static boolean shaderPackInUse() {
        return IrisApi.getInstance().isShaderPackInUse();
    }
}

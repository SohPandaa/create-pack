package dev.pandaa.balloonshaderfix.mixin;

import dev.pandaa.balloonshaderfix.BalloonShaderFix;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Pseudo
@Mixin(targets = "dev.eriksonn.aeronautics.content.blocks.hot_air.balloon.effect.ClientBalloonEffectRenderer", remap = false)
public abstract class ClientBalloonEffectRendererMixin {

    @Inject(method = "onRenderLevelStage", at = @At("HEAD"), cancellable = true, require = 0)
    private static void balloonshaderfix$skipWithShaders(final CallbackInfo ci) {
        if (BalloonShaderFix.shaderPackActive()) {
            ci.cancel();
        }
    }
}

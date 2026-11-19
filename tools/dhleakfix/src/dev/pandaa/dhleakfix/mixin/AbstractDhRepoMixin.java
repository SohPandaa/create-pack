package dev.pandaa.dhleakfix.mixin;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Pseudo
@Mixin(targets = "com.seibel.distanthorizons.core.sql.repo.AbstractDhRepo", remap = false)
public abstract class AbstractDhRepoMixin {

    /** Connection opened by the current thread inside the getConnection lambda, until it returns or fails. */
    @Unique
    private static final ThreadLocal<Connection> dhleakfix$pending = new ThreadLocal<>();

    @Redirect(method = "lambda$getConnection$0", require = 0,
            at = @At(value = "INVOKE", target = "Ljava/sql/DriverManager;getConnection(Ljava/lang/String;)Ljava/sql/Connection;"))
    private Connection dhleakfix$remember(final String url) throws SQLException {
        final Connection connection = DriverManager.getConnection(url);
        dhleakfix$pending.set(connection);
        return connection;
    }

    @Inject(method = "lambda$getConnection$0", at = @At("RETURN"), require = 0)
    private void dhleakfix$success(final CallbackInfoReturnable<Connection> cir) {
        dhleakfix$pending.remove();
    }

    /** Runs in the catch block, just before DH wraps the error in a RuntimeException and rethrows. */
    @Inject(method = "lambda$getConnection$0", require = 0,
            at = @At(value = "NEW", target = "java/lang/RuntimeException"))
    private void dhleakfix$closeOnFailure(final CallbackInfoReturnable<Connection> cir) {
        final Connection connection = dhleakfix$pending.get();
        dhleakfix$pending.remove();
        if (connection != null) {
            try {
                connection.close();
            } catch (final Exception ignored) {
            }
        }
    }
}

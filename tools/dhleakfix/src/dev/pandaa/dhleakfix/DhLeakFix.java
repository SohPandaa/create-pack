package dev.pandaa.dhleakfix;

import net.neoforged.fml.common.Mod;

/**
 * Distant Horizons 3.3.3 AbstractDhRepo.getConnection() opens a SQLite connection per thread, then runs
 * "PRAGMA synchronous". If that statement throws (seen as SQLITE_IOERR_SHORT_READ on the Nether/End DBs of
 * Flashback's temporary replay world), the catch block logs and rethrows without closing the connection.
 * DH's update propagator retries several times a second, so native SQLite memory grows without bound
 * (the Java heap stays flat) until the machine runs out of RAM. See AbstractDhRepoMixin.
 */
@Mod("dhleakfix")
public final class DhLeakFix {
    public DhLeakFix() {
    }
}

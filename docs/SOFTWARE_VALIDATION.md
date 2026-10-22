# Software validation — 2026-10-22

Tested implementation commit: **807fa9531d939939ac0a1a25a10aaae53e735c5e**. Subsequent commits contain documentation/CAD evidence only. Baseline: `c9a24af93514cc6a27fa56c0eb7bdf4c22a49692`. The results below were obtained locally. Remote CI status is tracked on the GitHub pull request; no robot has been connected or deployed.

## Behavioral tests

Run with Temurin JDK 17.0.20.1 and Python 3. The harness compiles actual production OpModes with `javac --release 8` and runs them with SDK doubles; no Android SDK or actual SolversLib classes are loaded by these harnesses.

```text
python3 tests/verify_bench.py
PASS bench: 21 scenarios, 105 frames (SDK doubles; no hardware).
python3 tests/verify_drive.py
PASS drive: 106 assertions (library call spy; no kinematics/hardware).
```

Bench coverage: init zero and raw/BRAKE/FORWARD configuration; iterative lifecycle; held-enable startup interlock; four motors in both directions; 15% maximum; just before and exactly at the two-second cutoff; timeout lockout; bumper release and re-arm; changed corner, direction, selection release and multiple buttons; invalid initial selection requiring bumper release; Back latch; stop during an active burst; stop before init; and missing hardware at each initialization stage.

Drive coverage: configuration names/order; explicit motor inversion with library auto inversion false; raw/BRAKE mode; init/init_loop/start zero; zero/deadband and boundary inputs; continuous deadband rescaling; both signs of translation and turn; squared-input flag; 25/55/70% limits; exact 20% trigger boundary; precision precedence; Cross suppress/resume; Back latch; explicit stop; new initialization clearing the latch; and missing hardware at each initialization stage. The drive spy records calls and uses an arbitrary nonzero sentinel so stop tests can detect lingering power. It does **not** simulate mecanum outputs or confirm library math.

## Real Android build

```text
./gradlew :TeamCode:assembleDebug --no-daemon --stacktrace
BUILD SUCCESSFUL in 1m 10s
52 actionable tasks: 52 executed
```

The initial network-enabled run resolved the declared published dependencies and installed missing Android platform 30 / build tools 35.0.0 using already accepted SDK licenses. After the final Java/test changes, the cached verification run was:

```text
./gradlew :TeamCode:assembleDebug --offline --no-daemon --stacktrace
BUILD SUCCESSFUL in 4s
52 actionable tasks: 9 executed, 43 up-to-date
```

Environment: macOS ARM64, Temurin 17.0.20.1, Gradle 9.1.0, AGP 8.13.2, Android compile SDK 30, build tools 35.0.0; FTC dependencies 12.0.0 and SolversLib core 0.3.6. The project Java source/target is 8; CI JVM is 17. The real build validates the Motor and MecanumDrive API calls against published libraries, separately from the doubles.

One sandboxed attempt failed before Gradle startup with `FileLockContentionHandler` / `SocketException: Operation not permitted`; the same cached build succeeded with its local coordination socket permitted. Nonblocking toolchain notices included SDK XML schema-version mismatch, native libraries packaged without stripping, and Gradle deprecations affecting a future Gradle 10 migration. No version upgrade was made to hide them.

## APK inspection

Output: `TeamCode/build/outputs/apk/debug/TeamCode-debug.apk` (52,974,667 bytes).

SHA-256: `c91c0c26ceb740f84fa32b7ee8fbb8a4096b228fd6bad50f947964f883200ce7`

- `aapt dump badging`: application `com.qualcomm.ftcrobotcontroller`, version code 63, version name 12.0, compile SDK 30, minimum SDK 24, target SDK 28.
- `apksigner verify --verbose`: **Verifies**, v2 signature true, one signer. This is the upstream debug signing configuration, not a production release signature.
- DEX inspection finds `Lorg/firstinspires/ftc/teamcode/MorpheusDrive;` and `Lorg/firstinspires/ftc/teamcode/FourMotorBenchTest;`.
- Native libraries present for `armeabi-v7a` and `arm64-v8a`.

The APK is a local build output and is ignored by Git. CI will upload its own build artifact after a successful remote run. No APK install, Driver Station controller-mapping test, Control Hub connection, electrical test, encoder test, or motion test was performed.

## CAD and repository checks

The read-only CAD extractor completed with inch/mm conversion and assertions for four drive wheels, four drive motors, ten roller axles per wheel, orthogonal placements, motor/axle cylinder-axis geometry, and 45° roller slants. Evidence and source checksum are in [the CAD audit](CAD_DRIVETRAIN_AUDIT.md). This verifies extraction consistency, not the as-built robot.

Final diff review checks explicit single inversion, exact hardware names, commissioning caps, no stale linear harness, removal of root FourMotor.java, no CI source rewriting, and clean whitespace. The feature branch was subsequently published through authenticated Git after the owner completed GitHub CLI sign-in. Review current remote build status on the GitHub pull request. [Hardware acceptance](DRIVETRAIN_VALIDATION.md) remains mandatory.

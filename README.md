# Morpheus FTC drivetrain

FTC SDK **12.0.0**, SolversLib **core 0.3.6**, Android Gradle Plugin **8.13.2**, Gradle **9.1.0**, JDK **17**. Open the repository root in Android Studio; see [setup](ANDROID_SETUP.md).

Two iterative TeleOps are included:

- **Morpheus: Four Motor Bench Test** — individual motor identification, 15% power, two-second bursts, L1 enable, R1 reverse, and Back/Create latched stop.
- **Morpheus: PS5 Mecanum Drive** — robot-centric SolversLib drive with explicit motor directions, BRAKE, and raw-power control.

Software verification passes locally; **physical drivetrain validation has not been performed**. Direction settings remain provisional until each motor and motion is tested. [CAD audit and evidence](docs/CAD_DRIVETRAIN_AUDIT.md) establish mechanical layout and a conditional inversion prediction, not wiring or electrical polarity. Follow [hardware acceptance](docs/DRIVETRAIN_VALIDATION.md) before floor driving.

## PS5 / DualSense controls (gamepad1)

| Input | Drive action |
| --- | --- |
| Left stick Y | Forward/backward (SDK Y negated) |
| Left stick X | Left/right strafe |
| Right stick X | Rotate |
| L2 > 20% | 25% precision; takes priority over R2 |
| No trigger | 55% normal cap |
| R2 > 20% | 70% commissioning turbo cap |
| Cross (`a`) | Hold to command zero; releasing permits motion to resume |
| Back/Create (`back`) | Latch zero until OpMode restart |
| Driver Station STOP | Stop the OpMode |

A rescaled 5% stick deadband feeds SolversLib's squared-input option. Verify face-button and Back/Create mapping on the actual Driver Station. Full-speed operation is disabled. Hold L2 throughout the first combined-motion tests on blocks.

## Hardware configuration

| Proposed Control Hub port | Exact configuration name | Bench selection (FTC / PS5) |
| --- | --- | --- |
| 0 | `frontLeft` | A / Cross |
| 1 | `frontRight` | B / Circle |
| 2 | `backLeft` | X / Square |
| 3 | `backRight` | Y / Triangle |

Ports are a proposal, not CAD-derived. Trace and record the actual hub/port per corner with power off. Select the actual motor type. Motors in the bench OpMode are all FORWARD for identification; the drive provisionally reverses the right side. `new MecanumDrive(false, ...)` disables automatic library inversion so it is not applied twice. Encoder readings are available, but this drive does not regulate speed using encoders or an IMU.

## Build and verify

With JDK 17, Python 3, and an Android SDK configured via `ANDROID_HOME` or ignored `local.properties`:

```sh
python3 tests/verify_bench.py
python3 tests/verify_drive.py
./gradlew :TeamCode:assembleDebug --no-daemon --stacktrace
```

The Java behavioral tests compile the real OpMode sources against small SDK doubles and a SolversLib call spy. They verify lifecycle, controller mapping, limits, re-arm behavior, and stops; they do not simulate wheel physics. The Gradle build separately compiles against the real published FTC and SolversLib libraries and packages the debug Robot Controller APK at `TeamCode/build/outputs/apk/debug/TeamCode-debug.apk`.

[Morpheus Robot CI](.github/workflows/robot-ci.yml) runs on main, this feature branch, pull requests, or manual dispatch. It tests and builds the checked-out code, then uploads the debug APK. It has read-only repository permissions and never rewrites or commits source. A local build pass does not establish a GitHub Actions pass or deploy an APK.

See [software validation](docs/SOFTWARE_VALIDATION.md), [engineering decisions and limits](docs/ENGINEERING_LOG.md), and [measured test log](TEST_LOG.csv). No hardware PASS results are recorded in advance. Keep new work on feature branches and review through PRs; this integration must not be merged automatically.

The full FTC project and upstream license are retained. Upstream project reference: [FIRST-Tech-Challenge/FtcRobotController](https://github.com/FIRST-Tech-Challenge/FtcRobotController), commit `e14c2aeb33e84d4ea21697beeea9ac49557be870`. SolversLib's [published 0.3.6 sources](https://repo.dairy.foundation/releases/org/solverslib/core/0.3.6/core-0.3.6-sources.jar) were checked for constructor ordering, explicit inversion, squared inputs, and stop behavior.

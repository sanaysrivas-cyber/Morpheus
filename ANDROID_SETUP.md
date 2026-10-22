# Morpheus Android Studio setup

The repository is a complete FTC Robot Controller 12.0.0 Android project. Gradle resolves `org.solverslib:core:0.3.6` from the Dairy releases repository declared in `TeamCode/build.gradle`; no separate Android Studio SolversLib plugin is required. CAD is not a build dependency.

1. Clone `https://github.com/sanaysrivas-cyber/Morpheus.git` and check out the reviewed feature branch. Open the **repository root**, containing `settings.gradle`, rather than `TeamCode` alone.
2. Use Android Studio with support for AGP 8.13.2. Set the Gradle JDK to **17**. The wrapper supplies Gradle 9.1.0; Java source/target compatibility remains the upstream Java 8 setting.
3. Configure the Android SDK location. Install platform `android-30` and build tools `35.0.0`; accept their licenses through your normal Android SDK setup. The project compiles with SDK 30 and targets 28 with minimum 24, retaining upstream settings.
4. Sync Gradle. Source is under `TeamCode/src/main/java/org/firstinspires/ftc/teamcode/`: `FourMotorBenchTest.java` for commissioning and `MorpheusDrive.java` for PS5 mecanum drive.
5. Run both Python test scripts and `./gradlew :TeamCode:assembleDebug --no-daemon --stacktrace`. Details and results are in [software validation](docs/SOFTWARE_VALIDATION.md).
6. For hardware commissioning, connect the Control Hub through the team's normal USB/ADB connection and use the TeamCode run configuration. Confirm compatible Robot Controller/Driver Station versions. Deploying replaces the installed Robot Controller application; this software session did not deploy to a robot.
7. Start with the **Four Motor Bench Test** and the [hardware acceptance procedure](docs/DRIVETRAIN_VALIDATION.md). Keep wheels clear and verify all stop controls. Motor ports and polarity still need physical confirmation.

## GitHub Actions APK

After the branch is published, open Actions → **Morpheus Robot CI**. A successful run provides `Morpheus-RobotController-debug` with the APK. The workflow also runs on PRs and main. An artifact proves packaging, not hardware behavior. This workflow no longer bootstraps, edits, commits, or pushes an FTC project.

## Upstream and library references

The upstream FTC project is pinned by provenance to `e14c2aeb33e84d4ea21697beeea9ac49557be870`; LICENSE remains intact. [SolversLib installation](https://docs.seattlesolvers.com/installation), [published 0.3.6 source archive](https://repo.dairy.foundation/releases/org/solverslib/core/0.3.6/core-0.3.6-sources.jar).

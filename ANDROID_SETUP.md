# Morpheus Android Studio setup

This repository now includes the full FTC Robot Controller 12.0.0 project, Gradle wrapper, and SolversLib core 0.3.6.
Upstream source: FIRST-Tech-Challenge/FtcRobotController at e14c2aeb33e84d4ea21697beeea9ac49557be870. The upstream license is retained in LICENSE.

## Open in Android Studio

1. Install Android Studio from https://developer.android.com/studio if needed. Use a version supporting Android Gradle Plugin 8.13.2.
2. From the welcome screen choose Get from VCS / Clone Repository. URL: https://github.com/sanaysrivas-cyber/Morpheus.git . Sign into GitHub as an account with access to this private repository.
3. If you already cloned Morpheus, use Git > Pull, then reopen its root directory (the folder containing settings.gradle). Do not open TeamCode alone.
4. Allow Gradle sync and install the Android SDK components requested by Android Studio. Use JDK 17 or a compatible bundled JDK as the Gradle JDK. This project uses Gradle 9.1.0 and compile SDK 30.
5. In the Project panel, select Project view. Open TeamCode/build.gradle to see implementation 'org.solverslib:core:0.3.6' and the Dairy Maven repository.
6. Your motor code is TeamCode/src/main/java/org/firstinspires/ftc/teamcode/FourMotorBenchTest.java. In Android view it is under TeamCode > java > org.firstinspires.ftc.teamcode.
7. Select the TeamCode run configuration. Build the app, connect the Control Hub using the team's normal USB/ADB connection, select that device, and click Run. Use a Driver Station version compatible with FTC SDK 12.0.0.
8. On Driver Station choose TeleOp > Morpheus: Four Motor Bench Test. Follow the wiring and controls in README.md. Physical motor testing is still required.

## GitHub build and download

Open Actions > Android setup and build > Run workflow. A successful run provides the Morpheus-RobotController-debug artifact containing the APK. Download it from that run's Artifacts section. Builds do not deploy to a robot.

## SolversLib

Gradle downloads the library automatically during sync/build; there is no separate Android Studio plugin to install. Core is installed without optional Pedro Pathing or Photon modules. The existing motor test uses FTC SDK motor APIs and does not require a rewrite to use the project with SolversLib installed.
Installation reference: https://docs.seattlesolvers.com/installation

## Verification

The workflow runs the existing 14 mock motor scenarios and assembles the real TeamCode debug APK. Check the run result for build success. Neither step confirms physical wiring, motor direction, or behavior on your Control Hub.

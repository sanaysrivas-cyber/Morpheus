**Android Studio project:** [Open and build Morpheus](ANDROID_SETUP.md). SolversLib configuration: [TeamCode/build.gradle](TeamCode/build.gradle).

# Morpheus four-motor commissioning reference

Prepared September 26, 2026 for code review Monday September 28 and physical testing Tuesday September 29.

## Status and authorship
Morpheus FTC Team

## Install in the team's FTC project

1. Use the team's approved FTC Robot Controller SDK project and compatible Robot Controller/Driver Station versions. If there is no project, start from https://github.com/FIRST-Tech-Challenge/FtcRobotController and select the release approved for your season.
2. Open this repository root in Android Studio. The full FTC project and `FourMotorBenchTest.java` are included; follow [Android Studio setup](ANDROID_SETUP.md).
3. Configure the four Control Hub motor ports as below. Select the actual motor type; do not guess the model.
4. Build the Robot Controller app in Android Studio. Resolve any build errors before deployment. Deploy using the team's normal Control Hub connection.
5. Select `Morpheus: Four Motor Bench Test` in Driver Station TeleOp. INIT must produce no motor motion. Check the controls below before START.

## Proposed wiring and configuration

These names/ports are a proposed convention, not extracted from the CAD. Adapt the names in code if the team already has an agreed mapping. Names are case-sensitive.

| Control Hub motor port | Configuration name | Gamepad 1 button |
| --- | --- | --- |
| 0 | frontLeft | A |
| 1 | frontRight | B |
| 2 | backLeft | X |
| 3 | backRight | Y |

Power the hub off before changing wiring. Connect each motor's power cable to its designated motor port. For encoder readings, connect that motor's compatible encoder cable to the matching numbered encoder port. Encoders are optional for this open-loop spin test; a constant count without an encoder connection does not diagnose a motor failure.

Secure loose motors so their bodies cannot roll or twist. Support an assembled drivetrain with all wheels clear. Keep fingers, hair and cables away from rotating parts; keep the robot's power switch accessible. A software power limit is not a guarantee against injury or stall current.

## Controls

- Release LEFT BUMPER after START to arm the test.
- Hold exactly one of A/B/X/Y and LEFT BUMPER to run that motor at 15% commanded power.
- Hold RIGHT BUMPER before starting a burst for negative power.
- A burst lasts at most two seconds while the control loop is running. Release LEFT BUMPER to re-arm.
- Releasing the selected button, selecting multiple buttons, or changing direction stops an active burst and requires re-arming.
- Release LEFT BUMPER for normal stop. BACK latches all outputs off until the OpMode is restarted. Driver Station STOP exits the OpMode.
- Motors default to FORWARD for identification only. Positive shaft rotation does not necessarily mean forward chassis motion.

The timeout depends on the running software loop, not an independent hardware watchdog. Driver Station STOP and the physical power switch remain essential. At 15% a loaded motor might not move: release promptly, inspect the mechanism/wiring, and review with the lead instead of increasing power blindly.

## Monday review

The student should be able to explain `hardwareMap`, `DcMotor`, `@TeleOp`, `waitForStart`, `opModeIsActive`, `setPower`, motor direction, `RUN_WITHOUT_ENCODER`, and the stop/re-arm state variables. RUN_WITHOUT_ENCODER means no encoder-based speed regulation; connected encoder positions can still be read.

Build successfully in the real FTC project and record SDK/app versions. Test button behavior with a mentor before permitting wheel contact with the floor. Do not mark Tuesday's checklist passed in advance.

## Tuesday acceptance checklist

Record each result in TEST_LOG.csv. Pass only when observed.

1. INIT and START with no input: all motors stationary.
2. START with left bumper held: no motion until bumper is released and re-pressed with one selection.
3. Test A, B, X, Y separately: correct physical motor, all other motors stopped.
4. Release left bumper mid-burst: commanded output goes to zero.
5. Hold for longer than two seconds: output becomes zero and stays zero until re-armed.
6. Select two buttons or change direction during a burst: output stops and requires re-arm.
7. Repeat each motor in reverse. Record positive direction and encoder count change if connected.
8. Press BACK during a burst: all output stops; later button presses cannot restart it in that run.
9. Test Driver Station STOP. Confirm all motors stop.
10. Correct mapping and directions in a reviewed commit. Only then add drivetrain mixing and sensor-based control.

## Repository and team workflow

Repository: https://github.com/sanaysrivas-cyber/Morpheus

This private repository includes the full FTC SDK 12.0.0 Android project, SolversLib core 0.3.6, commissioning source, and mock tests. The owner must invite teammates before they can access it. The upstream license and setup files are retained. Follow ANDROID_SETUP.md for cloning, syncing, building, and deploying.

Use a `commissioning/four-motor-test` branch for changes, review them in a pull request, and commit measured direction changes after testing. Do not overwrite another team's or season's project.

## Official references

- https://ftc-docs.firstinspires.org/en/latest/programming_resources/tutorial_specific/android_studio/creating_op_modes/Creating-and-Running-an-Op-Mode-%28Android-Studio%29.html
- https://ftc-docs.firstinspires.org/en/latest/tech_tips/tech-tips/tech-tip-motor-modes/tech-tip-motor-modes.html

## Next stage

After commissioning: verify the actual drivetrain type, implement its motor mixing, confirm encoder polarity, measure wheel/gear conversion, initialize the actual IMU orientation, then implement and tune closed-loop control. CAD alone cannot supply working PID gains.

## Local verification completed

`python3 tests/verify.py` compiled the actual OpMode source against minimal Java SDK doubles and passed 14 behavioral scenarios: all four selections in both directions, startup interlock, burst timeout/re-arm, conflicting selections, direction change, latched stop, loop exit, partial initialization failure, and stop before the active loop. These checks do not establish FTC SDK compatibility, Android build success, electrical correctness, stopping latency, or real motor behavior.

# Morpheus drivetrain acceptance

Status: **NOT RUN on hardware**. Software builds and CAD analysis do not close these checks. Record observations in [TEST_LOG.csv](../TEST_LOG.csv), including failures and aborted trials. Use the tested commit SHA and STEP checksum/revision; never mark a planned result PASS.

## Preparation

Confirm the physical front convention in the [CAD audit](CAD_DRIVETRAIN_AUDIT.md). Confirm all four corner labels and mecanum roller slants. With power off, trace each motor cable to its actual hub/port and set its exact configuration name: `frontLeft`, `frontRight`, `backLeft`, `backRight`. Ports 0/1/2/3 respectively are a proposal only. Select the actual installed motor type. Confirm compatible RC/DS versions; build and deploy the reviewed APK through Android Studio/ADB. A successful build is not a deployment.

Secure the robot with every wheel clear, clear the rotating mechanisms, and keep the power switch accessible with a spotter. Inspect loose wires and mechanical binding before enabling power. At 15%, a loaded motor may stall; release promptly and investigate rather than increasing power. Software timeouts require a functioning loop; the physical switch remains the independent stop.

## Individual identification — Four Motor Bench Test

This OpMode uses **FORWARD direction on all four motors**, intentionally independent of drive inversions. DualSense mapping: Cross=A/FL, Circle=B/FR, Square=X/BL, Triangle=Y/BR. Select the button before or with L1, and hold L1 to enable. R1 selects negative power and must be set before the burst. Each burst is at most 15% for two seconds. Release L1 to re-arm; invalid initial selection also consumes the arm. Back/Create latches zero until restart. Verify the physical button mapping on the actual DS before testing motion.

1. INIT, then START centered: all motors remain stationary. Repeat START with L1 already held; no motion until L1 is released and pressed again.
2. Test one corner at a time with Cross/Circle/Square/Triangle + L1. Only the named wheel may move. Record physical corner, shaft/wheel direction, hub/port, and encoder start/end if connected.
3. Release L1 mid-burst; output stops. Hold over two seconds; output stops and stays stopped until L1 release. Test no selection, two selections, changing corner, and changing R1 while enabled; all must stop and require re-arm.
4. Repeat positive and negative bursts for every motor. Inspect which command would propel each wheel forward. Compare against the provisional left FORWARD/right REVERSE directions in MorpheusDrive. Correct directions in a reviewed commit; use per-corner settings if needed.
5. Back/Create during motion must latch all outputs off. Releasing it and pressing other controls must not resume motion. Restart is required. Verify DS STOP and the physical switch independently.

## Combined motion — Morpheus PS5 Mecanum Drive

The drive starts with 55% normal, 25% L2 precision, and 70% R2 turbo caps; L2 wins when both triggers are held. **Hold L2 throughout all initial combined tests.** Cross holds outputs at zero while pressed; releasing Cross allows stick motion to resume. Back/Create latches zero until the OpMode is initialized again. These are software stops, not certified safety circuits. Test both before floor use.

| Stage | Commanded cap | Required observation |
| --- | --- | --- |
| Wheels clear | 25% using L2 | Centered sticks, INIT, and START produce zero motion |
| Wheels clear | 25% using L2 | Forward and reverse: all wheels agree on intended chassis direction |
| Wheels clear | 25% using L2 | Strafe left/right: correct opposing diagonal wheel directions |
| Wheels clear | 25% using L2 | Clockwise/counterclockwise rotation: correct opposing sides |
| Wheels clear | 25% using L2 | Cross stops while held; Back/Create stays latched; DS STOP stops |
| Clear floor | 25% using L2 | Short motion, then marked 1 m straight trial; record drift/distance/stopping behavior |
| Clear floor | 25% using L2 | Short strafe and rotate trials; record scrub, drift and binding |
| Clear floor | Gradually to 55% normal | Mixed driving with small stick inputs first; record instability or delayed stopping |
| Clear floor | Up to 70% R2 | Only after lower-power tests pass; test stability and stopping distance |
| Future reviewed change | 100% | Disabled in this branch; raise only after prior acceptance and a suitable test area |

For pure forward (+Z), all wheel angular velocities should be +X in the CAD frame. For a right strafe (−X in that frame), FL/BR should have forward wheel action and FR/BL reverse. For clockwise yaw viewed from above, left wheels should have forward action and right wheels reverse. Confirm these physical observations, rather than judging only telemetry signs.

Abort on wrong identity/direction, unexpected motion, binding, heating, cable contact, loss of communications, tip risk, or ineffective stopping. Use DS STOP or switch, record FAIL/ABORTED with conditions, correct the cause, and repeat the affected lower stage before continuing. No fixed drift tolerance or stopping-distance claim is established yet; record measurements and agree operating tolerances before accepting performance.

## Log fields

Record date, tester, tested commit, CAD revision/checksum, battery voltage, surface, SDK and RC/DS versions, actual motor model, hub/port, configured name, motion/test, commanded limit, expected and observed behavior, encoder start/end where relevant, PASS/FAIL/ABORTED, notes, and next action. Leave unmeasured fields blank, rather than inventing values.

After acceptance: verify IMU mounting/heading independently, then consider field-centric control, heading hold, localization, and closed-loop trajectories. This TeleOp is robot-centric and raw-power only.

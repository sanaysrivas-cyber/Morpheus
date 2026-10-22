# Morpheus engineering log

## 2026-10-22 — SolversLib PS5 integration

Starting revision: `c9a24af93514cc6a27fa56c0eb7bdf4c22a49692` on main. Work branch: `solverslib/morpheus-drive`.

### Architecture and decisions

- Retain FTC SDK 12.0.0, SolversLib core 0.3.6, AGP 8.13.2, Gradle 9.1.0, and JDK 17. Avoid unrelated stack changes.
- Use SolversLib MecanumDrive for robot-centric kinematics. Explicit constructor order is FL, FR, BL, BR. Set auto inversion false and encode provisional motor directions once. The published 0.3.6 source was inspected, and the real Android build checks API compatibility.
- Use raw power, FTC RUN_WITHOUT_ENCODER, and BRAKE on every drive motor. No IMU or field-centric dependency yet.
- Preserve 25% precision, 55% normal, 70% commissioning turbo; precision wins. Match the trigger threshold to SDK float inputs so exactly 0.20 does not exceed it. Cross is a hold stop; Back/Create is a latched software stop. Neither replaces the physical switch.
- Keep the 15%, two-second individual-motor test separate. It intentionally uses FORWARD on every motor to expose raw wiring/direction observations.
- Remove obsolete root FourMotor.java and the stale linear test harness. Replace self-modifying bootstrap CI with tests, an Android build, and artifact upload under read-only repository permissions.
- Handle partial initialization failure by commanding all acquired motors to zero; stop() also works before initialization completes.

### Defects and fixes

The existing tests called runOpMode(), but the production bench class had become iterative OpMode. The new harness calls init(), init_loop(), start(), repeated loop(), and stop() with a deterministic elapsed-time double. It checks outputs on every frame.

The bench arm could remain available after L1 was pressed with no selection or multiple selections; changing the selection while continuing to hold L1 could then begin a burst. The revised code consumes the arm on the first enabled frame. A valid selection starts a burst; an invalid selection requires releasing L1 again. Timeout, changed corner, changed reverse, button release, and conflicting buttons also require re-arm.

The first remote CI run failed in Android setup before tests/build: setup-android v3 defaulted to the retired SDK package `tools`. The workflow now requests only `platform-tools`, then installs the explicit platform/build-tools packages in the following step. Java tests and the robot implementation are unchanged. Remote CI verifies this runner-specific repair.

### CAD findings and limits

The read-only STEP audit composes actual placement transforms with inch/mm normalization. It finds an X roller arrangement, four nominal 96 mm wheels, four motors labeled 435 RPM, mirrored miter gear trains, longitudinal front motors and vertical rear motors. The conditional mechanical prediction agrees with provisional left FORWARD/right REVERSE. Actual electrical command direction remains unproven. The front convention is chosen from the intake ramp and must match physical team labeling. See the full [audit](CAD_DRIVETRAIN_AUDIT.md).

### Validation, failures, and publication

Both Java behavioral suites pass; the real Android Gradle build and APK inspection are recorded in [SOFTWARE_VALIDATION.md](SOFTWARE_VALIDATION.md). The initial stale harness was replaced based on lifecycle inspection. A later sandboxed Gradle attempt failed before build startup because its local coordination socket was prohibited; the permitted rerun outside that restriction is the relevant build result.

Initial publishing attempts were blocked: the GitHub connector rejected branch creation with `403 Resource not accessible by integration`, and local Git had no stored credentials. The owner then authenticated GitHub CLI and configured its Git credential helper. The feature branch was successfully pushed through authenticated Git. Local commits and recovery exports remain available. Review and remote CI are tracked on the GitHub pull request; no merge is authorized.

No robot deployment or physical test occurred. CAD cannot prove wiring, electrical or encoder polarity, traction, stopping latency, stability, or installed part correspondence. All hardware checks remain open.

### Costs and next build tasks

No hardware purchased and no paid service provisioned. Existing Android Studio/SDK used; temporary JDK 17, Gradle, and library dependencies downloaded for local verification. Network transfer/storage were used; their monetary cost was not measured.

1. Review the published integration PR and its remote CI result; do not merge automatically.
2. Have the team review the front convention, mechanical inference, and provisional motor directions.
3. Deploy the reviewed APK and complete the individual motor and combined-motion acceptance stages. Record observations, battery/surface, failures, encoder deltas, and costs in TEST_LOG.csv.
4. Commit measured per-corner mapping/direction corrections. Establish performance tolerances from real trials.
5. Only after drivetrain acceptance: IMU orientation checks, field-centric control, heading hold, localization, and closed-loop trajectories.

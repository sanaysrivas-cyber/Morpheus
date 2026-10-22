package org.firstinspires.ftc.teamcode;

import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.seattlesolvers.solverslib.drivebase.MecanumDrive;
import com.seattlesolvers.solverslib.hardware.motors.Motor;

@TeleOp(name = "Morpheus: PS5 Mecanum Drive", group = "Drive")
public class MorpheusDrive extends OpMode {
    private static final double PRECISION_SPEED = 0.25;
    private static final double NORMAL_SPEED = 0.55;
    // Raise only after the documented hardware acceptance sequence passes.
    private static final double TURBO_SPEED = 0.70;
    private static final float TRIGGER_THRESHOLD = 0.20f;
    private static final double STICK_DEADBAND = 0.05;

    // Provisional electrical directions; CAD does not establish motor polarity.
    // See docs/CAD_DRIVETRAIN_AUDIT.md and commission each corner before driving.
    private static final boolean INVERT_LEFT_SIDE = false;
    private static final boolean INVERT_RIGHT_SIDE = true;

    private Motor frontLeft, frontRight, backLeft, backRight;
    private MecanumDrive drive;
    private boolean emergencyStop;

    @Override
    public void init() {
        try {
            frontLeft = new Motor(hardwareMap, "frontLeft");
            configureMotor(frontLeft, INVERT_LEFT_SIDE);
            frontRight = new Motor(hardwareMap, "frontRight");
            configureMotor(frontRight, INVERT_RIGHT_SIDE);
            backLeft = new Motor(hardwareMap, "backLeft");
            configureMotor(backLeft, INVERT_LEFT_SIDE);
            backRight = new Motor(hardwareMap, "backRight");
            configureMotor(backRight, INVERT_RIGHT_SIDE);

            // Disable the library's right-side multiplier: directions are explicit above.
            drive = new MecanumDrive(false, frontLeft, frontRight, backLeft, backRight);
            drive.setMaxSpeed(NORMAL_SPEED);
            emergencyStop = false;
            drive.stop();
        } catch (RuntimeException failure) {
            stop();
            throw failure;
        }
        telemetry.addLine("Morpheus: robot-centric PS5 drive; verify directions on blocks first.");
        telemetry.addLine("Left stick=translate; right stick X=turn; L2=25%; R2=70%; normal=55%.");
        telemetry.addLine("Cross=hold stop; Back/Create=latched stop until OpMode restart.");
        telemetry.update();
    }

    @Override
    public void loop() {
        if (gamepad1.back) emergencyStop = true;
        double strafe = applyDeadband(gamepad1.left_stick_x);
        double forward = applyDeadband(-gamepad1.left_stick_y);
        double turn = applyDeadband(gamepad1.right_stick_x);

        // Precision wins when both triggers are held.
        double speedLimit = gamepad1.left_trigger > TRIGGER_THRESHOLD ? PRECISION_SPEED
                : gamepad1.right_trigger > TRIGGER_THRESHOLD ? TURBO_SPEED : NORMAL_SPEED;
        drive.setMaxSpeed(speedLimit);
        if (emergencyStop || gamepad1.a) {
            drive.stop();
        } else {
            // SolversLib squares the rescaled inputs for finer control near center.
            drive.driveRobotCentric(strafe, forward, turn, true);
        }
        telemetry.addData("State", emergencyStop ? "STOP LATCHED - restart OpMode"
                : gamepad1.a ? "STOP HELD" : "DRIVING");
        telemetry.addData("Speed limit", "%.0f%%", speedLimit * 100.0);
        telemetry.addData("Forward", "%.2f", forward);
        telemetry.addData("Strafe", "%.2f", strafe);
        telemetry.addData("Turn", "%.2f", turn);
        telemetry.update();
    }

    @Override
    public void stop() {
        // Works even if initialization failed before the drive object was created.
        for (Motor motor : new Motor[]{frontLeft, frontRight, backLeft, backRight}) {
            if (motor != null) motor.stopMotor();
        }
    }

    private static void configureMotor(Motor motor, boolean inverted) {
        motor.stopMotor();
        motor.motor.setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
        motor.setRunMode(Motor.RunMode.RawPower);
        motor.setZeroPowerBehavior(Motor.ZeroPowerBehavior.BRAKE);
        motor.setInverted(inverted);
    }

    private static double applyDeadband(double value) {
        double magnitude = Math.abs(value);
        if (magnitude <= STICK_DEADBAND) return 0.0;
        return Math.copySign((magnitude - STICK_DEADBAND) / (1.0 - STICK_DEADBAND), value);
    }
}

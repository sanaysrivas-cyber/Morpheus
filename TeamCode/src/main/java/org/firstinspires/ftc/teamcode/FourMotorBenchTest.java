package org.firstinspires.ftc.teamcode;

import com.qualcomm.robotcore.eventloop.opmode.LinearOpMode;
import com.qualcomm.robotcore.eventloop.opmode.TeleOp;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorSimple;

@TeleOp(name = "Morpheus: Four Motor Bench Test", group = "Commissioning")
public class FourMotorBenchTest extends LinearOpMode {
    private static final double TEST_POWER = 0.15;
    private static final double MAX_BURST_SECONDS = 2.0;
    private static final String[] NAMES = {
        "frontLeft", "frontRight", "backLeft", "backRight"
    };
    private final DcMotor[] motors = new DcMotor[4];

    @Override
    public void runOpMode() throws InterruptedException {
        try {
            for (int i = 0; i < motors.length; i++) {
                motors[i] = hardwareMap.get(DcMotor.class, NAMES[i]);
                motors[i].setPower(0);
                motors[i].setDirection(DcMotorSimple.Direction.FORWARD);
                motors[i].setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
                motors[i].setMode(DcMotor.RunMode.RUN_WITHOUT_ENCODER);
            }

            telemetry.addLine("Secure motors; lift wheels clear; keep switch accessible.");
            telemetry.addLine("Release LEFT BUMPER before starting.");
            telemetry.addLine("Hold LEFT BUMPER + A/B/X/Y for one motor.");
            telemetry.addLine("Hold RIGHT BUMPER too for reverse. BACK latches stop.");
            telemetry.update();
            waitForStart();
            if (isStopRequested()) return;

            boolean ready = false;
            boolean emergencyStop = false;
            boolean burstActive = false;
            int activeMotor = -1;
            boolean activeReverse = false;
            double burstStart = 0;

            while (opModeIsActive()) {
                if (gamepad1.back) emergencyStop = true;
                boolean enable = gamepad1.left_bumper;
                boolean reverse = gamepad1.right_bumper;
                boolean[] selected = {gamepad1.a, gamepad1.b, gamepad1.x, gamepad1.y};
                int count = 0;
                int requestedMotor = -1;
                for (int i = 0; i < selected.length; i++) {
                    if (selected[i]) { count++; requestedMotor = i; }
                }

                if (!enable) {
                    ready = true;
                    burstActive = false;
                } else if (!emergencyStop) {
                    if (ready && count == 1) {
                        ready = false;
                        burstActive = true;
                        activeMotor = requestedMotor;
                        activeReverse = reverse;
                        burstStart = getRuntime();
                    }
                    if (burstActive && (count != 1 || requestedMotor != activeMotor
                            || reverse != activeReverse
                            || getRuntime() - burstStart >= MAX_BURST_SECONDS)) {
                        burstActive = false;
                    }
                }

                boolean running = enable && burstActive && !emergencyStop;
                double command = running ? (activeReverse ? -TEST_POWER : TEST_POWER) : 0;
                for (int i = 0; i < motors.length; i++) {
                    motors[i].setPower(running && i == activeMotor ? command : 0);
                    telemetry.addData(NAMES[i], "power %.2f | encoder %d",
                            motors[i].getPower(), motors[i].getCurrentPosition());
                }
                telemetry.addData("State", emergencyStop ? "STOP LATCHED: restart OpMode"
                        : running ? "RUNNING: release left bumper to stop"
                        : ready ? "READY: select ONE motor + left bumper"
                        : "Release left bumper to re-arm");
                telemetry.addLine("A=frontLeft B=frontRight X=backLeft Y=backRight");
                telemetry.addLine("Right bumper=reverse; BACK=latched stop; DS STOP=exit");
                telemetry.update();
                idle();
            }
        } finally {
            for (DcMotor motor : motors) {
                if (motor != null) motor.setPower(0);
            }
        }
    }
}

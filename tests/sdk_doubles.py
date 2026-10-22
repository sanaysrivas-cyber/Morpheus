"""Behavioral checks compile production Java with small SDK/library doubles.

These are controller/lifecycle tests, not Android compatibility or robot physics.
The real Gradle build separately checks the published FTC/SolversLib APIs.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STUBS = {
    'com/qualcomm/robotcore/hardware/DcMotorSimple.java': '''package com.qualcomm.robotcore.hardware;
public interface DcMotorSimple { enum Direction { FORWARD, REVERSE } }''',
    'com/qualcomm/robotcore/hardware/DcMotor.java': '''package com.qualcomm.robotcore.hardware;
public class DcMotor implements DcMotorSimple {
 public enum ZeroPowerBehavior { BRAKE, FLOAT }
 public enum RunMode { RUN_WITHOUT_ENCODER, RUN_USING_ENCODER }
 public Direction direction=Direction.REVERSE;
 public ZeroPowerBehavior zero=ZeroPowerBehavior.FLOAT;
 public RunMode mode=RunMode.RUN_USING_ENCODER;
 private double power=.9;
 public void setPower(double p) { if(!Double.isFinite(p)||Math.abs(p)>1) throw new AssertionError("power range"); power=p; }
 public double getPower(){return power;}
 public int getCurrentPosition(){return 0;}
 public void setDirection(Direction d){direction=d;}
 public void setZeroPowerBehavior(ZeroPowerBehavior b){zero=b;}
 public void setMode(RunMode r){mode=r;}
}''',
    'com/qualcomm/robotcore/hardware/HardwareMap.java': '''package com.qualcomm.robotcore.hardware;
import java.util.*;
public class HardwareMap {
 public final Map<String,DcMotor> devices=new LinkedHashMap<>();
 public String failName="";
 public HardwareMap(){for(String n:new String[]{"frontLeft","frontRight","backLeft","backRight"}) devices.put(n,new DcMotor());}
 public <T> T get(Class<T> c,String name){
  if(name.equals(failName)||!devices.containsKey(name)) throw new IllegalArgumentException("missing motor "+name);
  return c.cast(devices.get(name));
 }
}''',
    'com/qualcomm/robotcore/hardware/Gamepad.java': '''package com.qualcomm.robotcore.hardware;
public class Gamepad {
 public boolean a,b,x,y,left_bumper,right_bumper,back;
 public float left_stick_x,left_stick_y,right_stick_x,left_trigger,right_trigger;
}''',
    'com/qualcomm/robotcore/eventloop/opmode/TeleOp.java': '''package com.qualcomm.robotcore.eventloop.opmode;
public @interface TeleOp { String name(); String group(); }''',
    'com/qualcomm/robotcore/eventloop/opmode/OpMode.java': '''package com.qualcomm.robotcore.eventloop.opmode;
import com.qualcomm.robotcore.hardware.*;
public abstract class OpMode {
 public HardwareMap hardwareMap=new HardwareMap();
 public Gamepad gamepad1=new Gamepad(); public Telemetry telemetry=new Telemetry();
 public abstract void init(); public void init_loop(){} public void start(){}
 public abstract void loop(); public void stop(){}
 public static class Telemetry {
  public void addLine(String s){} public void addData(String s,Object o){}
  public void addData(String s,String f,Object... o){} public void update(){}
 }
}''',
    'com/qualcomm/robotcore/util/ElapsedTime.java': '''package com.qualcomm.robotcore.util;
public class ElapsedTime {
 public static double now; private double start;
 public void reset(){start=now;} public double seconds(){return now-start;}
}''',
    'com/seattlesolvers/solverslib/hardware/motors/Motor.java': '''package com.seattlesolvers.solverslib.hardware.motors;
import com.qualcomm.robotcore.hardware.*;
public class Motor {
 public enum RunMode { RawPower }
 public enum ZeroPowerBehavior { BRAKE }
 public final DcMotor motor; public final String name; public RunMode mode;
 public Motor(HardwareMap map,String id){motor=map.get(DcMotor.class,id);name=id;}
 public Motor setRunMode(RunMode r){mode=r;return this;}
 public Motor setZeroPowerBehavior(ZeroPowerBehavior b){motor.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);return this;}
 public Motor setInverted(boolean b){motor.setDirection(b?DcMotor.Direction.REVERSE:DcMotor.Direction.FORWARD);return this;}
 public void stopMotor(){motor.setPower(0);}
}''',
    'com/seattlesolvers/solverslib/drivebase/MecanumDrive.java': '''package com.seattlesolvers.solverslib.drivebase;
import com.seattlesolvers.solverslib.hardware.motors.Motor;
public class MecanumDrive {
 public static MecanumDrive last; public final Motor[] motors; public final boolean autoInvert;
 public double max,strafe,forward,turn; public boolean squared; public int calls,stops;
 public MecanumDrive(boolean auto,Motor fl,Motor fr,Motor bl,Motor br){autoInvert=auto;motors=new Motor[]{fl,fr,bl,br};last=this;}
 public void setMaxSpeed(double s){max=s;}
 public void driveRobotCentric(double s,double f,double t,boolean q){
  strafe=s;forward=f;turn=t;squared=q;calls++;
  // A nonzero sentinel makes lifecycle stop tests meaningful; no kinematics simulated.
  for(Motor m:motors)m.motor.setPower(.123);
 }
 public void stop(){stops++;for(Motor m:motors)m.stopMotor();}
}''',
}


def run(class_name, harness):
    with tempfile.TemporaryDirectory(prefix='morpheus-test-') as tmp:
        folder = Path(tmp)
        for name, content in {**STUBS, 'Harness.java': harness}.items():
            path = folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        sources = [str(p) for p in folder.rglob('*.java')]
        sources.append(str(ROOT / 'TeamCode/src/main/java/org/firstinspires/ftc/teamcode' / (class_name + '.java')))
        subprocess.run(['javac', '--release', '8', '-d', str(folder / 'classes'), *sources], check=True)
        subprocess.run(['java', '-cp', str(folder / 'classes'), 'Harness'], check=True)

"""Assert our PS5-to-SolversLib calls, configuration, and stopping lifecycle."""
from sdk_doubles import run

run('MorpheusDrive', '''
import org.firstinspires.ftc.teamcode.MorpheusDrive;
import com.qualcomm.robotcore.hardware.*;
import com.seattlesolvers.solverslib.hardware.motors.Motor;
import com.seattlesolvers.solverslib.drivebase.MecanumDrive;
public class Harness {
 static int checks=0;
 static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
 static void near(double a,double b){check(Math.abs(a-b)<1e-6,"expected "+b+" got "+a);}
 static void zero(MorpheusDrive op){for(DcMotor m:op.hardwareMap.devices.values())near(m.getPower(),0);}
 public static void main(String[] ignored){
  MorpheusDrive op=new MorpheusDrive();op.stop();op.init();MecanumDrive d=MecanumDrive.last;zero(op);
  check(!d.autoInvert,"disable duplicate library inversion");near(d.max,.55);
  String[] names={"frontLeft","frontRight","backLeft","backRight"};
  for(int i=0;i<4;i++){
   Motor m=d.motors[i];check(m.name.equals(names[i]),"constructor corner order");
   check(m.mode==Motor.RunMode.RawPower,"raw power");
   check(m.motor.mode==DcMotor.RunMode.RUN_WITHOUT_ENCODER,"FTC run mode");
   check(m.motor.zero==DcMotor.ZeroPowerBehavior.BRAKE,"brake");
   check(m.motor.direction==(i%2==1?DcMotorSimple.Direction.REVERSE:DcMotorSimple.Direction.FORWARD),"provisional direction");
  }
  op.init_loop();zero(op);op.start();zero(op);op.loop();near(d.strafe,0);near(d.forward,0);near(d.turn,0);
  check(d.squared,"library squares inputs");
  for(float small:new float[]{0,.01f,-.01f,.049f,-.049f,.05f,-.05f}){
   op.gamepad1.left_stick_x=small;op.gamepad1.left_stick_y=small;op.gamepad1.right_stick_x=small;
   op.loop();near(d.strafe,0);near(d.forward,0);near(d.turn,0);
  }
  op.gamepad1.left_stick_x=.525f;op.gamepad1.left_stick_y=-1;op.gamepad1.right_stick_x=-.525f;
  op.loop();near(d.strafe,.5);near(d.forward,1);near(d.turn,-.5);
  op.gamepad1.left_stick_x=-1;op.gamepad1.left_stick_y=1;op.gamepad1.right_stick_x=1;
  op.loop();near(d.strafe,-1);near(d.forward,-1);near(d.turn,1);
  op.gamepad1.right_trigger=.19f;op.loop();near(d.max,.55);
  op.gamepad1.right_trigger=.20f;op.loop();near(d.max,.55);
  op.gamepad1.right_trigger=.21f;op.loop();near(d.max,.70);
  op.gamepad1.left_trigger=.20f;op.loop();near(d.max,.70);
  op.gamepad1.left_trigger=.21f;op.loop();near(d.max,.25);
  op.gamepad1.right_trigger=0;op.loop();near(d.max,.25);
  op.gamepad1.left_trigger=0;op.loop();near(d.max,.55);
  int calls=d.calls;op.gamepad1.a=true;op.loop();zero(op);check(d.calls==calls,"Cross suppresses drive");
  op.gamepad1.a=false;op.loop();check(d.calls==calls+1,"release resumes drive");
  op.gamepad1.back=true;op.loop();zero(op);calls=d.calls;
  op.gamepad1.back=false;op.gamepad1.a=true;op.loop();zero(op);
  op.gamepad1.a=false;op.gamepad1.right_trigger=1;op.loop();zero(op);
  check(d.calls==calls,"Back remains latched");
  op.stop();zero(op);op.init();op.start();op.loop();check(MecanumDrive.last.calls==1,"new init clears latch");
  op.stop();zero(op);
  for(String failed:names){
   MorpheusDrive broken=new MorpheusDrive();broken.hardwareMap.failName=failed;
   try{broken.init();throw new AssertionError("expected init failure");}catch(IllegalArgumentException expected){}
   for(java.util.Map.Entry<String,DcMotor> e:broken.hardwareMap.devices.entrySet()){
    if(e.getKey().equals(failed))break;
    near(e.getValue().getPower(),0);
   }broken.stop();
  }
  System.out.println("PASS drive: "+checks+" assertions (library call spy; no kinematics/hardware).");
 }
}''')

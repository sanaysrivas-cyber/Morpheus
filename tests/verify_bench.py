"""Exercise the real iterative commissioning OpMode with deterministic time."""
from sdk_doubles import run

run('FourMotorBenchTest', '''
import org.firstinspires.ftc.teamcode.FourMotorBenchTest;
import com.qualcomm.robotcore.hardware.*;
import com.qualcomm.robotcore.util.ElapsedTime;
public class Harness {
 static int scenarios=0,frames=0;
 static void outputs(FourMotorBenchTest op,int active,double power){
  int i=0;for(DcMotor m:op.hardwareMap.devices.values()){
   double expected=i++==active?power:0;
   if(Math.abs(m.getPower()-expected)>1e-9)throw new AssertionError("frame "+frames+" motor "+i);
   if(Math.abs(m.getPower())>.15)throw new AssertionError("commissioning power cap");
  }
 }
 // selection (-1=none, 4=A+B), enable, reverse, back, time, expected motor, power
 static void scenario(double[][] script){
  ElapsedTime.now=10;FourMotorBenchTest op=new FourMotorBenchTest();op.init();outputs(op,-1,0);
  for(DcMotor m:op.hardwareMap.devices.values())
   if(m.direction!=DcMotorSimple.Direction.FORWARD||m.zero!=DcMotor.ZeroPowerBehavior.BRAKE
     ||m.mode!=DcMotor.RunMode.RUN_WITHOUT_ENCODER)throw new AssertionError("motor configuration");
  op.init_loop();outputs(op,-1,0);op.start();outputs(op,-1,0);
  for(double[] f:script){
   int s=(int)f[0];op.gamepad1.a=s==0||s==4;op.gamepad1.b=s==1||s==4;
   op.gamepad1.x=s==2;op.gamepad1.y=s==3;op.gamepad1.left_bumper=f[1]==1;
   op.gamepad1.right_bumper=f[2]==1;op.gamepad1.back=f[3]==1;
   ElapsedTime.now=10+f[4];op.loop();frames++;outputs(op,(int)f[5],f[6]);
  }
  op.stop();outputs(op,-1,0);scenarios++;
 }
 public static void main(String[] ignored){
  for(int m=0;m<4;m++)for(int r=0;r<2;r++){
   double p=r==1?-.15:.15;
   scenario(new double[][]{{m,1,r,0,0,-1,0},{m,0,r,0,.1,-1,0},
    {m,1,r,0,1,m,p},{m,1,r,0,2.999,m,p},{m,1,r,0,3,-1,0},
    {m,1,r,0,4,-1,0},{m,0,r,0,4.1,-1,0},{m,1,r,0,4.2,m,p}});
  }
  for(int interruption=0;interruption<4;interruption++){
   int s=interruption==0?4:interruption==1?1:interruption==2?-1:0;
   int r=interruption==3?1:0;
   scenario(new double[][]{{-1,0,0,0,0,-1,0},{0,1,0,0,.1,0,.15},
    {s,1,r,0,.2,-1,0},{0,1,0,0,.3,-1,0},{0,0,0,0,.4,-1,0},{0,1,0,0,.5,0,.15}});
  }
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{0,1,0,0,.1,0,.15},
   {0,0,0,0,.2,-1,0},{0,1,0,0,.3,0,.15}});
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{0,1,0,0,.1,0,.15},
   {0,1,0,1,.2,-1,0},{0,0,0,0,.3,-1,0},{0,1,0,0,.4,-1,0}});
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{-1,1,0,0,.1,-1,0},{0,1,0,0,.2,-1,0}});
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{4,1,0,0,.1,-1,0},{0,1,0,0,.2,-1,0}});
  scenario(new double[][]{{-1,0,0,1,0,-1,0},{0,1,0,0,.1,-1,0}});
  for(String failed:new String[]{"frontLeft","frontRight","backLeft","backRight"}){
   FourMotorBenchTest op=new FourMotorBenchTest();op.hardwareMap.failName=failed;
   try{op.init();throw new AssertionError("expected init failure");}catch(IllegalArgumentException expected){}
   for(java.util.Map.Entry<String,DcMotor> e:op.hardwareMap.devices.entrySet()){
    if(e.getKey().equals(failed))break;
    if(e.getValue().getPower()!=0)throw new AssertionError("partial init stop");
   }op.stop();scenarios++;
  }
  new FourMotorBenchTest().stop();
  System.out.println("PASS bench: "+scenarios+" scenarios, "+frames+" frames (SDK doubles; no hardware).");
 }
}''')

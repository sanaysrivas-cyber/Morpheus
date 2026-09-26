"""Compile and execute the real OpMode with minimal SDK doubles, not the FTC SDK.
Requires Java 17+. Does not verify Android packaging, hardware, or FTC API compatibility.
"""
from pathlib import Path
import subprocess, tempfile
root = Path(__file__).resolve().parents[1]
stubs = {
'com/qualcomm/robotcore/hardware/DcMotorSimple.java': '''package com.qualcomm.robotcore.hardware;
public interface DcMotorSimple { enum Direction { FORWARD, REVERSE } }''',
'com/qualcomm/robotcore/hardware/DcMotor.java': '''package com.qualcomm.robotcore.hardware;
public class DcMotor implements DcMotorSimple {
 public enum ZeroPowerBehavior { BRAKE }
 public enum RunMode { RUN_WITHOUT_ENCODER }
 private double power;
 public void setPower(double p) { if(Math.abs(p)>0.15) throw new AssertionError("power limit"); power=p; }
 public double getPower(){return power;}
 public int getCurrentPosition(){return 0;}
 public void setDirection(Direction d){}
 public void setZeroPowerBehavior(ZeroPowerBehavior b){}
 public void setMode(RunMode r){}
}''',
'com/qualcomm/robotcore/hardware/HardwareMap.java': '''package com.qualcomm.robotcore.hardware;
import java.util.*;
public class HardwareMap {
 public Map<String,DcMotor> devices=new LinkedHashMap<>();
 public String failName="";
 public <T> T get(Class<T> c,String name){
  if(name.equals(failName)) throw new IllegalArgumentException("missing motor");
  DcMotor m=new DcMotor();devices.put(name,m);return c.cast(m);
 }
}''',
'com/qualcomm/robotcore/hardware/Gamepad.java': '''package com.qualcomm.robotcore.hardware;
public class Gamepad { public boolean a,b,x,y,left_bumper,right_bumper,back; }''',
'com/qualcomm/robotcore/eventloop/opmode/TeleOp.java': '''package com.qualcomm.robotcore.eventloop.opmode;
public @interface TeleOp { String name(); String group(); }''',
'com/qualcomm/robotcore/eventloop/opmode/LinearOpMode.java': '''package com.qualcomm.robotcore.eventloop.opmode;
import com.qualcomm.robotcore.hardware.*;
public abstract class LinearOpMode {
 public HardwareMap hardwareMap=new HardwareMap();
 public Gamepad gamepad1=new Gamepad(); public Telemetry telemetry=new Telemetry();
 public Runnable beforeLoop=()->{}; public Runnable afterLoop=()->{};
 public int loops=0,maxLoops=0; public double time=0;
 public boolean stopRequested=false;
 public abstract void runOpMode() throws InterruptedException;
 public void waitForStart(){}
 public boolean isStopRequested(){return stopRequested;}
 public boolean opModeIsActive(){if(loops>=maxLoops)return false;beforeLoop.run();return true;}
 public double getRuntime(){return time;}
 public void idle(){afterLoop.run();loops++;}
 public static class Telemetry {
  public void addLine(String s){} public void addData(String s,Object o){}
  public void addData(String s,String f,Object... o){} public void update(){}
 }
}''',
'Harness.java': '''import org.firstinspires.ftc.teamcode.FourMotorBenchTest;
import com.qualcomm.robotcore.hardware.*;
public class Harness {
 static int cases=0;
 // motor index, enable, reverse, back, elapsed time, expected active index, expected power
 static void scenario(double[][] frames) throws Exception {
  FourMotorBenchTest op=new FourMotorBenchTest();op.maxLoops=frames.length;
  op.beforeLoop=()->{
   double[] f=frames[op.loops];int selected=(int)f[0];
   op.gamepad1.a=selected==0||selected==4; op.gamepad1.b=selected==1||selected==4;
   op.gamepad1.x=selected==2;op.gamepad1.y=selected==3;
   op.gamepad1.left_bumper=f[1]==1;op.gamepad1.right_bumper=f[2]==1;
   op.gamepad1.back=f[3]==1;op.time=f[4];
  };
  op.afterLoop=()->{
   double[] f=frames[op.loops];int i=0;
   for(DcMotor m:op.hardwareMap.devices.values()){
    double expected=i++==(int)f[5]?f[6]:0;
    if(Math.abs(m.getPower()-expected)>1e-9)throw new AssertionError("frame "+op.loops);
   }
  };
  op.runOpMode();for(DcMotor m:op.hardwareMap.devices.values())
   if(m.getPower()!=0)throw new AssertionError("exit stop");cases++;
 }
 public static void main(String[] args)throws Exception{
  for(int m=0;m<4;m++)for(int r=0;r<2;r++){
   double p=r==1?-.15:.15;
   scenario(new double[][]{{m,1,r,0,0,-1,0},{m,0,r,0,.1,-1,0},
    {m,1,r,0,.2,m,p},{m,1,r,0,2.3,-1,0},{m,1,r,0,2.4,-1,0},
    {m,0,r,0,2.5,-1,0},{m,1,r,0,2.6,m,p},{m,0,r,0,2.7,-1,0}});
  }
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{0,1,0,0,.1,0,.15},
   {4,1,0,0,.2,-1,0},{0,1,0,0,.3,-1,0}});
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{0,1,0,0,.1,0,.15},
   {0,1,1,0,.2,-1,0},{0,1,0,0,.3,-1,0}});
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{0,1,0,0,.1,0,.15},
   {0,1,0,1,.2,-1,0},{0,0,0,0,.3,-1,0},{0,1,0,0,.4,-1,0}});
  scenario(new double[][]{{-1,0,0,0,0,-1,0},{2,1,0,0,.1,2,.15}});
  FourMotorBenchTest initFail=new FourMotorBenchTest();initFail.hardwareMap.failName="backLeft";
  try{initFail.runOpMode();throw new AssertionError("expected failure");}
  catch(IllegalArgumentException expected){}
  for(DcMotor m:initFail.hardwareMap.devices.values())if(m.getPower()!=0)throw new AssertionError("init stop");cases++;
  FourMotorBenchTest preStop=new FourMotorBenchTest();preStop.stopRequested=true;preStop.runOpMode();
  for(DcMotor m:preStop.hardwareMap.devices.values())if(m.getPower()!=0)throw new AssertionError("prestart stop");cases++;
  System.out.println("PASS: "+cases+" mock scenarios. Not an FTC SDK build or hardware test.");
 }
}'''
}
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 for name,content in stubs.items():
  f=p/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(content)
 sources=[str(x) for x in p.rglob('*.java')]+[str(root/'TeamCode/src/main/java/org/firstinspires/ftc/teamcode/FourMotorBenchTest.java')]
 subprocess.run(['java','--module','jdk.compiler/com.sun.tools.javac.Main','-d',str(p/'classes')]+sources,check=True)
 subprocess.run(['java','-cp',str(p/'classes'),'Harness'],check=True)

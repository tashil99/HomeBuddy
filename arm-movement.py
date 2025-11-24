#!/usr/bin/env python3
#coding=utf-8
import time
from Rosmaster_Lib import Rosmaster
from ipywidgets import interact
import ipywidgets as widgets

# 创建Rosmaster对象 bot Create the Rosmaster object bot
bot = Rosmaster()

# 启动接收数据 Start receiving data
bot.create_receive_threading()

# 当前舵机ID号 ID of current steering gear
servo_id = 1

# 控制串口舵机关节运动 Control the joint movement of serial steering gear
def arm_servo(s_angle):
    bot.set_uart_servo_angle(servo_id, s_angle)

# 创建一个滑块来控制的某个串口舵机 Create a slider to control a serial actuator
if servo_id == 1:
    interact(arm_servo, s_angle=widgets.IntSlider(min=0,max=180,step=1,value=90));
elif servo_id == 2:
    interact(arm_servo, s_angle=widgets.IntSlider(min=0,max=180,step=1,value=90));
elif servo_id == 3:
    interact(arm_servo, s_angle=widgets.IntSlider(min=0,max=180,step=1,value=90));
elif servo_id == 4:
    interact(arm_servo, s_angle=widgets.IntSlider(min=0,max=180,step=1,value=90));
elif servo_id == 5:
    interact(arm_servo, s_angle=widgets.IntSlider(min=0,max=270,step=1,value=90));
elif servo_id == 6:
    interact(arm_servo, s_angle=widgets.IntSlider(min=30,max=180,step=1,value=90));


# 读取当前串口舵机的角度，读取的角度值和设置的角度值可能存在1-2度偏差。
# 读取错误返回-1
# Read the current serial steering gear Angle, read the Angle value and the set Angle value may be 1-2 degrees deviation
# Read error returns -1
read_servo = bot.get_uart_servo_angle(servo_id)
print("read angle:", servo_id, read_servo)


# 一次控制的六个串口舵机 Six serial steering gear at one time
def arm_servo(s1, s2, s3, s4, s5, s6):
    bot.set_uart_servo_angle_array([s1, s2, s3, s4, s5, s6])
    return s1, s2, s3, s4, s5, s6

# 创建六个滑块来控制串口舵机的六个关节 Create six sliders to control the six joints of the serial actuator
interact(arm_servo, \
         s1=widgets.IntSlider(min=0,max=180,step=1,value=90), \
         s2=widgets.IntSlider(min=0,max=180,step=1,value=90), \
         s3=widgets.IntSlider(min=0,max=180,step=1,value=90), \
         s4=widgets.IntSlider(min=0,max=180,step=1,value=90), \
         s5=widgets.IntSlider(min=0,max=180,step=1,value=90), \
         s6=widgets.IntSlider(min=30,max=180,step=1,value=180));

# 一次性读取六个舵机角度，读取的角度值和设置的角度值可能存在1-2度偏差。
# 读取正确返回六个舵机的角度[xx, xx, xx, xx, xx, xx]，如果某个舵机错误则那一位为-1
# Read six steering gear angles at one time, the Angle values read and set may be 1-2 degrees deviation
# Read the correct return six steering gear Angle [xx, xx, xx, xx, xx, xx, xx], if one of the steering gear is wrong, which one is -1
read_array = bot.get_uart_servo_angle_array()
print("read array:", read_array)

# 关闭扭矩力，可以用手转动舵机关节，但命令无法控制转动
# Turn off torque force, the steering gear joint can be turned by hand, but command cannot control rotation
bot.set_uart_servo_torque(False)


# 打开扭矩力，命令可以控制转动，不可以用手转动舵机关节
# Turn on torque force, command can control rotation, can not turn steering gear joint by hand
bot.set_uart_servo_torque(True)

# 程序结束后请删除对象，避免在其他程序中使用Rosmaster库造成冲突
# After the program is complete, delete the object to avoid conflicts caused by using the library in other programs
del bot


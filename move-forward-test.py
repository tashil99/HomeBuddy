#!/usr/bin/env python3
#coding=utf-8
import time
from Rosmaster_Lib import Rosmaster

def grab_object(bot):
    print("Performing grab sequence...")

    # ---- ARM CONFIG ----
    # Your arm has 6 UART servos, typical meaning:
    # s1 = base rotation
    # s2 = shoulder
    # s3 = elbow
    # s4 = wrist
    # s5 = gripper rotation OR wrist roll
    # s6 = gripper open/close  (usually 30 = fully open, 180 = fully closed)

    # === Step 1: Move arm to READY position ===
    bot.set_uart_servo_angle_array([90, 80, 100, 90, 90, 60])  # gripper open (60)
    time.sleep(0.8)

    # === Step 2: Lower arm toward object ===
    bot.set_uart_servo_angle_array([90, 120, 60, 90, 90, 60])  # lower shoulder + extend elbow
    time.sleep(0.8)

    # === Step 3: Close gripper (GRAB) ===
    bot.set_uart_servo_angle(6, 180)  # close gripper
    time.sleep(0.6)

    # === Step 4: Lift object up ===
    bot.set_uart_servo_angle_array([90, 80, 110, 90, 90, 180])
    time.sleep(0.8)

    print("Object grabbed.")

def main():
    bot = Rosmaster()
    bot.create_receive_threading()

    print("Moving forward...")
    bot.set_car_motion(0.5, 0, 0)
    time.sleep(3)

    # Stop
    bot.set_car_motion(0, 0, 0)
    print("Stopped. Starting grab sequence...")

    grab_object(bot)

    # Recommended: turn torque on after gripping
    bot.set_uart_servo_torque(True)

    # Cleanup
    del bot

if __name__ == "__main__":
    main()

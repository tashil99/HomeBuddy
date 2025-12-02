#!/usr/bin/env python3
# coding=utf-8

import time
import math
from Rosmaster_Lib import Rosmaster

# ==========================
# CONFIGURATION
# ==========================
LINEAR_SPEED = 0.3  # meters per second
ANGULAR_SPEED = 0.8  # rad/s
STOP_DELAY = 0.5  # seconds


# ==========================
# MOVEMENT FUNCTIONS
# ==========================

def stop(bot):
    bot.set_car_motion(0, 0, 0)
    time.sleep(STOP_DELAY)


def rotate_to_angle(bot, target_angle):
    """
    Rotate robot to a specific heading (radians).
    Robot rotates in place using angular velocity only.
    """
    print(f"[INFO] Rotating to {math.degrees(target_angle):.2f}°")

    direction = 1 if target_angle > 0 else -1
    bot.set_car_motion(0, 0, direction * ANGULAR_SPEED)
    time.sleep(abs(target_angle) / ANGULAR_SPEED)
    stop(bot)


def move_straight(bot, distance_m):
    """
    Move the robot forward or backward by distance_m (m).
    """
    print(f"[INFO] Moving straight {distance_m:.2f} meters")

    direction = 1 if distance_m > 0 else -1
    bot.set_car_motion(direction * LINEAR_SPEED, 0, 0)
    time_duration = abs(distance_m) / LINEAR_SPEED
    time.sleep(time_duration)
    stop(bot)


# ==========================
# GRAB MOVEMENT
# ==========================

def perform_grab_sequence(bot):

    print("[ACTION] Moving arm to INITIAL POSITION...")

    bot.set_uart_servo_angle(1, 90, 90)   # base center
    bot.set_uart_servo_angle(2, 90, 90)   # shoulder neutral
    bot.set_uart_servo_angle(3, 0, 0)  # elbow downward
    bot.set_uart_servo_angle(4, 90, 90)   # wrist neutral
    bot.set_uart_servo_angle(5, 90, 90)   # wrist rotate neutral
    bot.set_uart_servo_angle(6, 90, 90)  # gripper open

    time.sleep(1.2)

    print("[ACTION] Initial pose reached!")


# ==========================
# MAIN NAVIGATION FUNCTION
# ==========================

def go_to_point(bot, x0, y0, xt, yt):
    """
    Move robot from (x0, y0) to (xt, yt).
    """
    print("\n========== NAVIGATION ==========")
    print(f"Start: ({x0}, {y0})")
    print(f"Target: ({xt}, {yt})")

    dx = xt - x0
    dy = yt - y0

    angle_to_target = math.atan2(dy, dx)
    distance_to_target = math.sqrt(dx * dx + dy * dy)

    print(f"Angle needed: {math.degrees(angle_to_target):.2f}°")
    print(f"Distance: {distance_to_target:.2f} m\n")

    rotate_to_angle(bot, angle_to_target)
    move_straight(bot, distance_to_target)

    print("[DONE] Robot reached the target point!")

    # ---- NEW: Perform grab ----
    perform_grab_sequence(bot)


# ==========================
# RUN EXAMPLE
# ==========================

if __name__ == "__main__":
    bot = Rosmaster()

    x0, y0 = 0.0, 0.0
    xt, yt = 1.5, 1.0

    go_to_point(bot, x0, y0, xt, yt)

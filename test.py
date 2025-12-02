#!/usr/bin/env python3
# coding=utf-8

import serial
import time
import math
from Rosmaster_Lib import Rosmaster

# Voice module port
PORT = "/dev/ttyUSB2"
BAUD = 115200
TIMEOUT = 0.1

LINEAR_SPEED = 0.3    # meters/s
ANGULAR_SPEED = 0.8   # rad/s
STOP_DELAY = 0.5

def stop(bot):
    bot.set_car_motion(0, 0, 0)
    time.sleep(STOP_DELAY)

def rotate_to_angle(bot, target_angle):
    print(f"[INFO] Rotating to {math.degrees(target_angle):.2f}°")
    direction = 1 if target_angle > 0 else -1
    bot.set_car_motion(0, 0, direction * ANGULAR_SPEED)
    time.sleep(abs(target_angle) / ANGULAR_SPEED)
    stop(bot)


def move_straight(bot, distance_m):
    print(f"[INFO] Moving straight {distance_m:.2f} meters")

    direction = 1 if distance_m > 0 else -1
    bot.set_car_motion(direction * LINEAR_SPEED, 0, 0)
    time_duration = abs(distance_m) / LINEAR_SPEED
    time.sleep(time_duration)
    stop(bot)

def perform_grab_sequence(bot):

    bot.set_uart_servo_angle(1, 90, 90)   # base center
    bot.set_uart_servo_angle(2, 90, 90)   # shoulder neutral
    bot.set_uart_servo_angle(3, 0, 0)  # elbow downward
    bot.set_uart_servo_angle(4, 90, 90)   # wrist neutral
    bot.set_uart_servo_angle(5, 90, 90)   # wrist rotate neutral
    bot.set_uart_servo_angle(6, 90, 90)  # gripper open

    time.sleep(1.2)


def go_to_point(bot, x0, y0, xt, yt):
    """Move robot from (x0,y0) to (xt,yt)."""
    print("\n========== NAVIGATION ==========")
    print(f"Start: ({x0}, {y0})")
    print(f"Target: ({xt}, {yt})")

    dx = xt - x0
    dy = yt - y0

    angle_to_target = math.atan2(dy, dx)
    distance_to_target = math.sqrt(dx * dx + dy * dy)

    rotate_to_angle(bot, angle_to_target)
    move_straight(bot, distance_to_target)

    print("[DONE] Reached point!")

    # OPTIONAL: auto-grab
    perform_grab_sequence(bot)

def move_forward(bot):
    bot.set_car_motion(0.5, 0, 0)
    time.sleep(2)
    bot.set_car_motion(0, 0, 0)
    print("Action: Forward")


def move_backward(bot):
    bot.set_car_motion(-1.5, 0, 0)
    time.sleep(2)
    bot.set_car_motion(0, 0, 0)
    print("Action: Backward")


def turn_left(bot):
    bot.set_car_motion(0, 0, 1.5)
    time.sleep(1.5)
    bot.set_car_motion(0, 0, 0)
    print("Action: Left")


def turn_right(bot):
    bot.set_car_motion(0, 0, -1.5)
    time.sleep(1.5)
    bot.set_car_motion(0, 0, 0)
    print("Action: Right")


def release(bot):
    bot.set_uart_servo_angle(6, 0)
    time.sleep(0.6)
    print("Action: Released")

def send_voice_feedback(ser, code):
    try:
        ser.write(code.encode())
        print(f"Voice feedback sent: {code}")
    except:
        print("Voice feedback FAILED!")


# =====================================================
# ========== NAVIGATION POINT A/B/C/D =================
# =====================================================

# YOU MUST SET THE COORDINATES BELOW
POINT_A = (1.5, 1.0)
POINT_B = (0.5, -1.2)
POINT_C = (2.2, 0.4)
POINT_D = (-1.0, 0.0)

CURRENT_POS = [0.0, 0.0]   # (x,y) updated if needed


def go_to_point_A(bot, ser):
    print("Going to Point A...")
    send_voice_feedback(ser, "$A019#")
    go_to_point(bot, CURRENT_POS[0], CURRENT_POS[1], POINT_A[0], POINT_A[1])


def go_to_point_B(bot, ser):
    print("Going to Point B...")
    send_voice_feedback(ser, "$A020#")
    go_to_point(bot, CURRENT_POS[0], CURRENT_POS[1], POINT_B[0], POINT_B[1])


def go_to_point_C(bot, ser):
    print("Going to Point C...")
    send_voice_feedback(ser, "$A021#")
    go_to_point(bot, CURRENT_POS[0], CURRENT_POS[1], POINT_C[0], POINT_C[1])


def go_to_point_D(bot, ser):
    print("Going to Point D...")
    send_voice_feedback(ser, "$A022#")
    go_to_point(bot, CURRENT_POS[0], CURRENT_POS[1], POINT_D[0], POINT_D[1])

def return_to_origin(bot, ser):
    print("Returning to original place...")
    send_voice_feedback(ser, "$A023#")
    go_to_point(bot, 0.0, 0.0, 0.0, 0.0)

def initialize_module(ser):
    print("Initializing voice module...")
    cmds = [b'AT+ASR=ON\r\n', b'AT+CMD=1\r\n', b'AT+DEBUG=1\r\n']
    for cmd in cmds:
        ser.write(cmd)
        time.sleep(0.2)
    ser.flushInput()
    print("Voice module ready.")


def main():
    bot = Rosmaster()
    bot.create_receive_threading()
    print("Rosmaster initialized.")

    try:
        ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
        time.sleep(1)
    except Exception as e:
        print("Serial port error:", e)
        return

    initialize_module(ser)
    print("Listening for voice commands...")

    while True:
        try:
            if ser.in_waiting:
                data = ser.readline()
                if not data:
                    continue

                text = data.decode(errors="ignore").strip()
                print("Received:", text)

                tl = text.lower()

                # ===== BASIC MOVEMENT =====
                if tl == "$b000#":
                    print("Wake word detected.")

                elif tl == "$b004#":
                    move_forward(bot)

                elif tl == "$b005#":
                    move_backward(bot)

                elif tl == "$b006#":
                    turn_left(bot)

                elif tl == "$b007#":
                    turn_right(bot)

                elif tl == "stop":
                    stop(bot)

                elif tl == "$b011#":
                    perform_grab_sequence(bot)

                elif tl == "loose":
                    release(bot)

                # ===== NAVIGATION POINTS =====
                elif text == "$B019#":
                    go_to_point_A(bot, ser)

                elif text == "$B020#":
                    go_to_point_B(bot, ser)

                elif text == "$B021#":
                    go_to_point_C(bot, ser)

                elif text == "$B022#":
                    go_to_point_D(bot, ser)

                elif text == "$B023#":
                    return_to_origin(bot, ser)

        except KeyboardInterrupt:
            print("Exiting...")
            ser.close()
            break
        except Exception as e:
            print("ERR:", e)
            continue


if __name__ == "__main__":
    main()

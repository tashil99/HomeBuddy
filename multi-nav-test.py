import serial
import time
from Rosmaster_Lib import Rosmaster

# ----------------- CONFIG -----------------
PORT = "/dev/ttyUSB2"  # Yahboom voice module port
BAUD = 115200
TIMEOUT = 0.1


# -----------------------------------------

# ----------- ROBOT MOVEMENT FUNCTIONS -----------
def move_forward(home_buddy):
    home_buddy.set_car_motion(0.5, 0, 0)
    time.sleep(2)
    home_buddy.set_car_motion(0, 0, 0)
    print("Action: Moved forward")


def move_backward(home_buddy):
    home_buddy.set_car_motion(-0.5, 0, 0)
    time.sleep(2)
    home_buddy.set_car_motion(0, 0, 0)
    print("Action: Moved backward")


def turn_left(home_buddy):
    home_buddy.set_car_motion(0, 0, 0.5)
    time.sleep(1.5)
    home_buddy.set_car_motion(0, 0, 0)
    print("Action: Turned left")


def turn_right(home_buddy):
    home_buddy.set_car_motion(0, 0, -0.5)
    time.sleep(1.5)
    home_buddy.set_car_motion(0, 0, 0)
    print("Action: Turned right")


def stop(home_buddy):
    home_buddy.set_car_motion(0, 0, 0)
    print("Action: Stopped")


# def grab(home_buddy):
#     home_buddy.set_uart_servo_angle(6, 180)
#     time.sleep(0.6)
#     home_buddy.set_uart_servo_angle_array(90, 80, 110, 90, 90, 180)
#     time.sleep(0.8)
#     print("Action: Object grabbed")

def grab(home_buddy):
    print("Action: Starting grab sequence...")
    home_buddy.set_uart_servo_angle_array(0, 0, -1.57, 0, 0, 0)
    time.sleep(1.0)
    print("Action: Object grabbed and lifted")


def release(home_buddy):
    home_buddy.set_uart_servo_angle(6, 0)
    time.sleep(0.6)
    print("Action: Object released")


# ----------- VOICE FEEDBACK FUNCTIONS -----------
def send_voice_feedback(ser, feedback_code):
    """Send voice feedback command to the voice module"""
    try:
        ser.write(feedback_code.encode())
        print(f"Voice feedback sent: {feedback_code}")
    except Exception as e:
        print(f"Error sending voice feedback: {e}")


# ----------- NAVIGATION FUNCTIONS -----------
def go_to_point_A(home_buddy, ser):
    print("Action: Going to point A")
    # Add your navigation logic for point A here
    send_voice_feedback(ser, "$A019#")  # "OK, I'm going to the point A."


def go_to_point_B(home_buddy, ser):
    print("Action: Going to point B")
    # Add your navigation logic for point B here
    send_voice_feedback(ser, "$A020#")  # "OK, I'm going to the point B."


def go_to_point_C(home_buddy, ser):
    print("Action: Going to point C")
    # Add your navigation logic for point C here
    send_voice_feedback(ser, "$A021#")  # "OK, I'm going to the point C."


def go_to_point_D(home_buddy, ser):
    print("Action: Going to point D")
    # Add your navigation logic for point D here
    send_voice_feedback(ser, "$A022#")  # "OK, I'm going to the point D."


def return_to_original_place(home_buddy, ser):
    print("Action: Returning to original place")
    # Add your return navigation logic here
    send_voice_feedback(ser, "$A023#")  # "OK, I'm return back."


# ----------- VOICE MODULE INITIALIZATION -----------
def initialize_module(ser):
    print("Initializing voice module...")
    commands = [
        b'AT+ASR=ON\r\n',
        b'AT+CMD=1\r\n',
        b'AT+DEBUG=1\r\n'
    ]
    for cmd in commands:
        ser.write(cmd)
        time.sleep(0.2)
    ser.flushInput()
    print("Voice module initialized. Waiting for commands...")


# ----------- MAIN FUNCTION -----------
def main():
    # Initialize Rosmaster
    home_buddy = Rosmaster()
    home_buddy.create_receive_threading()
    print("Rosmaster initialized.")

    # Initialize Voice Module
    try:
        ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
        time.sleep(1)
    except Exception as e:
        print("Failed to open serial port:", e)
        return

    initialize_module(ser)

    print("Listening for voice commands. Say 'Hi Yahboom' to wake up...")

    while True:
        try:
            if ser.in_waiting:
                data = ser.readline()
                if data:
                    text = data.decode(errors="ignore").strip()
                    if text:
                        print("Received:", text)

                        # Convert to lowercase for command matching (except for navigation commands)
                        text_lower = text.lower()

                        # ---------- VOICE COMMANDS ----------
                        if text_lower == "$b000#":
                            print("Wake word detected.")

                        elif text_lower == "$b004#":
                            move_forward(home_buddy)

                        elif text_lower == "$b005#":
                            move_backward(home_buddy)

                        elif text_lower == "$b006#":
                            turn_left(home_buddy)

                        elif text_lower == "$b007#":
                            turn_right(home_buddy)

                        elif text_lower == "$b002#":
                            stop(home_buddy)

                        elif text_lower == "$b043#":
                            grab(home_buddy)

                        elif text_lower == "loose":
                            release(home_buddy)

                        # Multi-point navigation commands
                        elif text == "$B019#":
                            go_to_point_A(home_buddy, ser)

                        elif text == "$B020#":
                            go_to_point_B(home_buddy, ser)

                        elif text == "$B021#":
                            go_to_point_C(home_buddy, ser)

                        elif text == "$B022#":
                            go_to_point_D(home_buddy, ser)

                        elif text == "$B023#":
                            return_to_original_place(home_buddy, ser)

                        elif text_lower.startswith("track"):
                            color = text_lower.split(" ")[1] if len(text_lower.split(" ")) > 1 else "unknown"
                            print(f"Action: Track {color} (Not implemented yet)")

        except KeyboardInterrupt:
            print("Exiting...")
            ser.close()
            break
        except Exception as e:
            print("Error:", e)
            continue


if __name__ == "__main__":
    main()

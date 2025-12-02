import serial
import time
from Rosmaster_Lib import Rosmaster

# ----------------- CONFIG -----------------
PORT = "/dev/ttyUSB2"  # Yahboom voice module port
BAUD = 115200
TIMEOUT = 0.1
# -----------------------------------------

# ----------- ROBOT MOVEMENT FUNCTIONS -----------
def move_forward(rosmaster):
    rosmaster.set_car_motion(0.5, 0, 0)
    time.sleep(2)
    rosmaster.set_car_motion(0, 0, 0)
    print("Action: Moved forward")

def move_backward(rosmaster):
    rosmaster.set_car_motion(-0.5, 0, 0)
    time.sleep(2)
    rosmaster.set_car_motion(0, 0, 0)
    print("Action: Moved backward")

def turn_left(rosmaster):
    rosmaster.set_car_motion(0, 0, 0.5)
    time.sleep(1.5)
    rosmaster.set_car_motion(0, 0, 0)
    print("Action: Turned left")

def turn_right(rosmaster):
    rosmaster.set_car_motion(0, 0, -0.5)
    time.sleep(1.5)
    rosmaster.set_car_motion(0, 0, 0)
    print("Action: Turned right")

def stop(rosmaster):
    rosmaster.set_car_motion(0, 0, 0)
    print("Action: Stopped")

def grab(rosmaster):
    rosmaster.set_uart_servo_angle(6, 180)
    time.sleep(0.6)
    rosmaster.set_uart_servo_angle_array([90, 80, 110, 90, 90, 180])
    time.sleep(0.8)
    print("Action: Object grabbed")

def release(rosmaster):
    rosmaster.set_uart_servo_angle(6, 0)
    time.sleep(0.6)
    print("Action: Object released")

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
    rosmaster = Rosmaster()
    rosmaster.create_receive_threading()
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
                    text = data.decode(errors="ignore").strip().lower()
                    if text:
                        print("Received:", text)

                        # ---------- VOICE COMMANDS ----------
                        if text == "$b000#":
                           print("Wake word detected.")

                        elif text == "$b004#":
                            move_forward(rosmaster)

                        elif text == "$b005#":
                            move_backward(rosmaster)

                        elif text == "$b006#":
                            turn_left(rosmaster)

                        elif text == "$b007#":
                            turn_right(rosmaster)

                        elif text == "$b002#":
                            stop(rosmaster)

                        elif text == "$b011#":
                            grab(rosmaster)

                        elif text == "loose":
                            release(rosmaster)

        except KeyboardInterrupt:
            print("Exiting...")
            ser.close()
            break
        except Exception as e:
            print("Error:", e)
            continue

if __name__ == "__main__":
    main()

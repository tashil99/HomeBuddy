import time
from Rosmaster_Lib import Rosmaster

def move_forward(rosmaster):
    rosmaster.set_car_motion(0.5, 0, 0)
    time.sleep(2)
    rosmaster.set_car_motion(0, 0, 0)

def move_backward(rosmaster):
    rosmaster.set_car_motion(-0.5, 0, 0)
    time.sleep(2)
    rosmaster.set_car_motion(0, 0, 0)

def grab(rosmaster):
    rosmaster.set_uart_servo_angle(6, 180)
    time.sleep(0.6)
    rosmaster.set_uart_servo_angle_array([90, 80, 110, 90, 90, 180])
    time.sleep(0.8)
    print("Object grabbed.")

def main():
    ACTIONS = {
        "1": move_forward,
        "2": move_backward,
        "3": grab
    }

    rosmaster = Rosmaster()
    rosmaster.create_receive_threading()

    print("Available commands:")
    for cmd in ACTIONS:
        print(f" - {cmd}")
    print("Type 'exit' to quit.")

    while True:
        command = input("Enter command: ").strip().lower()
        if command == "exit":
            print("Exiting...")
            break
        elif command in ACTIONS:
            print(f"Performing: {command}")
            ACTIONS[command](rosmaster)
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()
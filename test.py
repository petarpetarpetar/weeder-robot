import serial
import threading
import keyboard
import logging
import argparse
from typing import Dict


# Configuration
SERIAL_PORT = "/dev/ttyUSB0"  # Update with your serial port
BAUD_RATE = 115200


# Argument parser for command-line options
parser = argparse.ArgumentParser(description="Motor Control Script")
parser.add_argument(
    "--debug", action="store_true", help="Enable debug messages on the console"
)
args = parser.parse_args()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File handler to log all messages
file_handler = logging.FileHandler("motor_control.log")
file_handler.setLevel(logging.DEBUG)

# Console handler to log only INFO and above by default
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class SerialCommunicator:
    def __init__(self, port: str, baud_rate: int):
        self.ser = serial.Serial(port, baud_rate, timeout=1)
        logging.info(f"Serial port open: {self.ser.is_open}")

    def send_command(self, command: str) -> None:
        self.ser.write(command.encode())
        logging.info(f"Sent: {command.strip()}")

    def read_serial(self) -> None:
        while True:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode().strip()
                logging.info(f"Received: {data}")

    def close(self) -> None:
        self.ser.close()
        logging.info("Serial port closed")


class MotorController:
    def __init__(self, serial_communicator: SerialCommunicator):
        self.serial_communicator = serial_communicator
        self.motor_states: Dict[str, str] = {"motor_1": "stopped", "motor_2": "stopped"}

    def increase_speed(self) -> None:
        self.serial_communicator.send_command("INCREASE_SPEED\n")
        logging.info("Command: Increase Speed")

    def decrease_speed(self) -> None:
        self.serial_communicator.send_command("DECREASE_SPEED\n")
        logging.info("Command: Decrease Speed")

    def motor_1_forward_start(self) -> None:
        if self.motor_states["motor_1"] != "forward":
            self.serial_communicator.send_command("M1F\n")
            logging.info("Command: Motor 1 Forward Start")
            self.motor_states["motor_1"] = "forward"

    def motor_1_forward_stop(self) -> None:
        if self.motor_states["motor_1"] != "stopped":
            self.serial_communicator.send_command("M1S\n")
            logging.info("Command: Motor 1 Stop")
            self.motor_states["motor_1"] = "stopped"

    def motor_1_backward_start(self) -> None:
        if self.motor_states["motor_1"] != "backward":
            self.serial_communicator.send_command("M1R\n")
            logging.info("Command: Motor 1 Backward Start")
            self.motor_states["motor_1"] = "backward"

    def motor_1_backward_stop(self) -> None:
        if self.motor_states["motor_1"] != "stopped":
            self.serial_communicator.send_command("M1S\n")
            logging.info("Command: Motor 1 Stop")
            self.motor_states["motor_1"] = "stopped"

    def motor_2_forward_start(self) -> None:
        if self.motor_states["motor_2"] != "forward":
            self.serial_communicator.send_command("M2F\n")
            logging.info("Command: Motor 2 Forward Start")
            self.motor_states["motor_2"] = "forward"

    def motor_2_forward_stop(self) -> None:
        if self.motor_states["motor_2"] != "stopped":
            self.serial_communicator.send_command("M2S\n")
            logging.info("Command: Motor 2 Stop")
            self.motor_states["motor_2"] = "stopped"

    def motor_2_backward_start(self) -> None:
        if self.motor_states["motor_2"] != "backward":
            self.serial_communicator.send_command("M2R\n")
            logging.info("Command: Motor 2 Backward Start")
            self.motor_states["motor_2"] = "backward"

    def motor_2_backward_stop(self) -> None:
        if self.motor_states["motor_2"] != "stopped":
            self.serial_communicator.send_command("M2S\n")
            logging.info("Command: Motor 2 Stop")
            self.motor_states["motor_2"] = "stopped"


class KeyboardController:
    def __init__(self, motor_controller: MotorController):
        self.motor_controller = motor_controller
        self.key_states: Dict[str, bool] = {
            "w": False,
            "a": False,
            "s": False,
            "d": False,
            "q": False,  # Not really needed, just to keep everything consistent
            "e": False,  # Not really needed, just to keep everything consistent
        }

    def on_key_event(self, event: keyboard.KeyboardEvent) -> None:
        if event.event_type == "down" and not self.key_states[event.name]:
            self.key_states[event.name] = True
            if event.name == "q":
                self.motor_controller.decrease_speed()
            elif event.name == "e":
                self.motor_controller.increase_speed()
            elif event.name == "w":
                self.motor_controller.motor_1_forward_start()
            elif event.name == "s":
                self.motor_controller.motor_1_backward_start()
            elif event.name == "a":
                self.motor_controller.motor_2_forward_start()
            elif event.name == "d":
                self.motor_controller.motor_2_backward_start()
            logging.debug(f"Key pressed: {event.name}")

        elif event.event_type == "up" and self.key_states[event.name]:
            self.key_states[event.name] = False
            if event.name == "w":
                self.motor_controller.motor_1_forward_stop()
            elif event.name == "s":
                self.motor_controller.motor_1_backward_stop()
            elif event.name == "a":
                self.motor_controller.motor_2_forward_stop()
            elif event.name == "d":
                self.motor_controller.motor_2_backward_stop()
            logging.debug(f"Key released: {event.name}")


class MainController:
    def __init__(
        self,
        serial_communicator: SerialCommunicator,
        keyboard_controller: KeyboardController,
    ):
        self.serial_communicator = serial_communicator
        self.keyboard_controller = keyboard_controller

    def run(self) -> None:
        # Create a thread for reading serial data
        read_thread = threading.Thread(target=self.serial_communicator.read_serial)
        read_thread.start()

        # Set up keyboard listeners
        keyboard.hook(self.keyboard_controller.on_key_event)

        # Monitor for exit key press
        try:
            while True:
                if keyboard.is_pressed("esc"):  # Use "esc" to exit the program
                    logging.info("Exiting program...")
                    self.stop_all_motors()
                    break
        except KeyboardInterrupt:
            logging.info("Program interrupted")
        finally:
            self.serial_communicator.close()

    def stop_all_motors(self) -> None:
        self.keyboard_controller.motor_controller.motor_1_forward_stop()
        self.keyboard_controller.motor_controller.motor_1_backward_stop()
        self.keyboard_controller.motor_controller.motor_2_forward_stop()
        self.keyboard_controller.motor_controller.motor_2_backward_stop()
        logging.info("All motors stopped")


if __name__ == "__main__":
    serial_communicator = SerialCommunicator(SERIAL_PORT, BAUD_RATE)
    motor_controller = MotorController(serial_communicator)
    keyboard_controller = KeyboardController(motor_controller)
    main_controller = MainController(serial_communicator, keyboard_controller)
    main_controller.run()

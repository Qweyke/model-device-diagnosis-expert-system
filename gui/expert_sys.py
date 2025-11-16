# expert_sys_terminal.py
from experta import *


class Device(Fact):
    """Template: Terminal-device status"""

    power: str = "unknown"
    led_color: str = "unknown"
    internal_state: str = "unknown"


class DeviceExpertSystem(KnowledgeEngine):

    # --- Rules to ask slot values ---
    @Rule(Device(power="unknown"))
    def check_power(self):
        self.modify(self.facts[1], power=self.ask_slot_value("power"))

    @Rule(Device(power="on", led_color="unknown"))
    def check_led_color(self):
        self.modify(self.facts[1], led_color=self.ask_slot_value("led_color"))

    @Rule(Device(power="on", led_color="yellow", internal_state="unknown"))
    def check_internal_state(self):
        self.modify(self.facts[1], internal_state=self.ask_slot_value("internal_state"))

    # --- Diagnosis Rules ---
    @Rule(Device(power="off"))
    def diagnose_no_power(self):
        print("Diagnosis: Connect the power supply to device")
        self.halt()

    @Rule(Device(power="on", led_color="none"))
    def diagnose_led_none(self):
        print(
            "Diagnosis: Hardware fault detected - send the board for physical diagnostics"
        )
        self.halt()

    @Rule(Device(power="on", led_color="red"))
    def diagnose_led_red(self):
        print("Diagnosis: CPU malfunction - send the board for CPU reballing")
        self.halt()

    @Rule(Device(power="on", led_color="yellow", internal_state="errfile"))
    def diagnose_led_yellow_errfile(self):
        print("Diagnosis: Flash error - reflash device with Stable.bin image")
        self.halt()

    @Rule(Device(power="on", led_color="yellow", internal_state="erraddress"))
    def diagnose_led_yellow_erraddr(self):
        print(
            "Diagnosis: Bootloader address fault - reflash device with Recovery.bin image"
        )
        self.halt()

    @Rule(Device(power="on", led_color="green"))
    def diagnose_led_green_ok(self):
        print("Diagnosis: Device fully operational - ready for casing")
        self.halt()

    @Rule(Device(power="on", led_color="blue"))
    def diagnose_led_blue(self):
        print("Diagnosis: Firmware update process detected")
        self.halt()

    # --- Slot asking method ---
    def ask_slot_value(self, slot: str) -> str:
        allowed_values = {
            "power": ["on", "off", "unknown"],
            "led_color": ["red", "green", "yellow", "blue", "none", "unknown"],
            "internal_state": ["errfile", "erraddress", "unknown"],
        }
        while True:
            val = (
                input(
                    f"[Device Poll] What's the status of {slot}? {allowed_values[slot]}: "
                )
                .strip()
                .lower()
            )
            if val in allowed_values[slot]:
                return val
            print(f"Invalid input. Allowed: {allowed_values[slot]}")


# --- Terminal Start Function (like CLIPS start) ---
def start():
    engine = DeviceExpertSystem()
    engine.reset()  # Reset engine
    engine.declare(Device())  # Declare initial device fact
    engine.run()  # Run engine


if __name__ == "__main__":
    print("=== Device Expert System ===")
    start()

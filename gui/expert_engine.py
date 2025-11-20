from experta import *
from PySide6.QtCore import QObject, Signal, QEventLoop


class Device(Fact):
    power = Field(str, default="unknown")           # "off" / "on"
    power_source = Field(str, default="unknown")    
    led_color = Field(str, default="unknown")
    internal_state = Field(str, default="unknown")

    allowed_vals = {
        "power": ["off", "on"],
        "power_source": ["low", "sufficient"],
        "led_color": ["red", "green", "yellow", "blue", "none"],
        "internal_state": ["errfile", "erraddress", "unknown_error", "firmware_update", "component_test", "unknown"]
    }


class DeviceDiagnosisEngine(KnowledgeEngine, QObject):
    """
    Expert system engine.
    Emits signals to GUI instead of calling it directly.
    """

    signal_request_input = Signal(str, list)
    signal_diagnosis_ready = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        KnowledgeEngine.__init__(self)

        self.loop = None
        self.last_answer = None

    def provide_answer(self, slot, value):
        """Called by GUI to provide user input."""
        self.last_answer = value.lower()
        if self.loop and self.loop.isRunning():
            self.loop.quit()

    def ask_value(self, slot, allowed_vals=None):
        """Emit signal to GUI and wait for answer."""
        if allowed_vals is None:
            allowed_vals = Device.allowed_vals[slot]

        self.signal_request_input.emit(slot, allowed_vals)
        self.loop = QEventLoop()
        self.loop.exec()
        return self.last_answer or "unknown"

    # ------------------- Facts -------------------
    @DefFacts()
    def start_facts(self):
        yield Device()

    # ------------------- Rules: Power -------------------
    @Rule(AS.dev << Device(power="unknown"))
    def rule_power(self, dev):
        v = self.ask_value("power", allowed_vals=["off", "on"])
        self.modify(dev, power=v)

    @Rule(AS.dev << Device(power="on", power_source="unknown"))
    def rule_power_source(self, dev):
        v = self.ask_value("power_source", allowed_vals=["low", "sufficient"])
        self.modify(dev, power_source=v)

    # ------------------- Rules: Low power -------------------
    @Rule(AS.dev << Device(power="on", power_source="low", led_color="unknown"))
    def rule_led_low(self, dev):
        v = self.ask_value("led_color", allowed_vals=["yellow", "red"])
        self.modify(dev, led_color=v)

    @Rule(Device(power="on", power_source="low", led_color="red"))
    def diag_red_low(self):
        self.signal_diagnosis_ready.emit(
            "Critical unknown error — diagnostics cannot continue with low power."
        )

    @Rule(AS.dev << Device(power="on", power_source="low", led_color="yellow", internal_state="unknown"))
    def rule_internal_low(self, dev):
        v = self.ask_value("internal_state", allowed_vals=["errfile", "erraddress", "unknown_error"])
        self.modify(dev, internal_state=v)

    @Rule(Device(power="on", power_source="low", led_color="yellow", internal_state="errfile"))
    def diag_yellow_errfile_low(self):
        self.signal_diagnosis_ready.emit(
            "Flash error — partial diagnostics.\nSolution: reflash Stable.bin when power is sufficient."
        )

    @Rule(Device(power="on", power_source="low", led_color="yellow", internal_state="erraddress"))
    def diag_yellow_erraddress_low(self):
        self.signal_diagnosis_ready.emit(
            "Bootloader address fault — partial diagnostics.\nSolution: reflash Recovery.bin when power is sufficient."
        )

    @Rule(Device(power="on", power_source="low", led_color="yellow", internal_state="unknown_error"))
    def diag_yellow_unknown_low(self):
        self.signal_diagnosis_ready.emit(
            "Unknown error — device may behave unpredictably.\nSolution: check power and repeat diagnostics."
        )

    # ------------------- Rules: Sufficient power -------------------
    @Rule(AS.dev << Device(power="on", power_source="sufficient", led_color="unknown"))
    def rule_led_sufficient(self, dev):
        v = self.ask_value("led_color", allowed_vals=["green", "yellow", "red", "blue", "none"])
        self.modify(dev, led_color=v)

    @Rule(AS.dev << Device(power="on", power_source="sufficient", led_color="yellow", internal_state="unknown"))
    def rule_internal_yellow(self, dev):
        v = self.ask_value("internal_state", allowed_vals=["errfile", "erraddress", "unknown_error"])
        self.modify(dev, internal_state=v)

    @Rule(AS.dev << Device(power="on", power_source="sufficient", led_color="blue", internal_state="unknown"))
    def rule_internal_blue(self, dev):
        v = self.ask_value("internal_state", allowed_vals=["firmware_update", "component_test", "unknown"])
        self.modify(dev, internal_state=v)

    # ------------------- Diagnoses: Sufficient power -------------------
    @Rule(Device(power="on", power_source="sufficient", led_color="red"))
    def diag_red(self):
        self.signal_diagnosis_ready.emit("CPU malfunction — send for reballing.")

    @Rule(Device(power="on", power_source="sufficient", led_color="green"))
    def diag_green(self):
        self.signal_diagnosis_ready.emit("Device fully operational — OK.")

    @Rule(Device(power="on", power_source="sufficient", led_color="yellow", internal_state="errfile"))
    def diag_yellow_errfile(self):
        self.signal_diagnosis_ready.emit("Flash error — reflash Stable.bin")

    @Rule(Device(power="on", power_source="sufficient", led_color="yellow", internal_state="erraddress"))
    def diag_yellow_erraddress(self):
        self.signal_diagnosis_ready.emit("Bootloader address fault — reflash Recovery.bin")

    @Rule(Device(power="on", power_source="sufficient", led_color="yellow", internal_state="unknown_error"))
    def diag_yellow_unknown(self):
        self.signal_diagnosis_ready.emit("Unknown yellow LED state — check device.")

    @Rule(Device(power="on", power_source="sufficient", led_color="blue", internal_state="firmware_update"))
    def diag_blue_fw(self):
        self.signal_diagnosis_ready.emit("Firmware update in progress — do not disconnect power.")

    @Rule(Device(power="on", power_source="sufficient", led_color="blue", internal_state="component_test"))
    def diag_blue_comp(self):
        self.signal_diagnosis_ready.emit("Component self-test running — wait until complete.")

    @Rule(Device(power="on", power_source="sufficient", led_color="blue", internal_state="unknown"))
    def diag_blue_unknown(self):
        self.signal_diagnosis_ready.emit("Unknown blue LED state — consult documentation.")

    @Rule(Device(power="on", power_source="sufficient", led_color="none"))
    def diag_none(self):
        self.signal_diagnosis_ready.emit("Hardware fault — send board for physical inspection.")

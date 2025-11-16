from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent
CLP_SCRIPT_PATH = BASE_DIR / "clips_core" / "diagnostic-system.clp"
CLIPS_HARDCODED_EXE_PATH = Path(
    "C:/Users/Qweyke/Desktop/clips_core_source_640/core/CLIPS.exe"
)


class Clips:

    def __init__(self, clips_exe: Path, clp_script: Path):
        self.clips_exe_path = clips_exe
        self.clp_file = clp_script
        self.process = None

    def start(self):
        """Start CLIPS in subprocess mode with stdin/stdout pipes."""
        self.process = subprocess.Popen(
            [str(self.clips_exe_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # ensures strings instead of bytes
        )
        print(self.send_command(f"facts"))
        # Load the CLP file
        # self.send_command(f'(load "{self.clp_file}")/n')

    def send_command(self, command: str) -> str:
        """Send a command to CLIPS and get the output."""
        if not self.process:
            raise RuntimeError("CLIPS process not started")

        # Отправляем команду с реальным переносом строки
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

        print(f"Command sent: {command}")

        # Считываем строки до подсказки 'CLIPS>'
        output_lines = []
        while True:
            line = self.process.stdout.readline()
            if not line:  # EOF
                break
            stripped = line.strip()
            if stripped.endswith("CLIPS>"):  # иногда CLIPS> на конце строки
                break
            output_lines.append(line)
        return "".join(output_lines)

    def stop(self):
        if self.process:
            self.send_command("(exit)")
            self.process.stdin.close()
            self.process.stdout.close()
            self.process.stderr.close()
            self.process.wait()
            self.process = None


if __name__ == "__main__":
    clips = Clips(CLIPS_HARDCODED_EXE_PATH, CLP_SCRIPT_PATH)
    clips.start()
    output = clips.send_command("(facts)")
    print("CLIPS facts:/n", output)
    clips.stop()

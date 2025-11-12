from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CLP_SCRIPT_PATH = BASE_DIR / "clips_core" / "diagnostic-system.clp"
CLIPS_HARDCODED_EXE_PATH = Path("C:\Users\Qweyke\Desktop\CLIPS 6.4\CLIPSDOS.exe")


# print(f"CLIPS file located at: {CLIPS_PATH}")

def start(clips_exe_path: Path):


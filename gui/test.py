import subprocess

result = subprocess.run(
    [
        "C:/Users/Qweyke/Desktop/clips_core_source_640/core/CLIPS.exe",
        "-f",
        "clips_core/diagnostic-system.clp",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

print(result.stdout)

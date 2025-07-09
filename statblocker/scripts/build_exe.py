import subprocess
from pathlib import Path


def build_exe():
    entry_point_script = Path(__file__).resolve().parent.parent / "main.py"
    subprocess.run(
        [
            "pyinstaller",
            "--onefile",
            "--noconsole",  # Important for GUI apps!
            "--name",
            "statblocker",  # The name of the final .exe
            str(entry_point_script),  # Your PyQt5 entry point
        ],
        check=True,
    )
    print("✅ Executable created in ./dist/")


if __name__ == "__main__":
    build_exe()

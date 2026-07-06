import subprocess
import os

os.makedirs("docs/reports", exist_ok=True)

commands = [
    ("ruff", "python -m ruff check backend/ tests/"),
    ("mypy", "python -m mypy backend/ tests/"),
    ("bandit", "python -m bandit -r backend/"),
    ("pytest", "python -m pytest --cov=backend tests/ --cov-report=term-missing"),
    ("smoke", "python smoke_test.py")
]

for name, cmd in commands:
    with open(f"docs/reports/{name}.txt", "w") as f:
        print(f"Running {name}...")
        f.write(f"COMMAND: {cmd}\n")
        f.write("="*40 + "\n")
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, _ = process.communicate()
        f.write(out.decode("utf-8", errors="replace"))
        f.write("\n" + "="*40 + "\n")
        f.write(f"EXIT_CODE: {process.returncode}\n")
print("Done.")

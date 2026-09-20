"""
Entry point runner script for Pragati Bharati Document Intelligence Service.
Run with: python run.py
"""
import os
import sys

# Auto-detect and switch to local project virtual environment if run under system Python
base_dir = os.path.dirname(os.path.abspath(__file__))
venv_windows = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
venv_posix = os.path.join(base_dir, ".venv", "bin", "python")

target_python = None
if os.path.exists(venv_windows):
    target_python = venv_windows
elif os.path.exists(venv_posix):
    target_python = venv_posix

if target_python:
    current_exe = os.path.normcase(os.path.abspath(sys.executable))
    target_exe = os.path.normcase(os.path.abspath(target_python))
    if current_exe != target_exe:
        import subprocess
        print(f"[*] Switching to virtual environment Python: {target_python}")
        try:
            result = subprocess.run([target_python] + sys.argv, cwd=base_dir)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            sys.exit(0)

try:
    import uvicorn
except ModuleNotFoundError:
    print("=" * 70)
    print("[!] ERROR: 'uvicorn' is not installed in the current Python environment.")
    print(f"    Current Python: {sys.executable}")
    print("\nTo resolve this, please either:")
    print("  1. Run using the project virtual environment:")
    print(r"     .\.venv\Scripts\python.exe run.py")
    print("  2. Activate the virtual environment in PowerShell:")
    print(r"     .\.venv\Scripts\Activate.ps1")
    print("     python run.py")
    print("  3. Or install the dependencies:")
    print("     pip install -r requirements.txt")
    print("=" * 70)
    sys.exit(1)

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Pragati Bharati Document Intelligence & Question Extraction Service")
    print("Web Workbench UI:       http://127.0.0.1:8000/")
    print("Swagger API Docs:       http://127.0.0.1:8000/docs")
    print("ReDoc Documentation:    http://127.0.0.1:8000/redoc")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

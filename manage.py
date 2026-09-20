"""
Convenience CLI wrapper for running the Pragati Bharati FastAPI service.
Supports:
  python manage.py runserver
  python manage.py
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
    print(r"     .\.venv\Scripts\python.exe manage.py")
    print("  2. Activate the virtual environment:")
    print(r"     .\.venv\Scripts\Activate.ps1")
    print("     python manage.py")
    print("  3. Or install the dependencies:")
    print("     pip install -r requirements.txt")
    print("=" * 70)
    sys.exit(1)

def main():
    print("=" * 70)
    print("Pragati Bharati Document Intelligence Workbench (FastAPI)")
    print("Web Workbench:   http://127.0.0.1:8000/")
    print("Swagger Docs:    http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

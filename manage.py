"""
Convenience CLI wrapper for running the Pragati Bharati FastAPI service.
Supports:
  python manage.py runserver
  python manage.py
"""
import sys
import uvicorn

def main():
    print("=" * 70)
    print("Pragati Bharati Document Intelligence Workbench (FastAPI)")
    print("Web Workbench:   http://127.0.0.1:8000/")
    print("Swagger Docs:    http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()

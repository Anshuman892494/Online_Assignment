"""
Entry point runner script for Pragati Bharati Document Intelligence Service.
Run with: python run.py
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Pragati Bharati Document Intelligence & Question Extraction Service")
    print("🌐 Web Workbench UI:       http://127.0.0.1:8000/")
    print("📑 Swagger API Docs:       http://127.0.0.1:8000/docs")
    print("📚 ReDoc Documentation:    http://127.0.0.1:8000/redoc")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

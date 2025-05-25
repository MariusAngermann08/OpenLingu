import uvicorn
import threading
import subprocess
import sys
import os
import time
from contextlib import contextmanager

@contextmanager
def change_dir(destination):
    """Context manager to temporarily change the working directory."""
    current_dir = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(current_dir)

def run_fastapi():
    """Run the FastAPI server using uvicorn."""
    config = uvicorn.Config(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()

def run_flet():
    """Run the Flet app using subprocess."""
    client_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client')
    with change_dir(client_dir):
        try:
            # Try running with 'flet run' command
            subprocess.run([sys.executable, "-m", "flet", "run", "src/main.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run with 'flet run', trying direct execution: {e}")
            # Fall back to running the Python file directly
            subprocess.run([sys.executable, "src/main.py"], check=True)

def main():
    print("Starting server and app...")
    
    # Start FastAPI server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("FastAPI server starting on http://localhost:8000")
    
    # Give the server a moment to start
    time.sleep(2)
    
    try:
        # Start Flet app in the main process
        print("Starting Flet app...")
        run_flet()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("Application stopped")

if __name__ == "__main__":
    main()

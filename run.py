import uvicorn
import threading
import subprocess
import sys
import os
import time
import argparse
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



def run_flet(web_mode=False):
    """Run the Flet app using subprocess and return the process object and whether it's in web mode."""
    client_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client')
    with change_dir(client_dir):
        try:
            # Try using the flet command directly first
            cmd = ["flet", "run", "src/main.py"]
            if web_mode:
                cmd.append("--web")
            
            # Run the command in a subprocess
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process, web_mode
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Failed to run with 'flet' command: {e}")
            
            # Fallback to python -m flet
            try:
                cmd = [sys.executable, "-m", "flet", "run", "src/main.py"]
                if web_mode:
                    cmd.append("--web")
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return process, web_mode
            except subprocess.SubprocessError as e2:
                print(f"Failed to run with 'python -m flet': {e2}")
                
            # Final fallback: run the Python file directly
            try:
                print("Attempting to run the app directly...")
                process = subprocess.Popen(
                    [sys.executable, "src/main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                return process, False  # Direct execution is never in web mode
            except subprocess.SubprocessError as e3:
                print(f"Failed to run app directly: {e3}")
                return None, False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run OpenLingu application')
    parser.add_argument('--web', action='store_true', help='Run Flet app in web browser')
    args = parser.parse_args()
    
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
    
    # Run the Flet app
    print("Starting Flet application...")
    flet_process, is_web = run_flet(web_mode=args.web)
    
    if not flet_process:
        print("\nFailed to start Flet application. Please make sure Flet is installed:")
        print("pip install flet")
        print("\nAlternatively, you can run the app directly with:")
        print("cd client && python src/main.py")
        # Clean up server process before exiting
        server_process.terminate()
        server_process.wait()
        return
    
    try:
        if is_web:
            print("\nRunning in web mode. The app should open in your default browser.")
            print("Press any key to stop the server and exit...")
            # Wait for any key press
            if os.name == 'nt':  # Windows
                import msvcrt
                msvcrt.getch()
            else:  # Unix/Linux/MacOS
                import termios, tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        else:
            # Monitor the Flet process for desktop mode
            while True:
                # Check if Flet process is still running
                if flet_process.poll() is not None:
                    print("\nFlet application has exited.")
                    break
                    
                # Check for keyboard interrupt
                time.sleep(0.5)
                    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up processes
        print("Stopping FastAPI server...")
        server_process.terminate()
        server_process.wait()
        
        # Ensure Flet process is terminated
        if flet_process and flet_process.poll() is None:
            print("Terminating Flet process...")
            flet_process.terminate()
            try:
                flet_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                flet_process.kill()
        
        print("Application stopped")

if __name__ == "__main__":
    main()

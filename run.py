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
    # Set environment variable to indicate we're running in development
    import os
    os.environ["ENVIRONMENT"] = "development"
    
    # Ensure the server module can be found
    import sys
    server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)
    
    # Configure uvicorn
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        reload_dirs=[server_dir],
        workers=1,
        loop="asyncio",
        timeout_keep_alive=30,
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except Exception as e:
        print(f"Error in FastAPI server: {e}", file=sys.stderr)
        raise



def run_flet(web_mode=False):
    """Run the Flet app using the flet command directly."""
    client_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client')
    
    try:
        with change_dir(client_dir):
            # Build the command
            cmd = ["flet", "run", "src/main.py"]
            if web_mode:
                cmd.append("--web")
            
            # Print the command for debugging
            print(f"Running: {' '.join(cmd)} in {os.getcwd()}")
            
            # Run the command in the client directory
            process = subprocess.Popen(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            return process, web_mode
            
    except Exception as e:
        print(f"Failed to start Flet application: {e}", file=sys.stderr)
        print("\nMake sure you're in the virtual environment and Flet is installed.")
        print("You can install it with: pip install flet")
        print("\nYou can also try running the app manually with:")
        print(f"  cd {client_dir}")
        print("  flet run src/main.py")
        return None, False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run OpenLingu application')
    parser.add_argument('--web', action='store_true', help='Run Flet app in web browser')
    args = parser.parse_args()
    
    print("Starting server and app...")
    
    # Start FastAPI server in a separate process with clean environment
    server_env = os.environ.copy()
    server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
    server_env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
    
    # Print debug info
    print(f"Starting server from: {server_dir}")
    print(f"Python executable: {sys.executable}")
    
    server_process = None
    try:
        server_process = subprocess.Popen(
            [
                sys.executable, 
                "-m", 
                "uvicorn", 
                "main:app",  # Changed from server.main:app to main:app since we're running from server dir
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload",
                "--reload-dir", server_dir,
                "--workers", "1"
            ],
            cwd=server_dir,  # Run from the server directory
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=server_env,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Start threads to capture output
        def log_stream(stream, prefix):
            for line in iter(stream.readline, ''):
                print(f"[{prefix}] {line.strip()}")
        
        import threading
        threading.Thread(target=log_stream, args=(server_process.stdout, "SERVER"), daemon=True).start()
        threading.Thread(target=log_stream, args=(server_process.stderr, "SERVER-ERR"), daemon=True).start()
        
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        if server_process:
            server_process.terminate()
        raise
    
    print("FastAPI server starting on http://localhost:8000")
    
    # Wait for server to be ready with more detailed logging
    max_wait = 30  # seconds
    start_time = time.time()
    server_ready = False
    last_error = None
    
    print("Waiting for server to be ready...")
    while time.time() - start_time < max_wait:
        if server_process.poll() is not None:
            # Server process has exited
            stdout, stderr = server_process.communicate()
            print(f"Server process exited with code {server_process.returncode}")
            if stdout:
                print(f"Server stdout:\n{stdout}")
            if stderr:
                print(f"Server stderr:\n{stderr}", file=sys.stderr)
            raise RuntimeError("Server process exited unexpectedly")
            
        try:
            import requests
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                server_ready = True
                print("Server is ready!")
                break
            else:
                print(f"Server returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            # Print progress every 5 seconds
            if int(time.time() - start_time) % 5 == 0:
                print(f"Waiting for server... ({int(time.time() - start_time)}s, last error: {last_error})")
        time.sleep(0.5)
    
    if not server_ready:
        print(f"Warning: Server did not become ready after {max_wait} seconds. Last error: {last_error}")
        print("Attempting to continue anyway...")
    
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
            print("Press Ctrl+C to stop the server and exit...")
        
        # Monitor the Flet process
        while True:
            # Check if Flet process is still running
            if flet_process.poll() is not None:
                print("\nFlet application has exited.")
                break
                
            # Check for keyboard interrupt
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
                    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up processes in reverse order
        if flet_process:
            print("Terminating Flet process...")
            try:
                if flet_process.poll() is None:
                    # First try to terminate gracefully
                    flet_process.terminate()
                    try:
                        flet_process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        print("Flet process did not terminate gracefully, forcing...")
                        flet_process.kill()
                        flet_process.wait()
                
                # Print any remaining output
                try:
                    stdout, stderr = flet_process.communicate(timeout=1)
                    if stdout:
                        print(f"Flet final stdout:\n{stdout}")
                    if stderr:
                        print(f"Flet final stderr:\n{stderr}", file=sys.stderr)
                except:
                    pass
                    
            except Exception as e:
                print(f"Error stopping Flet process: {e}")
                try:
                    if flet_process.poll() is None:
                        flet_process.kill()
                except:
                    pass
        
        print("Stopping FastAPI server...")
        if server_process:
            try:
                if server_process.poll() is None:
                    if os.name == 'nt':
                        # On Windows, use taskkill to ensure the process tree is terminated
                        import signal
                        os.kill(server_process.pid, signal.CTRL_BREAK_EVENT)
                        try:
                            server_process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            print("Server did not terminate gracefully, forcing...")
                            subprocess.run(['taskkill', '/F', '/T', '/PID', str(server_process.pid)], 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        # On Unix, send SIGTERM and then SIGKILL if needed
                        server_process.terminate()
                        try:
                            server_process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            print("Server did not terminate gracefully, killing...")
                            server_process.kill()
                
                # Print any remaining output
                try:
                    stdout, stderr = server_process.communicate(timeout=2)
                    if stdout:
                        print(f"Server final stdout:\n{stdout}")
                    if stderr:
                        print(f"Server final stderr:\n{stderr}", file=sys.stderr)
                except:
                    pass
                    
            except Exception as e:
                print(f"Error stopping server: {e}")
                try:
                    server_process.kill()
                except:
                    pass
        
        print("Application stopped")

if __name__ == "__main__":
    main()

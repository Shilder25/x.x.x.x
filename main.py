"""
Main entry point for TradingAgents deployment
Starts both Flask API and Next.js frontend
"""
import subprocess
import sys
import os
import time
import signal

# Store process references
processes = []

def signal_handler(sig, frame):
    """Clean shutdown of all processes"""
    print("\nShutting down services...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print("Starting TradingAgents Full Stack Application...")
    print("=" * 60)
    
    # Start Flask API on port 8000
    print("\n[1/2] Starting Flask API backend on port 8000...")
    api_process = subprocess.Popen(
        ["python", "api.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    processes.append(api_process)
    
    # Give API time to start
    time.sleep(2)
    
    # Start Next.js frontend on port 5000
    print("[2/2] Starting Next.js frontend on port 5000...")
    frontend_process = subprocess.Popen(
        ["sh", "-c", "cd frontend && npm install && npm start"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    processes.append(frontend_process)
    
    print("\n" + "=" * 60)
    print("✓ TradingAgents is running!")
    print("  - Frontend: http://localhost:5000")
    print("  - API: http://localhost:8000")
    print("=" * 60)
    
    # Keep the script running and monitor processes
    try:
        while True:
            # Check if any process has died
            for proc in processes:
                if proc.poll() is not None:
                    print(f"\nError: Process {proc.pid} died unexpectedly")
                    for p in processes:
                        p.terminate()
                    sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()

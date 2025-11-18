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
    # Wait for graceful shutdown
    time.sleep(1)
    for proc in processes:
        if proc.poll() is None:
            proc.kill()
    sys.exit(0)

def is_production():
    """Check if running in production (Railway or Replit deployment)"""
    return (os.getenv('REPL_DEPLOYMENT') == '1' or 
            os.getenv('REPLIT_DEPLOYMENT') == '1' or
            os.getenv('REPLIT_ENVIRONMENT') == 'production' or
            os.getenv('RAILWAY_ENVIRONMENT') is not None)

def setup_frontend():
    """Install dependencies and build Next.js for production if needed"""
    print("\n[1/3] Setting up Next.js frontend...")
    
    # Get absolute path to frontend directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "frontend")
    
    if not os.path.exists(frontend_dir):
        print(f"  ✗ Frontend directory not found: {frontend_dir}")
        sys.exit(1)
    
    # Always install dependencies first
    print("  → Installing npm dependencies...")
    install_result = subprocess.run(
        ["npm", "install"],
        cwd=frontend_dir,
        capture_output=False  # Show output directly
    )
    
    if install_result.returncode != 0:
        print("  ✗ Failed to install dependencies")
        sys.exit(1)
    
    # Build for production if in production mode
    if is_production():
        print("  → Building Next.js for production...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=False  # Show output directly
        )
        
        if build_result.returncode != 0:
            print("  ✗ Failed to build Next.js")
            sys.exit(1)
        
        print("  ✓ Next.js built successfully")
    else:
        print("  ✓ Running in development mode (skip build)")

def main():
    # Set up signal handlers (must be in main thread)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    mode = "PRODUCTION" if is_production() else "DEVELOPMENT"
    print("=" * 60)
    print(f"TradingAgents Full Stack Application - {mode} MODE")
    print("=" * 60)
    
    # Setup frontend (install + build if production)
    setup_frontend()
    
    # Start Flask API on port 8000
    print("\n[2/3] Starting Flask API backend on port 8000...")
    
    # Use Gunicorn in production (Railway/Replit) to avoid Flask debug reloader issues
    # Flask debug reloader loses environment variables on restart
    if is_production():
        print("  → Using Gunicorn (production WSGI server)")
        api_command = [
            "gunicorn",
            "--bind", "0.0.0.0:8000",
            "--workers", "2",
            "--timeout", "120",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "api:app"
        ]
    else:
        print("  → Using Flask development server")
        api_command = ["python", "api.py"]
    
    api_process = subprocess.Popen(
        api_command,
        env=os.environ.copy(),  # Pass Railway env vars (API keys, secrets)
        stdout=sys.stdout,  # Inherit stdout to avoid pipe blocking
        stderr=sys.stderr   # Inherit stderr to avoid pipe blocking
    )
    processes.append(api_process)
    print("  ✓ Flask API started (PID: {})".format(api_process.pid))
    
    # Give API time to start
    time.sleep(3)
    
    # Check if API is still running
    if api_process.poll() is not None:
        print("  ✗ Flask API died immediately")
        sys.exit(1)
    
    # Start Next.js frontend on port 5000
    print("\n[3/3] Starting Next.js frontend on port 5000...")
    
    # Get absolute path to frontend directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "frontend")
    
    # Use 'npm start' for production, 'npm run dev' for development
    npm_command = "start" if is_production() else "dev"
    
    frontend_process = subprocess.Popen(
        ["npm", "run", npm_command],
        cwd=frontend_dir,
        env=os.environ.copy(),  # Pass Railway env vars
        stdout=sys.stdout,  # Inherit stdout to avoid pipe blocking
        stderr=sys.stderr   # Inherit stderr to avoid pipe blocking
    )
    processes.append(frontend_process)
    print("  ✓ Next.js frontend started (PID: {})".format(frontend_process.pid))
    
    print("\n" + "=" * 60)
    print("✓ TradingAgents is running!")
    print("  - Frontend (Next.js): http://localhost:5000")
    print("  - API (Flask): http://localhost:8000")
    print("  - Mode: {}".format(mode))
    print("=" * 60)
    print("\nPress Ctrl+C to stop all services\n")
    
    # Keep the script running and monitor processes
    try:
        while True:
            # Check if any process has died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    service_name = "Flask API" if i == 0 else "Next.js Frontend"
                    print(f"\n✗ Error: {service_name} (PID: {proc.pid}) died unexpectedly")
                    print("  Exit code:", proc.returncode)
                    
                    # Kill all other processes
                    for p in processes:
                        if p.poll() is None:
                            p.terminate()
                    
                    sys.exit(1)
            
            time.sleep(2)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()

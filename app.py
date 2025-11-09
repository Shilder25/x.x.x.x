"""
Entry point for Replit deployment
This file exists to work with the existing .replit configuration
It redirects to main.py which properly launches Flask API + Next.js frontend
"""

if __name__ == "__main__":
    print("=" * 70)
    print("TradingAgents - Launching Full Stack Application")
    print("=" * 70)
    print("\nThis deployment uses:")
    print("  • Flask REST API (port 8000) - Backend services")
    print("  • Next.js React Frontend (port 5000) - Alpha Arena UI")
    print("\n" + "=" * 70)
    
    # Import and run main.py
    import main
    main.main()

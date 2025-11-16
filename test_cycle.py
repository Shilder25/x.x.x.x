#!/usr/bin/env python3
"""
Quick test script to run autonomous cycle and see detailed logs
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import TradingDatabase
from autonomous_engine import AutonomousEngine

def main():
    print("="*80)
    print("TESTING AUTONOMOUS CYCLE WITH FIXES")
    print("="*80)
    print()
    print("This will test:")
    print("  1. Pagination: Fetch ALL markets (not just 20)")
    print("  2. Fee calculation: Fee applies ONLY to winning payout")
    print("  3. Detailed logging: Shows events per category, EV calcs, rejection reasons")
    print()
    
    # Initialize database and engine
    db = TradingDatabase()
    engine = AutonomousEngine(db)
    
    print("Starting autonomous cycle...")
    print("-"*80)
    
    try:
        # Run the cycle
        results = engine.run_daily_cycle()
        
        print()
        print("="*80)
        print("CYCLE COMPLETED")
        print("="*80)
        print()
        print(f"Results: {results}")
        
    except Exception as e:
        import traceback
        print()
        print("="*80)
        print("CYCLE FAILED")
        print("="*80)
        print(f"Error: {e}")
        print()
        print("Traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    main()

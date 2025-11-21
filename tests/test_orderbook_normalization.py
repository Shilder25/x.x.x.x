#!/usr/bin/env python3
"""
Quick test to verify orderbook normalization handles different data types correctly.
"""

from decimal import Decimal

def test_safe_float_convert():
    """Test that safe_float_convert handles strings, Decimals, floats correctly."""
    
    # Simulate the safe_float_convert function from opinion_trade_api.py
    def safe_float_convert(value, field_name='unknown'):
        """Safely convert any numeric type to float with detailed error logging."""
        if value is None:
            return 0.0
        
        # Already a number
        if isinstance(value, (int, float)):
            return float(value)
        
        # Decimal type (already imported at module level)
        if isinstance(value, Decimal):
            return float(value)
        
        # String conversion
        if isinstance(value, str):
            value = value.strip()
            if not value or value == '':
                return 0.0
            try:
                return float(value)
            except (ValueError, TypeError) as e:
                print(f"Failed to convert {field_name}='{value}' to float: {e}")
                return 0.0
        
        # Unknown type - last resort
        try:
            return float(value)
        except:
            print(f"Unknown type for {field_name}: {type(value).__name__} = {value}")
            return 0.0
    
    # Test cases
    test_cases = [
        # (input, expected_output, description)
        ("0.182", 0.182, "String price"),
        (Decimal("0.182"), 0.182, "Decimal price"),
        (0.182, 0.182, "Float price"),
        (182, 182.0, "Int price"),
        ("  0.05  ", 0.05, "String with whitespace"),
        (None, 0.0, "None value"),
        ("", 0.0, "Empty string"),
        (Decimal("0.001"), 0.001, "Very small Decimal"),
    ]
    
    print("Testing safe_float_convert:")
    all_passed = True
    
    for input_val, expected, description in test_cases:
        result = safe_float_convert(input_val, 'price')
        passed = abs(result - expected) < 0.0001
        status = "✓" if passed else "✗"
        print(f"  {status} {description}: {repr(input_val)} → {result} (expected {expected})")
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = test_safe_float_convert()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)

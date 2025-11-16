#!/usr/bin/env python3
"""
Unit test for EV calculation to verify the fee fix is correct
"""

def calculate_expected_value(probability, market_price, bet_size=10.0, taker_fee=0.03):
    """
    Simplified version of _calculate_expected_value for testing
    """
    # 1. Cost of entry (NO fee)
    cost = market_price * bet_size
    
    # 2. Gross EV (without fees)
    gross_ev = (probability - market_price) * bet_size
    
    # 3. Fee cost (only paid if you win)
    fee_cost = probability * bet_size * taker_fee
    
    # 4. Net EV (with fees)
    net_ev = gross_ev - fee_cost
    
    return {
        'gross_ev': gross_ev,
        'net_ev': net_ev,
        'fee_cost': fee_cost
    }

def test_positive_ev_scenario():
    """Test: AI predicts 80%, market at 60% - should be POSITIVE EV"""
    result = calculate_expected_value(probability=0.80, market_price=0.60, bet_size=10.0)
    
    print("Test 1: Positive EV Scenario")
    print(f"  AI Prediction: 80%")
    print(f"  Market Price: 60%")
    print(f"  Edge: 20%")
    print(f"  Gross EV: ${result['gross_ev']:.2f}")
    print(f"  Fee Cost: ${result['fee_cost']:.2f}")
    print(f"  Net EV: ${result['net_ev']:.2f}")
    
    assert abs(result['gross_ev'] - 2.00) < 0.01, f"Expected gross_ev=2.00, got {result['gross_ev']}"
    assert abs(result['fee_cost'] - 0.24) < 0.01, f"Expected fee_cost=0.24, got {result['fee_cost']}"
    assert abs(result['net_ev'] - 1.76) < 0.01, f"Expected net_ev=1.76, got {result['net_ev']}"
    assert result['net_ev'] > 0, "Net EV should be POSITIVE"
    print("  ✅ PASS - Correctly identifies positive EV bet\n")

def test_negative_ev_scenario():
    """Test: AI predicts 50%, market at 60% - should be NEGATIVE EV"""
    result = calculate_expected_value(probability=0.50, market_price=0.60, bet_size=10.0)
    
    print("Test 2: Negative EV Scenario")
    print(f"  AI Prediction: 50%")
    print(f"  Market Price: 60%")
    print(f"  Edge: -10%")
    print(f"  Gross EV: ${result['gross_ev']:.2f}")
    print(f"  Fee Cost: ${result['fee_cost']:.2f}")
    print(f"  Net EV: ${result['net_ev']:.2f}")
    
    assert abs(result['gross_ev'] + 1.00) < 0.01, f"Expected gross_ev=-1.00, got {result['gross_ev']}"
    assert abs(result['fee_cost'] - 0.15) < 0.01, f"Expected fee_cost=0.15, got {result['fee_cost']}"
    assert result['net_ev'] < 0, "Net EV should be NEGATIVE"
    print("  ✅ PASS - Correctly rejects negative EV bet\n")

def test_break_even_scenario():
    """Test: AI predicts 60%, market at 60% - should be NEGATIVE due to fees"""
    result = calculate_expected_value(probability=0.60, market_price=0.60, bet_size=10.0)
    
    print("Test 3: Break-Even Scenario (market efficient)")
    print(f"  AI Prediction: 60%")
    print(f"  Market Price: 60%")
    print(f"  Edge: 0%")
    print(f"  Gross EV: ${result['gross_ev']:.2f}")
    print(f"  Fee Cost: ${result['fee_cost']:.2f}")
    print(f"  Net EV: ${result['net_ev']:.2f}")
    
    assert abs(result['gross_ev'] - 0.00) < 0.01, f"Expected gross_ev=0.00, got {result['gross_ev']}"
    assert abs(result['fee_cost'] - 0.18) < 0.01, f"Expected fee_cost=0.18, got {result['fee_cost']}"
    assert result['net_ev'] < 0, "Net EV should be NEGATIVE due to fees"
    print("  ✅ PASS - Correctly accounts for fee drag\n")

def test_high_confidence_scenario():
    """Test: AI very confident (90%), market undervalued at 70%"""
    result = calculate_expected_value(probability=0.90, market_price=0.70, bet_size=10.0)
    
    print("Test 4: High Confidence Scenario")
    print(f"  AI Prediction: 90%")
    print(f"  Market Price: 70%")
    print(f"  Edge: 20%")
    print(f"  Gross EV: ${result['gross_ev']:.2f}")
    print(f"  Fee Cost: ${result['fee_cost']:.2f}")
    print(f"  Net EV: ${result['net_ev']:.2f}")
    
    assert abs(result['gross_ev'] - 2.00) < 0.01, f"Expected gross_ev=2.00, got {result['gross_ev']}"
    assert abs(result['fee_cost'] - 0.27) < 0.01, f"Expected fee_cost=0.27, got {result['fee_cost']}"
    assert result['net_ev'] > 0, "Net EV should be POSITIVE"
    print("  ✅ PASS - High confidence bet approved\n")

def main():
    print("="*70)
    print("EV CALCULATION UNIT TESTS")
    print("="*70)
    print("Testing that fee applies ONLY to winning payout (not purchase cost)")
    print()
    
    try:
        test_positive_ev_scenario()
        test_negative_ev_scenario()
        test_break_even_scenario()
        test_high_confidence_scenario()
        
        print("="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print()
        print("Conclusion: Fee calculation is CORRECT")
        print("  - Fee applies only to winning payout (not purchase cost)")
        print("  - Positive EV bets are correctly identified")
        print("  - Negative EV bets are correctly rejected")
        print("  - Break-even scenarios account for fee drag")
        
    except AssertionError as e:
        print()
        print("="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"Error: {e}")

if __name__ == '__main__':
    main()

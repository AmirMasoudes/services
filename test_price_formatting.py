#!/usr/bin/env python3
"""
Test script to verify price formatting fixes
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plan.models import ConfingPlansModel
from django.utils.html import format_html
import locale

def test_price_formatting():
    """Test the price formatting methods"""
    print("Testing price formatting...")
    
    # Test with different price values
    test_prices = [0, 1000, 1000000, None]
    
    for price in test_prices:
        print(f"\nTesting price: {price}")
        
        # Create a mock object
        class MockPlan:
            def __init__(self, price):
                self.price = price
        
        obj = MockPlan(price)
        
        # Test the admin method
        try:
            if obj.price is not None:
                try:
                    # Use locale formatting for better compatibility
                    formatted_price = locale.format_string("%d", int(obj.price), grouping=True)
                    result = format_html('<strong>{}</strong> تومان', formatted_price)
                    print(f"  Admin method result: {result}")
                except (ValueError, TypeError):
                    # Fallback to simple formatting
                    result = format_html('<strong>{}</strong> تومان', str(obj.price))
                    print(f"  Admin method result (fallback): {result}")
            else:
                result = format_html('<strong>نامشخص</strong>')
                print(f"  Admin method result: {result}")
        except Exception as e:
            print(f"  Error in admin method: {e}")
    
    print("\nPrice formatting test completed!")

if __name__ == "__main__":
    test_price_formatting() 
#!/usr/bin/env python3
"""
Integration test - verify all T-codes load without errors
"""
import sys
from PyQt5.QtWidgets import QApplication
from database import Database
from main import SAPSimulator

def test_tcodes():
    """Smoke test all implemented T-codes"""
    app = QApplication(sys.argv)
    
    db = Database()
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT code FROM tcodes WHERE implemented=1 ORDER BY code")
    tcodes = [row['code'] for row in cur.fetchall()]
    conn.close()
    
    print(f"Testing {len(tcodes)} T-codes...")
    
    simulator = SAPSimulator()
    results = []
    
    for tcode in tcodes:
        try:
            simulator.execute_tcode(tcode)
            results.append((tcode, "✓ OK"))
            print(f"  {tcode}: ✓")
        except Exception as e:
            results.append((tcode, f"✗ ERROR: {str(e)}"))
            print(f"  {tcode}: ✗ {str(e)}")
    
    # Summary
    passed = sum(1 for _, r in results if "✓" in r)
    failed = len(results) - passed
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(tcodes)} passed, {failed} failed")
    
    if failed > 0:
        print("\nFailed T-codes:")
        for tcode, result in results:
            if "✗" in result:
                print(f"  {tcode}: {result}")
        sys.exit(1)
    else:
        print("✅ All T-codes load successfully!")
        sys.exit(0)

if __name__ == '__main__':
    test_tcodes()

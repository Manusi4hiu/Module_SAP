#!/usr/bin/env python3
"""
Test script untuk verify master data bug fix
Run: python3 test_master_data.py
"""
import sys
from database import Database

def test_database_integrity():
    """Verify database has all master data"""
    print("=== Testing Database Integrity ===")
    db = Database()
    conn = db.connect()
    cur = conn.cursor()
    
    # Test materials
    cur.execute("SELECT COUNT(*) FROM materials")
    mat_count = cur.fetchone()[0]
    print(f"✓ Materials: {mat_count} (expected: 36)")
    assert mat_count == 36, f"Material count mismatch: {mat_count}"
    
    # Test vendors
    cur.execute("SELECT COUNT(*) FROM vendors")
    ven_count = cur.fetchone()[0]
    print(f"✓ Vendors: {ven_count} (expected: 10)")
    assert ven_count == 10, f"Vendor count mismatch: {ven_count}"
    
    # Test employees
    cur.execute("SELECT COUNT(*) FROM employees")
    emp_count = cur.fetchone()[0]
    print(f"✓ Employees: {emp_count} (expected: 10)")
    assert emp_count == 10, f"Employee count mismatch: {emp_count}"
    
    # Test sample data exists
    cur.execute("SELECT material_id, description FROM materials WHERE material_id IN ('MAT1001', 'MAT1002', 'MAT1003')")
    materials = cur.fetchall()
    print(f"\n✓ Sample materials found: {len(materials)}")
    for mat in materials:
        print(f"  - {mat['material_id']}: {mat['description']}")
    
    cur.execute("SELECT vendor_id, name FROM vendors WHERE vendor_id IN ('C1001', 'C1002', 'C1003')")
    vendors = cur.fetchall()
    print(f"\n✓ Sample vendors found: {len(vendors)}")
    for ven in vendors:
        print(f"  - {ven['vendor_id']}: {ven['name']}")
    
    cur.execute("SELECT personnel_no, name, position FROM employees WHERE personnel_no IN ('100001', '100002', '100003')")
    employees = cur.fetchall()
    print(f"\n✓ Sample employees found: {len(employees)}")
    for emp in employees:
        print(f"  - {emp['personnel_no']}: {emp['name']} ({emp['position']})")
    
    conn.close()
    print("\n✅ Database integrity: PASS\n")

def test_screen_imports():
    """Verify all screen modules can be imported"""
    print("=== Testing Screen Imports ===")
    screens = [
        'screens.master_data',
        'screens.hcm_master',
        'screens.po_create',
        'screens.po_display',
        'screens.so_create',
        'screens.so_display',
        'screens.goods_receipt',
        'screens.fi_posting',
        'screens.co_cost_center',
        'screens.pp_planned_order',
        'screens.pm_work_order',
        'screens.ewm_transfer_order',
    ]
    
    for screen in screens:
        try:
            __import__(screen)
            print(f"✓ {screen}")
        except Exception as e:
            print(f"✗ {screen}: {e}")
            sys.exit(1)
    
    print("✅ All screen imports: PASS\n")

def test_database_queries():
    """Test common database queries used by screens"""
    print("=== Testing Database Queries ===")
    db = Database()
    conn = db.connect()
    cur = conn.cursor()
    
    # Query used by MM03
    cur.execute("SELECT * FROM materials ORDER BY material_id LIMIT 5")
    materials = cur.fetchall()
    print(f"✓ MM03 query returns {len(materials)} rows")
    
    # Query used by ME21N vendor lookup
    cur.execute("SELECT vendor_id, name, city FROM vendors ORDER BY vendor_id")
    vendors = cur.fetchall()
    print(f"✓ ME21N vendor query returns {len(vendors)} rows")
    
    # Query used by PA30
    cur.execute("SELECT personnel_no, name, position FROM employees ORDER BY personnel_no")
    employees = cur.fetchall()
    print(f"✓ PA30 employee query returns {len(employees)} rows")
    
    # Query used by material lookup in PO/SO
    cur.execute("SELECT material_id, description, uom FROM materials WHERE material_id = ?", ('MAT1001',))
    mat = cur.fetchone()
    assert mat is not None, "MAT1001 not found"
    print(f"✓ Material lookup: {mat['material_id']} - {mat['description']}")
    
    conn.close()
    print("✅ Database queries: PASS\n")

if __name__ == '__main__':
    try:
        test_database_integrity()
        test_screen_imports()
        test_database_queries()
        print("=" * 50)
        print("✅ ALL TESTS PASSED")
        print("=" * 50)
        print("\nMaster data fix verified locally.")
        print("Next: Download v1.0.3 binary dan verify GUI shows data.")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

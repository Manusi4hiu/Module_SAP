#!/usr/bin/env python3
"""
Quick test script to verify the app launches
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing SAP Simulator components...")

# Test database
from database import Database
db = Database()
print("✓ Database initialized")

# Test data counts
conn = db.connect()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM materials")
mat_count = cur.fetchone()[0]
print(f"✓ Materials: {mat_count}")

cur.execute("SELECT COUNT(*) FROM vendors")
vendor_count = cur.fetchone()[0]
print(f"✓ Vendors: {vendor_count}")

cur.execute("SELECT COUNT(*) FROM employees")
emp_count = cur.fetchone()[0]
print(f"✓ Employees: {emp_count}")

cur.execute("SELECT COUNT(*) FROM tcodes WHERE implemented=1")
tcode_count = cur.fetchone()[0]
print(f"✓ Implemented T-codes: {tcode_count}")

conn.close()

print("\n✅ All checks passed! Run './run.sh' to start the app")

import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path="sap_simulator.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.init_db()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_db(self):
        conn = self.connect()
        cur = conn.cursor()
        
        # T-code registry
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tcodes (
                code TEXT PRIMARY KEY,
                module TEXT NOT NULL,
                name TEXT NOT NULL,
                screen TEXT NOT NULL,
                implemented INTEGER DEFAULT 0
            )
        """)
        
        # Master data - Materials
        cur.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                material_id TEXT PRIMARY KEY,
                description TEXT,
                material_group TEXT,
                uom TEXT,
                plant TEXT,
                mrp_type TEXT,
                mrp_controller TEXT,
                reorder_point INTEGER,
                safety_stock INTEGER
            )
        """)
        
        # Master data - Vendors
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                vendor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT,
                payment_terms TEXT,
                credit_limit REAL
            )
        """)
        
        # Master data - Employees
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                personnel_no TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                emp_subgroup TEXT,
                area TEXT,
                department TEXT,
                position TEXT,
                basic_salary REAL
            )
        """)
        
        # Documents - Purchase Orders
        cur.execute("""
            CREATE TABLE IF NOT EXISTS purchase_orders (
                po_number TEXT PRIMARY KEY,
                vendor_id TEXT,
                po_date TEXT,
                company_code TEXT,
                plant TEXT,
                status TEXT DEFAULT 'Draft',
                total_value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
            )
        """)
        
        # PO Items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS po_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT,
                item_no INTEGER,
                material_id TEXT,
                quantity REAL,
                unit_price REAL,
                net_value REAL,
                FOREIGN KEY (po_number) REFERENCES purchase_orders(po_number),
                FOREIGN KEY (material_id) REFERENCES materials(material_id)
            )
        """)
        
        # User progress tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                module TEXT,
                tcode TEXT,
                completed INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                last_accessed TIMESTAMP
            )
        """)
        
        # Insert default T-codes
        tcodes = [
            ('MM01', 'MM', 'Create Material', 'material_master', 1),
            ('MM03', 'MM', 'Display Material', 'material_display', 1),
            ('ME21N', 'MM', 'Create Purchase Order', 'po_create', 1),
            ('ME23N', 'MM', 'Display Purchase Order', 'po_display', 1),
            ('MIGO', 'MM', 'Goods Receipt', 'goods_receipt', 0),
            ('PA30', 'HCM', 'Maintain HR Master Data', 'personnel_master', 1),
            ('PA20', 'HCM', 'Display HR Master Data', 'personnel_display', 1),
            ('FB01', 'FI', 'Post Document', 'fi_posting', 0),
            ('VA01', 'SD', 'Create Sales Order', 'so_create', 0),
        ]
        
        cur.executemany("""
            INSERT OR IGNORE INTO tcodes (code, module, name, screen, implemented)
            VALUES (?, ?, ?, ?, ?)
        """, tcodes)
        
        conn.commit()
        conn.close()
    
    def get_tcodes(self, module=None):
        conn = self.connect()
        cur = conn.cursor()
        if module:
            cur.execute("SELECT * FROM tcodes WHERE module = ?", (module,))
        else:
            cur.execute("SELECT * FROM tcodes ORDER BY module, code")
        results = cur.fetchall()
        conn.close()
        return results
    
    def get_tcode(self, code):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tcodes WHERE code = ?", (code,))
        result = cur.fetchone()
        conn.close()
        return result

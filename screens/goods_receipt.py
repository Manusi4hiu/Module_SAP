#!/usr/bin/env python3
"""
Goods Receipt screen (MIGO)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                             QPushButton, QGroupBox, QMessageBox, QHeaderView)
from datetime import datetime

class GoodsReceiptScreen(QWidget):
    """MIGO - Goods Receipt"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_po = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Goods Receipt (MIGO)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # PO selection
        po_layout = QHBoxLayout()
        po_layout.addWidget(QLabel("PO Number:"))
        self.po_input = QLineEdit()
        self.po_input.setPlaceholderText("PO-20260922093000")
        po_layout.addWidget(self.po_input)
        
        load_btn = QPushButton("Load PO")
        load_btn.clicked.connect(self.load_po)
        po_layout.addWidget(load_btn)
        po_layout.addStretch()
        layout.addLayout(po_layout)
        
        # PO Header info
        self.header_group = QGroupBox("PO Information")
        header_layout = QFormLayout()
        
        self.vendor_label = QLabel()
        header_layout.addRow("Vendor:", self.vendor_label)
        
        self.po_date_label = QLabel()
        header_layout.addRow("PO Date:", self.po_date_label)
        
        self.gr_date = QLineEdit()
        self.gr_date.setText(datetime.now().strftime("%Y-%m-%d"))
        header_layout.addRow("GR Date:", self.gr_date)
        
        self.header_group.setLayout(header_layout)
        self.header_group.setVisible(False)
        layout.addWidget(self.header_group)
        
        # Items section
        self.items_group = QGroupBox("Items - Enter Received Quantity")
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels([
            "Item", "Material", "PO Qty", "Received", "Pending", "GR Qty"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        items_layout.addWidget(self.items_table)
        
        self.items_group.setLayout(items_layout)
        self.items_group.setVisible(False)
        layout.addWidget(self.items_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        post_btn = QPushButton("Post (Ctrl+S)")
        post_btn.setShortcut("Ctrl+S")
        post_btn.clicked.connect(self.post_gr)
        btn_layout.addWidget(post_btn)
        
        check_btn = QPushButton("Check (F8)")
        check_btn.setShortcut("F8")
        check_btn.clicked.connect(self.check_gr)
        btn_layout.addWidget(check_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_po(self):
        po_number = self.po_input.text().strip()
        if not po_number:
            QMessageBox.warning(self, "Error", "PO Number required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Load PO header
        cur.execute("SELECT * FROM purchase_orders WHERE po_number = ?", (po_number,))
        po = cur.fetchone()
        
        if not po:
            QMessageBox.warning(self, "Not Found", f"PO {po_number} not found")
            conn.close()
            return
        
        self.current_po = po_number
        self.vendor_label.setText(po['vendor_id'])
        self.po_date_label.setText(po['po_date'])
        self.header_group.setVisible(True)
        
        # Load items with GR history
        cur.execute("SELECT * FROM po_items WHERE po_number = ? ORDER BY item_no", (po_number,))
        items = cur.fetchall()
        
        # Create GR table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS goods_receipts (
                gr_number TEXT PRIMARY KEY,
                po_number TEXT,
                gr_date TEXT,
                status TEXT DEFAULT 'Posted',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gr_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gr_number TEXT,
                po_number TEXT,
                item_no INTEGER,
                material_id TEXT,
                quantity REAL
            )
        """)
        
        conn.commit()
        
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            # Get total received
            cur.execute("""
                SELECT COALESCE(SUM(quantity), 0) as received 
                FROM gr_items 
                WHERE po_number = ? AND item_no = ?
            """, (po_number, item['item_no']))
            received = cur.fetchone()['received']
            pending = item['quantity'] - received
            
            self.items_table.setItem(i, 0, QTableWidgetItem(str(item['item_no'])))
            self.items_table.setItem(i, 1, QTableWidgetItem(item['material_id']))
            self.items_table.setItem(i, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(i, 3, QTableWidgetItem(str(received)))
            self.items_table.setItem(i, 4, QTableWidgetItem(str(pending)))
            # GR Qty editable (col 5)
            self.items_table.setItem(i, 5, QTableWidgetItem(""))
        
        conn.close()
        self.items_group.setVisible(True)
    
    def check_gr(self):
        if not self.current_po:
            QMessageBox.warning(self, "Error", "Load PO first")
            return
        
        has_gr = False
        for row in range(self.items_table.rowCount()):
            gr_qty = self.items_table.item(row, 5)
            if gr_qty and gr_qty.text().strip():
                has_gr = True
                break
        
        if not has_gr:
            QMessageBox.warning(self, "Validation", "Enter at least one GR quantity")
            return
        
        QMessageBox.information(self, "Check", "Validation OK. Press Post to create GR.")
    
    def post_gr(self):
        if not self.current_po:
            QMessageBox.warning(self, "Error", "Load PO first")
            return
        
        # Generate GR number
        gr_number = f"GR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        gr_items = []
        for row in range(self.items_table.rowCount()):
            gr_qty_item = self.items_table.item(row, 5)
            if gr_qty_item and gr_qty_item.text().strip():
                item_no = int(self.items_table.item(row, 0).text())
                material_id = self.items_table.item(row, 1).text()
                gr_qty = float(gr_qty_item.text())
                
                if gr_qty > 0:
                    gr_items.append((gr_number, self.current_po, item_no, material_id, gr_qty))
        
        if not gr_items:
            QMessageBox.warning(self, "Error", "No valid GR quantities entered")
            return
        
        # Save to DB
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            # Insert GR header
            cur.execute("""
                INSERT INTO goods_receipts (gr_number, po_number, gr_date, status)
                VALUES (?, ?, ?, ?)
            """, (gr_number, self.current_po, self.gr_date.text(), 'Posted'))
            
            # Insert GR items
            cur.executemany("""
                INSERT INTO gr_items (gr_number, po_number, item_no, material_id, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, gr_items)
            
            conn.commit()
            
            QMessageBox.information(self, "Success", 
                f"Goods Receipt {gr_number} posted successfully\nItems: {len(gr_items)}")
            
            self.clear_form()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to post GR: {str(e)}")
        finally:
            conn.close()
    
    def clear_form(self):
        self.po_input.clear()
        self.current_po = None
        self.header_group.setVisible(False)
        self.items_group.setVisible(False)
        self.items_table.setRowCount(0)

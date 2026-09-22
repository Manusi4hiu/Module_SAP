#!/usr/bin/env python3
"""
Sales Order Creation screen (VA01)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                             QPushButton, QGroupBox, QMessageBox, QHeaderView)
from datetime import datetime

class SOCreateScreen(QWidget):
    """VA01 - Create Sales Order"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Create Sales Order (VA01)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Header section
        header_group = QGroupBox("Header Data")
        header_layout = QFormLayout()
        
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("C1001")
        header_layout.addRow("Customer:", self.customer_input)
        
        self.so_date = QLineEdit()
        self.so_date.setText(datetime.now().strftime("%Y-%m-%d"))
        header_layout.addRow("Order Date:", self.so_date)
        
        self.sales_org = QLineEdit()
        self.sales_org.setText("1000")
        header_layout.addRow("Sales Org:", self.sales_org)
        
        self.dist_channel = QLineEdit()
        self.dist_channel.setText("10")
        header_layout.addRow("Dist Channel:", self.dist_channel)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Items section
        items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Item", "Material", "Quantity", "Unit Price", "Net Value"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setRowCount(10)
        
        items_layout.addWidget(self.items_table)
        
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item_row)
        items_layout.addWidget(add_btn)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save (Ctrl+S)")
        save_btn.setShortcut("Ctrl+S")
        save_btn.clicked.connect(self.save_so)
        btn_layout.addWidget(save_btn)
        
        check_btn = QPushButton("Check (F8)")
        check_btn.setShortcut("F8")
        check_btn.clicked.connect(self.check_so)
        btn_layout.addWidget(check_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
    
    def check_so(self):
        customer = self.customer_input.text().strip()
        if not customer:
            QMessageBox.warning(self, "Validation", "Customer harus diisi")
            return
        
        has_items = False
        for row in range(self.items_table.rowCount()):
            material = self.items_table.item(row, 1)
            if material and material.text().strip():
                has_items = True
                break
        
        if not has_items:
            QMessageBox.warning(self, "Validation", "Minimal 1 item harus diisi")
            return
        
        QMessageBox.information(self, "Check", "Validation OK. Press Save to create Sales Order.")
    
    def save_so(self):
        customer = self.customer_input.text().strip()
        
        if not customer:
            QMessageBox.critical(self, "Error VA 020", "Customer is required\nEnter customer number")
            return
        
        # Generate SO number
        so_number = f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate total
        total = 0.0
        items = []
        item_no = 10
        
        for row in range(self.items_table.rowCount()):
            material = self.items_table.item(row, 1)
            qty_item = self.items_table.item(row, 2)
            price_item = self.items_table.item(row, 3)
            
            if material and material.text().strip():
                material_id = material.text().strip()
                qty = float(qty_item.text() if qty_item and qty_item.text() else 0)
                price = float(price_item.text() if price_item and price_item.text() else 0)
                net = qty * price
                
                items.append((so_number, item_no, material_id, qty, price, net))
                total += net
                item_no += 10
        
        if not items:
            QMessageBox.warning(self, "Error", "Tidak ada item yang valid")
            return
        
        # Save to DB
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            # Create sales_orders table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales_orders (
                    so_number TEXT PRIMARY KEY,
                    customer_id TEXT,
                    so_date TEXT,
                    sales_org TEXT,
                    dist_channel TEXT,
                    status TEXT DEFAULT 'Saved',
                    total_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS so_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    so_number TEXT,
                    item_no INTEGER,
                    material_id TEXT,
                    quantity REAL,
                    unit_price REAL,
                    net_value REAL
                )
            """)
            
            # Insert SO header
            cur.execute("""
                INSERT INTO sales_orders 
                (so_number, customer_id, so_date, sales_org, dist_channel, status, total_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (so_number, customer, self.so_date.text(), self.sales_org.text(),
                  self.dist_channel.text(), 'Saved', total))
            
            # Insert items
            cur.executemany("""
                INSERT INTO so_items 
                (so_number, item_no, material_id, quantity, unit_price, net_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, items)
            
            conn.commit()
            
            QMessageBox.information(self, "Success", 
                f"Sales Order {so_number} created successfully\nTotal: {total:,.2f}")
            
            self.clear_form()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to save SO: {str(e)}")
        finally:
            conn.close()
    
    def clear_form(self):
        self.customer_input.clear()
        self.items_table.setRowCount(0)
        self.items_table.setRowCount(10)

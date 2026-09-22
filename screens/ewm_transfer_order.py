#!/usr/bin/env python3
"""
EWM Transfer Order Management (LT01)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
                             QHeaderView, QComboBox)
from datetime import datetime

class TransferOrderScreen(QWidget):
    """LT01 - Transfer Order CRUD"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Transfer Order Management (LT01)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        toolbar = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_order)
        toolbar.addWidget(create_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "TO Number", "Material", "From Bin", "To Bin", "Quantity", "Status", "Warehouse"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_order)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transfer_orders (
                to_number TEXT PRIMARY KEY,
                material_id TEXT,
                from_bin TEXT,
                to_bin TEXT,
                quantity REAL,
                status TEXT DEFAULT 'Open',
                warehouse TEXT
            )
        """)
        conn.commit()
        
        cur.execute("SELECT * FROM transfer_orders ORDER BY to_number")
        orders = cur.fetchall()
        conn.close()
        
        self.table.setRowCount(len(orders))
        for i, order in enumerate(orders):
            for j, val in enumerate(order):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
    
    def create_order(self):
        dialog = TransferOrderDialog(self.db, None)
        if dialog.exec_():
            self.load_data()
    
    def edit_order(self):
        row = self.table.currentRow()
        if row >= 0:
            to_number = self.table.item(row, 0).text()
            dialog = TransferOrderDialog(self.db, to_number)
            if dialog.exec_():
                self.load_data()

class TransferOrderDialog(QDialog):
    def __init__(self, db, to_number=None):
        super().__init__()
        self.db = db
        self.to_number = to_number
        self.init_ui()
        if to_number:
            self.load_order()
    
    def init_ui(self):
        self.setWindowTitle("Transfer Order")
        layout = QFormLayout()
        
        self.to_input = QLineEdit()
        if not self.to_number:
            self.to_input.setText(f"TO-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.to_input.setReadOnly(bool(self.to_number))
        layout.addRow("TO Number:", self.to_input)
        
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("MAT1001")
        layout.addRow("Material:", self.material_input)
        
        self.from_bin = QLineEdit()
        self.from_bin.setPlaceholderText("A-01-01")
        layout.addRow("From Bin:", self.from_bin)
        
        self.to_bin = QLineEdit()
        self.to_bin.setPlaceholderText("B-02-03")
        layout.addRow("To Bin:", self.to_bin)
        
        self.qty_input = QLineEdit()
        layout.addRow("Quantity:", self.qty_input)
        
        self.warehouse = QLineEdit()
        self.warehouse.setText("WH01")
        layout.addRow("Warehouse:", self.warehouse)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_order(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM transfer_orders WHERE to_number = ?", (self.to_number,))
        order = cur.fetchone()
        conn.close()
        
        if order:
            self.to_input.setText(order['to_number'])
            self.material_input.setText(order['material_id'] or "")
            self.from_bin.setText(order['from_bin'] or "")
            self.to_bin.setText(order['to_bin'] or "")
            self.qty_input.setText(str(order['quantity'] or ""))
            self.warehouse.setText(order['warehouse'] or "")
    
    def save(self):
        to_number = self.to_input.text().strip()
        material = self.material_input.text().strip()
        from_bin = self.from_bin.text().strip()
        to_bin = self.to_bin.text().strip()
        
        if not to_number:
            QMessageBox.critical(self, "Error LT 001", "TO number required")
            return
        
        if not material:
            QMessageBox.critical(self, "Error LT 002", "Material required")
            return
        
        if not from_bin or not to_bin:
            QMessageBox.critical(self, "Error LT 003", "Source and destination bins required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT OR REPLACE INTO transfer_orders 
                (to_number, material_id, from_bin, to_bin, quantity, status, warehouse)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                to_number,
                material,
                from_bin,
                to_bin,
                float(self.qty_input.text() or 0),
                'Open',
                self.warehouse.text()
            ))
            conn.commit()
            QMessageBox.information(self, "Success", f"Transfer Order {to_number} created")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            conn.close()

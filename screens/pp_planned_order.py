#!/usr/bin/env python3
"""
PP Planned Order Management (MD61)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
                             QHeaderView)
from datetime import datetime

class PlannedOrderScreen(QWidget):
    """MD61 - Planned Order CRUD"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Planned Order Management (MD61)")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Order No", "Material", "Quantity", "Start Date", "Plant", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_order)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS planned_orders (
                order_no TEXT PRIMARY KEY,
                material_id TEXT NOT NULL,
                quantity REAL,
                start_date TEXT,
                plant TEXT,
                status TEXT DEFAULT 'Planned'
            )
        """)
        conn.commit()
        
        cur.execute("SELECT * FROM planned_orders ORDER BY order_no")
        orders = cur.fetchall()
        conn.close()
        
        self.table.setRowCount(len(orders))
        for i, order in enumerate(orders):
            for j, val in enumerate(order):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
    
    def create_order(self):
        dialog = PlannedOrderDialog(self.db, None)
        if dialog.exec_():
            self.load_data()
    
    def edit_order(self):
        row = self.table.currentRow()
        if row >= 0:
            order_no = self.table.item(row, 0).text()
            dialog = PlannedOrderDialog(self.db, order_no)
            if dialog.exec_():
                self.load_data()

class PlannedOrderDialog(QDialog):
    def __init__(self, db, order_no=None):
        super().__init__()
        self.db = db
        self.order_no = order_no
        self.init_ui()
        if order_no:
            self.load_order()
    
    def init_ui(self):
        self.setWindowTitle("Planned Order")
        layout = QFormLayout()
        
        self.order_input = QLineEdit()
        if not self.order_no:
            self.order_input.setText(f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.order_input.setReadOnly(bool(self.order_no))
        layout.addRow("Order No:", self.order_input)
        
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("MAT1001")
        layout.addRow("Material:", self.material_input)
        
        self.qty_input = QLineEdit()
        layout.addRow("Quantity:", self.qty_input)
        
        self.start_date = QLineEdit()
        self.start_date.setText(datetime.now().strftime("%Y-%m-%d"))
        layout.addRow("Start Date:", self.start_date)
        
        self.plant_input = QLineEdit()
        self.plant_input.setText("JKT1")
        layout.addRow("Plant:", self.plant_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_order(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM planned_orders WHERE order_no = ?", (self.order_no,))
        order = cur.fetchone()
        conn.close()
        
        if order:
            self.order_input.setText(order['order_no'])
            self.material_input.setText(order['material_id'] or "")
            self.qty_input.setText(str(order['quantity'] or ""))
            self.start_date.setText(order['start_date'] or "")
            self.plant_input.setText(order['plant'] or "")
    
    def save(self):
        order_no = self.order_input.text().strip()
        material = self.material_input.text().strip()
        
        if not order_no:
            QMessageBox.critical(self, "Error PP 001", "Order number required")
            return
        
        if not material:
            QMessageBox.critical(self, "Error PP 002", "Material required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT OR REPLACE INTO planned_orders 
                (order_no, material_id, quantity, start_date, plant, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_no,
                material,
                float(self.qty_input.text() or 0),
                self.start_date.text(),
                self.plant_input.text(),
                'Planned'
            ))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            conn.close()

#!/usr/bin/env python3
"""
PM Work Order Management (IW31)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
                             QHeaderView, QComboBox)
from datetime import datetime

class WorkOrderScreen(QWidget):
    """IW31 - Work Order CRUD"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Work Order Management (IW31)")
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
            "Order No", "Equipment", "Description", "Priority", "Status", "Start Date", "Plant"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_order)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS work_orders (
                order_no TEXT PRIMARY KEY,
                equipment TEXT,
                description TEXT,
                priority TEXT,
                status TEXT DEFAULT 'Created',
                start_date TEXT,
                plant TEXT
            )
        """)
        conn.commit()
        
        cur.execute("SELECT * FROM work_orders ORDER BY order_no")
        orders = cur.fetchall()
        conn.close()
        
        self.table.setRowCount(len(orders))
        for i, order in enumerate(orders):
            for j, val in enumerate(order):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
    
    def create_order(self):
        dialog = WorkOrderDialog(self.db, None)
        if dialog.exec_():
            self.load_data()
    
    def edit_order(self):
        row = self.table.currentRow()
        if row >= 0:
            order_no = self.table.item(row, 0).text()
            dialog = WorkOrderDialog(self.db, order_no)
            if dialog.exec_():
                self.load_data()

class WorkOrderDialog(QDialog):
    def __init__(self, db, order_no=None):
        super().__init__()
        self.db = db
        self.order_no = order_no
        self.init_ui()
        if order_no:
            self.load_order()
    
    def init_ui(self):
        self.setWindowTitle("Work Order")
        layout = QFormLayout()
        
        self.order_input = QLineEdit()
        if not self.order_no:
            self.order_input.setText(f"WO-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.order_input.setReadOnly(bool(self.order_no))
        layout.addRow("Order No:", self.order_input)
        
        self.equipment_input = QLineEdit()
        self.equipment_input.setPlaceholderText("EQP-001")
        layout.addRow("Equipment:", self.equipment_input)
        
        self.desc_input = QLineEdit()
        layout.addRow("Description:", self.desc_input)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Urgent"])
        self.priority_combo.setCurrentIndex(1)
        layout.addRow("Priority:", self.priority_combo)
        
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
        cur.execute("SELECT * FROM work_orders WHERE order_no = ?", (self.order_no,))
        order = cur.fetchone()
        conn.close()
        
        if order:
            self.order_input.setText(order['order_no'])
            self.equipment_input.setText(order['equipment'] or "")
            self.desc_input.setText(order['description'] or "")
            idx = self.priority_combo.findText(order['priority'] or "Medium")
            if idx >= 0:
                self.priority_combo.setCurrentIndex(idx)
            self.start_date.setText(order['start_date'] or "")
            self.plant_input.setText(order['plant'] or "")
    
    def save(self):
        order_no = self.order_input.text().strip()
        if not order_no:
            QMessageBox.critical(self, "Error PM 001", "Order number required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT OR REPLACE INTO work_orders 
                (order_no, equipment, description, priority, status, start_date, plant)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                order_no,
                self.equipment_input.text(),
                self.desc_input.text(),
                self.priority_combo.currentText(),
                'Created',
                self.start_date.text(),
                self.plant_input.text()
            ))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            conn.close()

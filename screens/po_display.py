#!/usr/bin/env python3
"""
Purchase Order Display screen (ME23N)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QGroupBox, QFormLayout, QMessageBox, QHeaderView)

class PODisplayScreen(QWidget):
    """ME23N - Display Purchase Order"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Display Purchase Order (ME23N)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("PO Number:"))
        self.po_input = QLineEdit()
        self.po_input.setPlaceholderText("PO-20260922093000")
        search_layout.addWidget(self.po_input)
        
        search_btn = QPushButton("Display")
        search_btn.clicked.connect(self.load_po)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Header section
        self.header_group = QGroupBox("Header Data")
        header_layout = QFormLayout()
        
        self.vendor_label = QLabel()
        header_layout.addRow("Vendor:", self.vendor_label)
        
        self.po_date_label = QLabel()
        header_layout.addRow("PO Date:", self.po_date_label)
        
        self.company_label = QLabel()
        header_layout.addRow("Company Code:", self.company_label)
        
        self.plant_label = QLabel()
        header_layout.addRow("Plant:", self.plant_label)
        
        self.status_label = QLabel()
        header_layout.addRow("Status:", self.status_label)
        
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-weight: bold;")
        header_layout.addRow("Total Value:", self.total_label)
        
        self.header_group.setLayout(header_layout)
        self.header_group.setVisible(False)
        layout.addWidget(self.header_group)
        
        # Items section
        self.items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Item", "Material", "Quantity", "Unit Price", "Net Value"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        items_layout.addWidget(self.items_table)
        
        self.items_group.setLayout(items_layout)
        self.items_group.setVisible(False)
        layout.addWidget(self.items_group)
        
        self.setLayout(layout)
    
    def load_po(self):
        po_number = self.po_input.text().strip()
        if not po_number:
            QMessageBox.warning(self, "Error", "PO Number required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Load header
        cur.execute("SELECT * FROM purchase_orders WHERE po_number = ?", (po_number,))
        po = cur.fetchone()
        
        if not po:
            QMessageBox.warning(self, "Not Found", f"PO {po_number} not found")
            conn.close()
            return
        
        # Display header
        self.vendor_label.setText(po['vendor_id'])
        self.po_date_label.setText(po['po_date'])
        self.company_label.setText(po['company_code'])
        self.plant_label.setText(po['plant'])
        self.status_label.setText(po['status'])
        self.total_label.setText(f"{po['total_value']:,.2f}")
        self.header_group.setVisible(True)
        
        # Load items
        cur.execute("SELECT * FROM po_items WHERE po_number = ? ORDER BY item_no", (po_number,))
        items = cur.fetchall()
        conn.close()
        
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(str(item['item_no'])))
            self.items_table.setItem(i, 1, QTableWidgetItem(item['material_id']))
            self.items_table.setItem(i, 2, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(i, 3, QTableWidgetItem(f"{item['unit_price']:,.2f}"))
            self.items_table.setItem(i, 4, QTableWidgetItem(f"{item['net_value']:,.2f}"))
        
        self.items_group.setVisible(True)

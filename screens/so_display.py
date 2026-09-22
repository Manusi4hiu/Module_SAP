#!/usr/bin/env python3
"""
Sales Order Display screen (VA03)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QGroupBox, QFormLayout, QMessageBox, QHeaderView)

class SODisplayScreen(QWidget):
    """VA03 - Display Sales Order"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Display Sales Order (VA03)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Search section
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("SO Number:"))
        self.so_input = QLineEdit()
        self.so_input.setPlaceholderText("SO-20260922093000")
        search_layout.addWidget(self.so_input)
        
        search_btn = QPushButton("Display")
        search_btn.clicked.connect(self.load_so)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Header section
        self.header_group = QGroupBox("Header Data")
        header_layout = QFormLayout()
        
        self.customer_label = QLabel()
        header_layout.addRow("Customer:", self.customer_label)
        
        self.so_date_label = QLabel()
        header_layout.addRow("Order Date:", self.so_date_label)
        
        self.sales_org_label = QLabel()
        header_layout.addRow("Sales Org:", self.sales_org_label)
        
        self.dist_channel_label = QLabel()
        header_layout.addRow("Dist Channel:", self.dist_channel_label)
        
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
    
    def load_so(self):
        so_number = self.so_input.text().strip()
        if not so_number:
            QMessageBox.warning(self, "Error", "SO Number required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Load header
        cur.execute("SELECT * FROM sales_orders WHERE so_number = ?", (so_number,))
        so = cur.fetchone()
        
        if not so:
            QMessageBox.warning(self, "Not Found", f"SO {so_number} not found")
            conn.close()
            return
        
        # Display header
        self.customer_label.setText(so['customer_id'])
        self.so_date_label.setText(so['so_date'])
        self.sales_org_label.setText(so['sales_org'])
        self.dist_channel_label.setText(so['dist_channel'])
        self.status_label.setText(so['status'])
        self.total_label.setText(f"{so['total_value']:,.2f}")
        self.header_group.setVisible(True)
        
        # Load items
        cur.execute("SELECT * FROM so_items WHERE so_number = ? ORDER BY item_no", (so_number,))
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

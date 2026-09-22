from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                             QPushButton, QGroupBox, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from datetime import datetime

class POCreateScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.po_items = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create Purchase Order (ME21N)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Header section
        header_group = QGroupBox("Header Data")
        header_layout = QFormLayout()
        
        self.vendor_input = QLineEdit()
        self.vendor_input.setPlaceholderText("C1001")
        header_layout.addRow("Vendor:", self.vendor_input)
        
        self.po_date = QLineEdit()
        self.po_date.setText(datetime.now().strftime("%Y-%m-%d"))
        header_layout.addRow("PO Date:", self.po_date)
        
        self.company_code = QLineEdit()
        self.company_code.setText("1000")
        header_layout.addRow("Company Code:", self.company_code)
        
        self.plant = QLineEdit()
        self.plant.setText("JKT1")
        header_layout.addRow("Plant:", self.plant)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Items section
        items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()
        
        # Table for items
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Item", "Material", "Quantity", "Unit Price", "Net Value"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setRowCount(10)  # ponytail: fixed rows, add dynamic when needed
        
        items_layout.addWidget(self.items_table)
        
        # Add row button
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item_row)
        items_layout.addWidget(add_btn)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save (Ctrl+S)")
        save_btn.setShortcut("Ctrl+S")
        save_btn.clicked.connect(self.save_po)
        btn_layout.addWidget(save_btn)
        
        check_btn = QPushButton("Check (F8)")
        check_btn.setShortcut("F8")
        check_btn.clicked.connect(self.check_po)
        btn_layout.addWidget(check_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
    
    def check_po(self):
        """Validate PO before save"""
        vendor = self.vendor_input.text().strip()
        if not vendor:
            QMessageBox.warning(self, "Validation", "Vendor harus diisi")
            return
        
        # Check if items exist
        has_items = False
        for row in range(self.items_table.rowCount()):
            material = self.items_table.item(row, 1)
            if material and material.text().strip():
                has_items = True
                break
        
        if not has_items:
            QMessageBox.warning(self, "Validation", "Minimal 1 item harus diisi")
            return
        
        QMessageBox.information(self, "Check", "Validation OK. Press Save to create PO.")
    
    def save_po(self):
        """Save PO to database"""
        vendor = self.vendor_input.text().strip()
        
        if not vendor:
            QMessageBox.critical(self, "Error ME 022", "Vendor is required\nEnter vendor number")
            return
        
        # Generate PO number
        po_number = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
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
                
                items.append((po_number, item_no, material_id, qty, price, net))
                total += net
                item_no += 10
        
        if not items:
            QMessageBox.critical(self, "Error ME 023", "No valid line items\nEnter at least one item")
            return
        
        # Save to DB
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            # Insert PO header
            cur.execute("""
                INSERT INTO purchase_orders 
                (po_number, vendor_id, po_date, company_code, plant, status, total_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (po_number, vendor, self.po_date.text(), self.company_code.text(),
                  self.plant.text(), 'Saved', total))
            
            # Insert items
            cur.executemany("""
                INSERT INTO po_items 
                (po_number, item_no, material_id, quantity, unit_price, net_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, items)
            
            conn.commit()
            
            QMessageBox.information(self, "Success", 
                f"Purchase Order {po_number} created successfully\nTotal: {total:,.2f}")
            
            self.clear_form()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to save PO: {str(e)}")
        finally:
            conn.close()
    
    def clear_form(self):
        self.vendor_input.clear()
        self.items_table.setRowCount(0)
        self.items_table.setRowCount(10)

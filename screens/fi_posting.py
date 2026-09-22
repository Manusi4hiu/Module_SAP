#!/usr/bin/env python3
"""
FI Document Posting screen (FB01)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                             QPushButton, QGroupBox, QMessageBox, QHeaderView)
from datetime import datetime

class FIPostingScreen(QWidget):
    """FB01 - Post FI Document"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Post Document (FB01)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Header section
        header_group = QGroupBox("Document Header")
        header_layout = QFormLayout()
        
        self.doc_date = QLineEdit()
        self.doc_date.setText(datetime.now().strftime("%Y-%m-%d"))
        header_layout.addRow("Document Date:", self.doc_date)
        
        self.posting_date = QLineEdit()
        self.posting_date.setText(datetime.now().strftime("%Y-%m-%d"))
        header_layout.addRow("Posting Date:", self.posting_date)
        
        self.company_code = QLineEdit()
        self.company_code.setText("1000")
        header_layout.addRow("Company Code:", self.company_code)
        
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Reference text")
        header_layout.addRow("Reference:", self.reference)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Line items section
        items_group = QGroupBox("Line Items (Must Balance)")
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([
            "GL Account", "Debit", "Credit", "Text"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setRowCount(10)
        items_layout.addWidget(self.items_table)
        
        add_btn = QPushButton("Add Line")
        add_btn.clicked.connect(self.add_line)
        items_layout.addWidget(add_btn)
        
        # Balance display
        balance_layout = QHBoxLayout()
        balance_layout.addWidget(QLabel("Total Debit:"))
        self.debit_total = QLabel("0.00")
        self.debit_total.setStyleSheet("font-weight: bold;")
        balance_layout.addWidget(self.debit_total)
        
        balance_layout.addWidget(QLabel("Total Credit:"))
        self.credit_total = QLabel("0.00")
        self.credit_total.setStyleSheet("font-weight: bold;")
        balance_layout.addWidget(self.credit_total)
        
        balance_layout.addWidget(QLabel("Balance:"))
        self.balance_label = QLabel("0.00")
        balance_layout.addWidget(self.balance_label)
        balance_layout.addStretch()
        items_layout.addLayout(balance_layout)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        calc_btn = QPushButton("Calculate (F8)")
        calc_btn.setShortcut("F8")
        calc_btn.clicked.connect(self.calculate_balance)
        btn_layout.addWidget(calc_btn)
        
        post_btn = QPushButton("Post (Ctrl+S)")
        post_btn.setShortcut("Ctrl+S")
        post_btn.clicked.connect(self.post_document)
        btn_layout.addWidget(post_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_line(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
    
    def calculate_balance(self):
        """F8 - Calculate totals and balance"""
        debit_sum = 0.0
        credit_sum = 0.0
        
        for row in range(self.items_table.rowCount()):
            debit_item = self.items_table.item(row, 1)
            credit_item = self.items_table.item(row, 2)
            
            if debit_item and debit_item.text():
                try:
                    debit_sum += float(debit_item.text())
                except ValueError:
                    pass
            
            if credit_item and credit_item.text():
                try:
                    credit_sum += float(credit_item.text())
                except ValueError:
                    pass
        
        balance = debit_sum - credit_sum
        
        self.debit_total.setText(f"{debit_sum:,.2f}")
        self.credit_total.setText(f"{credit_sum:,.2f}")
        self.balance_label.setText(f"{balance:,.2f}")
        
        # Color code balance
        if abs(balance) < 0.01:  # Balanced
            self.balance_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.balance_label.setStyleSheet("font-weight: bold; color: red;")
    
    def post_document(self):
        """Post FI document after validation"""
        # Calculate first
        self.calculate_balance()
        
        # Validation
        debit_sum = float(self.debit_total.text().replace(',', ''))
        credit_sum = float(self.credit_total.text().replace(',', ''))
        balance = abs(debit_sum - credit_sum)
        
        if balance > 0.01:
            QMessageBox.critical(self, "Error F5 001", 
                f"Document not balanced\nBalance difference: {balance:,.2f}\nDebit and credit must be equal")
            return
        
        if debit_sum == 0:
            QMessageBox.warning(self, "Error F5 002", "No line items entered")
            return
        
        # Collect line items
        lines = []
        for row in range(self.items_table.rowCount()):
            gl_item = self.items_table.item(row, 0)
            debit_item = self.items_table.item(row, 1)
            credit_item = self.items_table.item(row, 2)
            text_item = self.items_table.item(row, 3)
            
            if gl_item and gl_item.text().strip():
                gl_account = gl_item.text().strip()
                debit = float(debit_item.text()) if debit_item and debit_item.text() else 0.0
                credit = float(credit_item.text()) if credit_item and credit_item.text() else 0.0
                text = text_item.text() if text_item else ""
                
                if debit > 0 or credit > 0:
                    lines.append((gl_account, debit, credit, text))
        
        if len(lines) < 2:
            QMessageBox.warning(self, "Error F5 003", "Minimum 2 line items required")
            return
        
        # Generate doc number
        doc_number = f"FI-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save to DB
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            # Create tables
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fi_documents (
                    doc_number TEXT PRIMARY KEY,
                    doc_date TEXT,
                    posting_date TEXT,
                    company_code TEXT,
                    reference TEXT,
                    status TEXT DEFAULT 'Posted',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fi_line_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_number TEXT,
                    line_no INTEGER,
                    gl_account TEXT,
                    debit REAL,
                    credit REAL,
                    text TEXT
                )
            """)
            
            # Insert document
            cur.execute("""
                INSERT INTO fi_documents 
                (doc_number, doc_date, posting_date, company_code, reference, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_number, self.doc_date.text(), self.posting_date.text(),
                  self.company_code.text(), self.reference.text(), 'Posted'))
            
            # Insert line items
            for i, (gl, debit, credit, text) in enumerate(lines, 1):
                cur.execute("""
                    INSERT INTO fi_line_items 
                    (doc_number, line_no, gl_account, debit, credit, text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_number, i, gl, debit, credit, text))
            
            conn.commit()
            
            QMessageBox.information(self, "Success", 
                f"Document {doc_number} posted successfully\n" +
                f"Total: {debit_sum:,.2f}\n" +
                f"Lines: {len(lines)}")
            
            self.clear_form()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Failed to post document: {str(e)}")
        finally:
            conn.close()
    
    def clear_form(self):
        self.reference.clear()
        self.items_table.setRowCount(0)
        self.items_table.setRowCount(10)
        self.debit_total.setText("0.00")
        self.credit_total.setText("0.00")
        self.balance_label.setText("0.00")
        self.balance_label.setStyleSheet("font-weight: bold;")

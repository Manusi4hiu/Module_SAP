#!/usr/bin/env python3
"""
CO Cost Center Management (KS01)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
                             QHeaderView)

class CostCenterScreen(QWidget):
    """KS01 - Cost Center CRUD"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Cost Center Management (KS01)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        toolbar = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_cost_center)
        toolbar.addWidget(create_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Cost Center", "Name", "Controlling Area", "Department", "Budget"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_cost_center)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cost_centers (
                cost_center TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                controlling_area TEXT,
                department TEXT,
                budget REAL
            )
        """)
        conn.commit()
        
        cur.execute("SELECT * FROM cost_centers ORDER BY cost_center")
        cost_centers = cur.fetchall()
        conn.close()
        
        self.table.setRowCount(len(cost_centers))
        for i, cc in enumerate(cost_centers):
            for j, val in enumerate(cc):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
    
    def create_cost_center(self):
        dialog = CostCenterDialog(self.db, None)
        if dialog.exec_():
            self.load_data()
    
    def edit_cost_center(self):
        row = self.table.currentRow()
        if row >= 0:
            cc_id = self.table.item(row, 0).text()
            dialog = CostCenterDialog(self.db, cc_id)
            if dialog.exec_():
                self.load_data()

class CostCenterDialog(QDialog):
    def __init__(self, db, cc_id=None):
        super().__init__()
        self.db = db
        self.cc_id = cc_id
        self.init_ui()
        if cc_id:
            self.load_cost_center()
    
    def init_ui(self):
        self.setWindowTitle("Cost Center")
        layout = QFormLayout()
        
        self.cc_input = QLineEdit()
        self.cc_input.setReadOnly(bool(self.cc_id))
        layout.addRow("Cost Center:", self.cc_input)
        
        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        
        self.area_input = QLineEdit()
        self.area_input.setText("1000")
        layout.addRow("Controlling Area:", self.area_input)
        
        self.dept_input = QLineEdit()
        layout.addRow("Department:", self.dept_input)
        
        self.budget_input = QLineEdit()
        layout.addRow("Budget:", self.budget_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_cost_center(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM cost_centers WHERE cost_center = ?", (self.cc_id,))
        cc = cur.fetchone()
        conn.close()
        
        if cc:
            self.cc_input.setText(cc['cost_center'])
            self.name_input.setText(cc['name'] or "")
            self.area_input.setText(cc['controlling_area'] or "")
            self.dept_input.setText(cc['department'] or "")
            self.budget_input.setText(str(cc['budget'] or ""))
    
    def save(self):
        cc_id = self.cc_input.text().strip()
        if not cc_id:
            QMessageBox.critical(self, "Error CO 001", "Cost Center required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT OR REPLACE INTO cost_centers 
                (cost_center, name, controlling_area, department, budget)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cc_id,
                self.name_input.text(),
                self.area_input.text(),
                self.dept_input.text(),
                float(self.budget_input.text() or 0)
            ))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            conn.close()

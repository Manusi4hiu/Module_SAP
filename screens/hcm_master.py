#!/usr/bin/env python3
"""
HCM Master Data screens (PA30, PA20)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt

class EmployeeMasterScreen(QWidget):
    """PA30 - Employee Master maintenance"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Maintain HR Master Data (PA30)")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_employee)
        toolbar.addWidget(create_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Personnel No", "Name", "Emp Subgroup", "Area", 
            "Department", "Position", "Basic Salary"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_employee)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employees ORDER BY personnel_no")
        employees = cur.fetchall()
        conn.close()
        
        self.table.setRowCount(len(employees))
        for i, emp in enumerate(employees):
            for j, val in enumerate(emp):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
    
    def create_employee(self):
        dialog = EmployeeDialog(self.db, None)
        if dialog.exec_():
            self.load_data()
    
    def edit_employee(self):
        row = self.table.currentRow()
        if row >= 0:
            personnel_no = self.table.item(row, 0).text()
            dialog = EmployeeDialog(self.db, personnel_no)
            if dialog.exec_():
                self.load_data()

class EmployeeDialog(QDialog):
    def __init__(self, db, personnel_no=None):
        super().__init__()
        self.db = db
        self.personnel_no = personnel_no
        self.init_ui()
        if personnel_no:
            self.load_employee()
    
    def init_ui(self):
        self.setWindowTitle("Employee Master Data")
        layout = QFormLayout()
        
        self.personnel_input = QLineEdit()
        self.personnel_input.setReadOnly(bool(self.personnel_no))
        layout.addRow("Personnel No:", self.personnel_input)
        
        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        
        self.subgroup_input = QLineEdit()
        layout.addRow("Emp Subgroup:", self.subgroup_input)
        
        self.area_input = QLineEdit()
        layout.addRow("Area:", self.area_input)
        
        self.dept_input = QLineEdit()
        layout.addRow("Department:", self.dept_input)
        
        self.position_input = QLineEdit()
        layout.addRow("Position:", self.position_input)
        
        self.salary_input = QLineEdit()
        layout.addRow("Basic Salary:", self.salary_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_employee(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employees WHERE personnel_no = ?", (self.personnel_no,))
        emp = cur.fetchone()
        conn.close()
        
        if emp:
            self.personnel_input.setText(emp['personnel_no'])
            self.name_input.setText(emp['name'] or "")
            self.subgroup_input.setText(emp['emp_subgroup'] or "")
            self.area_input.setText(emp['area'] or "")
            self.dept_input.setText(emp['department'] or "")
            self.position_input.setText(emp['position'] or "")
            self.salary_input.setText(str(emp['basic_salary'] or ""))
    
    def save(self):
        personnel_no = self.personnel_input.text().strip()
        if not personnel_no:
            QMessageBox.warning(self, "Error", "Personnel No required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT OR REPLACE INTO employees 
                (personnel_no, name, emp_subgroup, area, department, position, basic_salary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                personnel_no,
                self.name_input.text(),
                self.subgroup_input.text(),
                self.area_input.text(),
                self.dept_input.text(),
                self.position_input.text(),
                float(self.salary_input.text() or 0)
            ))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            conn.close()

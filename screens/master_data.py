#!/usr/bin/env python3
"""
Master Data CRUD screens
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt

class MaterialMasterScreen(QWidget):
    """MM01/MM03 - Material Master maintenance/display"""
    def __init__(self, db, readonly=False):
        super().__init__()
        self.db = db
        self.readonly = readonly
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_text = "Material Master (MM03 - Display)" if self.readonly else "Material Master (MM01)"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Toolbar
        if not self.readonly:
            toolbar = QHBoxLayout()
            create_btn = QPushButton("Create")
            create_btn.clicked.connect(self.create_material)
            toolbar.addWidget(create_btn)
            
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.load_data)
            toolbar.addWidget(refresh_btn)
            toolbar.addStretch()
            layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Material", "Description", "Mat Group", "UoM", "Plant",
            "MRP Type", "MRP Ctrl", "Reorder Pt", "Safety Stock"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self.edit_material)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM materials ORDER BY material_id")
        materials = cur.fetchall()
        conn.close()
        
        self.table.setRowCount(len(materials))
        for i, mat in enumerate(materials):
            for j, val in enumerate(mat):
                self.table.setItem(i, j, QTableWidgetItem(str(val) if val else ""))
    
    def create_material(self):
        dialog = MaterialDialog(self.db, None)
        if dialog.exec_():
            self.load_data()
    
    def edit_material(self):
        if self.readonly:
            return  # ponytail: no-op in display mode
        row = self.table.currentRow()
        if row >= 0:
            material_id = self.table.item(row, 0).text()
            dialog = MaterialDialog(self.db, material_id)
            if dialog.exec_():
                self.load_data()

class MaterialDialog(QDialog):
    def __init__(self, db, material_id=None):
        super().__init__()
        self.db = db
        self.material_id = material_id
        self.init_ui()
        if material_id:
            self.load_material()
    
    def init_ui(self):
        self.setWindowTitle("Material Master")
        layout = QFormLayout()
        
        self.material_input = QLineEdit()
        self.material_input.setReadOnly(bool(self.material_id))
        layout.addRow("Material:", self.material_input)
        
        self.desc_input = QLineEdit()
        layout.addRow("Description:", self.desc_input)
        
        self.matgroup_input = QLineEdit()
        layout.addRow("Material Group:", self.matgroup_input)
        
        self.uom_input = QLineEdit()
        layout.addRow("UoM:", self.uom_input)
        
        self.plant_input = QLineEdit()
        layout.addRow("Plant:", self.plant_input)
        
        self.mrp_type_input = QLineEdit()
        layout.addRow("MRP Type:", self.mrp_type_input)
        
        self.mrp_ctrl_input = QLineEdit()
        layout.addRow("MRP Controller:", self.mrp_ctrl_input)
        
        self.reorder_input = QLineEdit()
        layout.addRow("Reorder Point:", self.reorder_input)
        
        self.safety_input = QLineEdit()
        layout.addRow("Safety Stock:", self.safety_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_material(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM materials WHERE material_id = ?", (self.material_id,))
        mat = cur.fetchone()
        conn.close()
        
        if mat:
            self.material_input.setText(mat['material_id'])
            self.desc_input.setText(mat['description'] or "")
            self.matgroup_input.setText(mat['material_group'] or "")
            self.uom_input.setText(mat['uom'] or "")
            self.plant_input.setText(mat['plant'] or "")
            self.mrp_type_input.setText(mat['mrp_type'] or "")
            self.mrp_ctrl_input.setText(mat['mrp_controller'] or "")
            self.reorder_input.setText(str(mat['reorder_point'] or ""))
            self.safety_input.setText(str(mat['safety_stock'] or ""))
    
    def save(self):
        material_id = self.material_input.text().strip()
        if not material_id:
            QMessageBox.warning(self, "Error", "Material ID required")
            return
        
        conn = self.db.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT OR REPLACE INTO materials 
                (material_id, description, material_group, uom, plant,
                 mrp_type, mrp_controller, reorder_point, safety_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material_id,
                self.desc_input.text(),
                self.matgroup_input.text(),
                self.uom_input.text(),
                self.plant_input.text(),
                self.mrp_type_input.text(),
                self.mrp_ctrl_input.text(),
                int(self.reorder_input.text() or 0),
                int(self.safety_input.text() or 0)
            ))
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
        finally:
            conn.close()

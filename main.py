#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
                             QStackedWidget, QToolBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QFont
from pathlib import Path
from database import Database
from screens.po_create import POCreateScreen
from screens.po_display import PODisplayScreen
from screens.so_create import SOCreateScreen
from screens.so_display import SODisplayScreen
from screens.goods_receipt import GoodsReceiptScreen
from screens.fi_posting import FIPostingScreen
from screens.co_cost_center import CostCenterScreen
from screens.master_data import MaterialMasterScreen
from screens.hcm_master import EmployeeMasterScreen

class SAPSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_tcode = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("SAP - Session 01")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load stylesheet
        style_path = Path(__file__).parent / "sap_style.qss"
        if style_path.exists():
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar with T-code input
        self.create_toolbar()
        
        # Central widget - stacked widget for screens
        self.stack = QStackedWidget()
        
        # Home screen
        home_widget = QWidget()
        home_layout = QVBoxLayout()
        welcome_label = QLabel("SAP Module Simulator\n\nMasukkan T-code di toolbar atau pilih dari menu")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 14))
        home_layout.addWidget(welcome_label)
        home_widget.setLayout(home_layout)
        
        self.stack.addWidget(home_widget)
        self.home_index = 0
        
        self.setCentralWidget(self.stack)
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")
        
        self.show()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # System menu
        system_menu = menubar.addMenu("System")
        create_session = QAction("Create Session", self)
        system_menu.addAction(create_session)
        system_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)
        
        # MM Module menu
        mm_menu = menubar.addMenu("MM - Materials Management")
        self.add_tcode_actions(mm_menu, 'MM')
        
        # HCM Module menu
        hcm_menu = menubar.addMenu("HCM - Human Capital")
        self.add_tcode_actions(hcm_menu, 'HCM')
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def add_tcode_actions(self, menu, module):
        tcodes = self.db.get_tcodes(module)
        for tcode in tcodes:
            action = QAction(f"{tcode['code']} - {tcode['name']}", self)
            action.triggered.connect(lambda checked, t=tcode['code']: self.execute_tcode(t))
            menu.addAction(action)
    
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # T-code input
        toolbar.addWidget(QLabel("  T-code: "))
        self.tcode_input = QLineEdit()
        self.tcode_input.setMaximumWidth(120)
        self.tcode_input.setPlaceholderText("ME21N")
        self.tcode_input.returnPressed.connect(self.on_tcode_enter)
        toolbar.addWidget(self.tcode_input)
        
        # Execute button
        exec_btn = QPushButton("▶")
        exec_btn.clicked.connect(self.on_tcode_enter)
        toolbar.addWidget(exec_btn)
        
        toolbar.addSeparator()
        
        # Back button (F3)
        back_btn = QPushButton("Back")
        back_btn.setShortcut(QKeySequence("F3"))
        back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(back_btn)
    
    def on_tcode_enter(self):
        tcode = self.tcode_input.text().strip().upper()
        if tcode:
            self.execute_tcode(tcode)
    
    def execute_tcode(self, tcode):
        tcode_data = self.db.get_tcode(tcode)
        
        if not tcode_data:
            QMessageBox.warning(self, "Error", f"T-code {tcode} tidak ditemukan")
            self.status.showMessage(f"T-code {tcode} tidak valid")
            return
        
        if not tcode_data['implemented']:
            QMessageBox.information(self, "Info", 
                f"{tcode} - {tcode_data['name']}\n\nBelum diimplementasikan")
            return
        
        self.current_tcode = tcode
        self.tcode_input.setText(tcode)
        
        # Load appropriate screen
        if tcode == 'ME21N':
            screen = POCreateScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'ME23N':
            screen = PODisplayScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'MIGO':
            screen = GoodsReceiptScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'MM01':
            screen = MaterialMasterScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'MM03':
            screen = MaterialMasterScreen(self.db, readonly=True)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'PA30':
            screen = EmployeeMasterScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'PA20':
            screen = EmployeeMasterScreen(self.db, readonly=True)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'VA01':
            screen = SOCreateScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'VA03':
            screen = SODisplayScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'FB01':
            screen = FIPostingScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        elif tcode == 'KS01':
            screen = CostCenterScreen(self.db)
            self.stack.addWidget(screen)
            self.stack.setCurrentWidget(screen)
        
        self.status.showMessage(f"{tcode} - {tcode_data['name']}")
    
    def go_back(self):
        if self.stack.currentIndex() > 0:
            self.stack.setCurrentIndex(self.home_index)
            self.current_tcode = None
            self.tcode_input.clear()
            self.status.showMessage("Ready")
    
    def show_about(self):
        QMessageBox.about(self, "About", 
            "SAP Module Simulator\nVersi 0.1\n\nSimulator SAP untuk learning purpose")

def main():
    app = QApplication(sys.argv)
    simulator = SAPSimulator()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

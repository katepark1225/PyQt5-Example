import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import* 
from PyQt5.QtGui import*
from PyQt5.QtPrintSupport import *
import translator
import pdf
import summarize
import summarize_kor

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100,50,1200,900)
        self.setWindowTitle("Demo Application")
        # self.setWindowIcon(QtGui.QIcon(src))
        self.grammar_style = "style_001"
        self.selected_dictionary = ""
        self.layout = QHBoxLayout(self)
        self.create_groupbox()
        self.create_tabs()
        self.setLayout(self.layout)
    def refresh_dictionaries(self, row, column):
        item = self.table.itemAt(row, column)
        self.ID = item.text()
        self.selected_dictionary = self.ID
        if self.ID in self.dictionaries:
            self.table.setParent(None)
            terms = translator.terminology()
            self.long_term = terms[0]
            self.short_term = terms[1]
            self.special_symbols = terms[2]
            long_term_size = len(self.long_term)
            short_term_size = len(self.short_term)
            total_rows = long_term_size + short_term_size + len(self.special_symbols)
            model = QStandardItemModel(total_rows, 2)
            model.setHorizontalHeaderLabels(['용어', '번역'])
            for i, x in self.long_term.iterrows():
                item = QStandardItem(x['term'])
                model.setItem(i, 0, item)
                item = QStandardItem(x['term_kor'])
                model.setItem(i, 1, item)
            for i, x in self.short_term.iterrows():
                item = QStandardItem(x['term'])
                model.setItem(i + long_term_size, 0, item)
                item = QStandardItem(x['term_kor'])
                model.setItem(i + long_term_size, 1, item)
            for i, x in self.special_symbols.iterrows():
                item = QStandardItem(x['term_kor'])
                model.setItem(i + long_term_size + short_term_size, 0, item)
                item = QStandardItem(x['term_kor'])
                model.setItem(i + long_term_size + short_term_size, 1, item)
            filter_proxy_model = QSortFilterProxyModel()
            filter_proxy_model.setSourceModel(model)
            filter_proxy_model.setFilterKeyColumn(0)
            line_edit = QLineEdit()
            line_edit.textChanged.connect(filter_proxy_model.setFilterRegExp)
            self.lbx.addWidget(line_edit)
            table = QTableView()
            table.setModel(filter_proxy_model)
            self.lbx.addWidget(table)
            table.setColumnWidth(0, 250)
            table.setColumnWidth(1, 250)
    def create_groupbox(self):
        self.vbox = QVBoxLayout()
        gb_1 = QGroupBox(self)
        gb_1.setFixedWidth(600)
        gb_1.setTitle("Dictionaries")
        self.vbox.addWidget(gb_1)
        self.lbx = QBoxLayout(QBoxLayout.TopToBottom, parent=self)
        gb_1.setLayout(self.lbx)
        self.table = QTableWidget()
        self.dictionaries = translator.dictionaries()
        self.table.setRowCount(len(self.dictionaries))
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0, 550)
        self.table.setHorizontalHeaderLabels(['Dictionary'])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i, x in enumerate(self.dictionaries):
            newitem = QTableWidgetItem(x)
            self.table.setItem(i, 0, newitem)
        self.table.cellClicked.connect(self.refresh_dictionaries)
        self.lbx.addWidget(self.table)
        self.b1 = QRadioButton("번역합니다")
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda:self.btnstate(self.b1))
        self.b2 = QRadioButton("번역함")
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        self.b3 = QRadioButton("번역해요")
        self.b3.toggled.connect(lambda:self.btnstate(self.b3))
        gb_2 = QGroupBox(self)
        gb_2.setTitle("어조")
        self.vbox.addWidget(gb_2)
        lbx = QBoxLayout(QBoxLayout.TopToBottom, parent=self)
        gb_2.setLayout(lbx)
        lbx.addWidget(self.b1)
        lbx.addWidget(self.b2)
        lbx.addWidget(self.b3)
        self.hbox = QHBoxLayout()
        self.summarizeButton = QPushButton("요약하기")
        self.summarizeButton.clicked.connect(self.summarize)
        self.hbox.addWidget(self.summarizeButton)
        self.runButton = QPushButton("번역하기")
        self.runButton.clicked.connect(self.run)
        self.hbox.addWidget(self.runButton)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.layout)
        self.layout.addLayout(self.vbox)
        self.vbox.addLayout(self.layout)
    def create_tabs(self):
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1,"Input")
        self.tabs.addTab(self.tab2,"Output")
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton = QPushButton("PDF 파일에서 텍스트 불러오기")
        self.pushButton.clicked.connect(self.pushButtonClicked)
        self.tab1.layout.addWidget(self.pushButton)
        self.textBox = QPlainTextEdit("텍스트를 입력하세요")
        self.tab1.layout.addWidget(self.textBox)
        self.tab1.setLayout(self.tab1.layout)
        self.layout.addWidget(self.tabs)
    def pushButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self)
        if fname != "":
            output = pdf.load_file(fname[0])
            self.textBox.setPlainText(output.strip())
    def btnstate(self,b):
        if b.text() == "번역합니다":
            if b.isChecked() == True:
                self.grammar_style = "style_001"
        if b.text() == "번역함":
            if b.isChecked() == True:
                self.grammar_style = "style_002"
        if b.text() == "번역해요":
            if b.isChecked() == True:
                self.grammar_style = "style_003"
    def run(self):
        if self.selected_dictionary == "":
            dlg = QMessageBox(self)
            dlg.setWindowTitle("딕셔너리 없음")
            dlg.setText("딕셔너리를 선택해주세요")
            dlg.addButton(QPushButton('확인'), QMessageBox.YesRole)
            dlg.setIcon(QMessageBox.Information)
            dlg.exec()
        elif self.textBox.toPlainText() != "":
            output = translator.translate(self.textBox.toPlainText(), self.grammar_style, self.selected_dictionary)
            self.tab2.layout = QVBoxLayout(self)
            self.outputText = QPlainTextEdit(output.strip())
            self.tab2.layout.addWidget(self.outputText)
            self.tab2.setLayout(self.tab2.layout)
            cur_index = self.tabs.currentIndex()
            if cur_index < len(self.tabs)-1:
                self.tabs.setCurrentIndex(cur_index+1)
    def summarize(self):
        cur_index = self.tabs.currentIndex()
        if cur_index == 0:
            if self.textBox.toPlainText() != "":
                output = summarize.summarize(self.textBox.toPlainText())
                if output.strip() == "":
                    pass
                else:
                    self.textBox.setPlainText(output.strip())
        else:
            if self.outputText.toPlainText() != "":
                output = summarize_kor.summarize(self.outputText.toPlainText())
                if output.strip() == "":
                    pass
                else:
                    self.outputText.setPlainText(output.strip())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = App()
    demo.show()
    sys.exit(app.exec_())

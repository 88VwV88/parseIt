from PyQt5.QtWidgets import (QApplication, 
                             QPushButton,
                             QMessageBox,
                             QLabel,
                             QLineEdit,
                             QFormLayout,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGroupBox,
                             QTreeWidget,
                             QTreeWidgetItem,
                             QWidget)
from PyQt5.QtCore import QFile, QIODevice

from datetime import date
from sys import argv, exit
from make_html_skeleton import make_html_skeleton, RequiredError
from parse_html import read_html, parse_html
from typing import Optional

def get_string_input(field: str, default: str | int="") -> tuple[QLabel, QLineEdit]:
        return (QLabel(f'{field}: '), QLineEdit(f'{default}'))

class App(QWidget):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.setObjectName('App')
        self.app = app
        self.appLayout = QVBoxLayout()

        self.psrBtn = QPushButton('parser')
        self.psrBtn.clicked.connect(self.add_parser)

        self.sklBtn = QPushButton('skeleton')
        self.sklBtn.clicked.connect(self.add_skeleton)

        self.inits = QVBoxLayout()
        self.inits.addWidget(self.psrBtn)
        self.inits.addWidget(self.sklBtn)
        
        self.appLayout.addLayout(self.inits)

        self.setLayout(self.appLayout)
        self.resize(500, 500)
        self.show()

        self.resBox:  Optional[QGroupBox] = None
        self.formBox: Optional[QGroupBox] = None
        self.psrBox:  Optional[QGroupBox] = None

        exit(self.app.exec())

    def add_parser(self) -> None:
        self.psrBtn.hide()
        if self.resBox is not None:
            self.resBox.hide()
        if self.formBox is not None:
            self.formBox.hide()

        self.psrBox = QGroupBox()

        self.psrLayout = QVBoxLayout()

        self.fileEdit = QLineEdit()
        self.fileEdit.setPlaceholderText('*.html, *.htm, *.htmx')
        self.fileLabel = QLabel('filename: ')

        self.fileRow = QFormLayout()
        self.fileRow.addRow(self.fileLabel, self.fileEdit)
        self.psrLayout.addLayout(self.fileRow)

        self.fileSubmit = QPushButton('submit')
        self.fileSubmit.clicked.connect(self.create_tree)
        self.psrLayout.addWidget(self.fileSubmit)

        self.psrBox.setLayout(self.psrLayout)
        self.appLayout.addWidget(self.psrBox)
        
        self.repaint()
        self.sklBtn.show()

    def add_skeleton(self) -> None:
        if self.psrBox:
            self.psrBox.hide()
        self.information = dict(name=None, year=date.today().year,
                            title=None, description=None, 
                            keywords=None, stylesheet=None, filename=None)
        self.accepted = False

        _fields = ['name', 'year', 'title', 'description (optional)', 'keywords (optional)', 'stylesheet (optional)', 'filename']
        self.fields = [(field, *get_string_input(field)) for field in _fields]

        self.formBox = QGroupBox()
        self.formBox.setObjectName('form')
        self.formLayout = QFormLayout()

        for _, label, edit in self.fields:
            self.formLayout.addRow(label, edit)
        self.formBox.setLayout(self.formLayout)
        self.appLayout.addWidget(self.formBox)

        self.resBox = QGroupBox()
        self.resLayout = QHBoxLayout()

        self.subBtn = QPushButton('submit')
        self.subBtn.clicked.connect(self.populate_information)
        self.resLayout.addWidget(self.subBtn)

        self.clsBtn = QPushButton('close')
        self.clsBtn.clicked.connect(self.app.quit)
        self.resLayout.addWidget(self.clsBtn)


        self.resBox.setLayout(self.resLayout)

        self.appLayout.addWidget(self.resBox)
        self.sklBtn.hide()

        self.repaint()
        self.psrBtn.show()

    def populate_information(self) -> None:
        try:
            name, year, title, description, keywords, stylesheet,filename = self.fields

            _name = name[2].text()
            name[2].setText("")
            if not (0 < len(_name) <= 80):
                raise RequiredError('name')
        
            _year = 0
            if not year[2].text():
                _year = 2000
            else:
                _year = int(year[2].text())
                if not (2000 <= _year <= date.today().year + 1):
                    raise AttributeError(f'year must be in [2000, {date.today().year + 1}]')
            year[2].setText("")

            _title = title[2].text()
            title[2].setText("")
            if not _title:
                raise RequiredError('title')
            
            _description = description[2].text()
            description[2].setText("")

            _keywords = keywords[2].text().split(',') if keywords[2].text() else []
            keywords[2].setText("")

            _stylesheet = stylesheet[2].text()
            stylesheet[2].setText("")
            if _stylesheet and not _stylesheet.endswith(('.tss', 'css', '.scss', '.sass')):
                _stylesheet += '.css'

            _filename = filename[2].text()
            filename[2].setText("")
            if not _filename:
                raise RequiredError('filename')
            if not _filename.endswith(('.htm', '.html')):
                _filename += '.html'
            
            self.information.update(name=_name, year=_year,title=_title, description=_description,keywords=_keywords, stylesheet=_stylesheet,filename=_filename) # type: ignore

        except RequiredError as err:
            msgBox = QMessageBox()
            msgBox.setText(f"{err} is a requied field")
            msgBox.exec()
            return
        
        except AttributeError as err:
            msgBox = QMessageBox()
            msgBox.setText(str(err))
            msgBox.exec()
            return
        
        except Exception as err:
            print(err)
            return
    
        make_html_skeleton(**self.information) # type: ignore
    
    @classmethod
    def populate_tree(self, data, parent):
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            item.setExpanded(True)
            item.setText(0, key)
            if isinstance(value, dict):
                self.populate_tree(value, item)
            else:
                child = QTreeWidgetItem()
                child.setText(0, f'"{value}"')
                item.addChild(child)

    def create_tree(self) -> None:
        if filename := self.fileEdit.text():
            try:
                filename = (filename 
                                if filename.endswith(('.html', '.htm', '.htmx')) 
                                else f'{filename}.html')
                html = read_html(filename)
                self.treeDict = parse_html(html)
                self.psrTree = QTreeWidget()
                self.psrTree.resize(500, 500)
                self.populate_tree(self.treeDict, self.psrTree)
                self.psrLayout.addWidget(self.psrTree)
            except FileNotFoundError as err:
                print('[ERROR]', err)

def main() -> None:
    app = QApplication(argv)
    app.setApplicationName("ParseIT")

    file = QFile('index.css')
    if file.open(QIODevice.OpenModeFlag.ReadOnly):
        style = str(file.readAll().replace('\\n', b''), 'utf-8')
        app.setStyleSheet(style)
        file.close()

    App(app)

if __name__ == '__main__':
    main()
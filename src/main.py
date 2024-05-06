from PyQt5.QtWidgets import (QApplication, 
                             QPushButton,
                             QMessageBox,
                             QLabel,
                             QLineEdit,
                             QFormLayout,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGroupBox,
                             QWidget)
from PyQt5.QtCore import QFile, QIODevice
from datetime import date
from sys import argv, exit
from make_html_skeleton import make_html_skeleton, RequiredError
from typing import Optional

def get_string_input(field: str, default: str | int="") -> tuple[QLabel, QLineEdit]:
        return (QLabel(f'{field}: '), QLineEdit(f'{default}'))

class App(QWidget):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.setObjectName('App')
        self.app = app
        self.appLayout = QVBoxLayout()

        self.parserB = QPushButton('parser')
        self.skeletonB = QPushButton('skeleton')
        self.parserB.clicked.connect(self.add_parser)
        self.skeletonB.clicked.connect(self.add_skeleton)

        self.inits = QVBoxLayout()
        self.inits.addWidget(self.parserB)
        self.inits.addWidget(self.skeletonB)
        
        self.appLayout.addLayout(self.inits)

        self.setLayout(self.appLayout)
        self.resize(500, 500)
        self.show()

        self.responses: Optional[QGroupBox] = None
        self.form: Optional[QGroupBox] = None

        exit(self.app.exec())

    def add_parser(self) -> None:
        self.parserB.hide()
        if self.responses is not None:
            self.responses.hide()
        if self.form is not None:
            self.form.hide()

        self.parserBox = QGroupBox()
        self.parserLayout = QFormLayout()
        self.fileEdit = QLineEdit()
        self.fileEdit.setPlaceholderText('*.html, *.htm, *.htmx')
        self.fileLabel = QLabel('filename: ')
        self.parserLayout.addRow(self.fileLabel, self.fileEdit)
        self.fileSubmit = QPushButton('submit')
        self.fileSubmit.clicked.connect(self.read_file_contents)
        self.parserBox.setLayout(self.parserLayout)
        
        self.appLayout.addWidget(self.parserBox)
        
        self.repaint()
        self.skeletonB.show()
        pass

    def add_skeleton(self) -> None:
        self.information = dict(name=None, year=date.today().year,
                            title=None, description=None, 
                            keywords=None, stylesheet=None, filename=None)
        self.accepted = False

        _fields = ['name', 'year', 'title', 'description (optional)', 'keywords (optional)', 'stylesheet (optional)', 'filename']
        self.fields = [(field, *get_string_input(field)) for field in _fields]

        self.form = QGroupBox()
        self.form.setObjectName('form')
        self.formLayout = QFormLayout()
        for _, label, edit in self.fields:
            self.formLayout.addRow(label, edit)
        self.form.setLayout(self.formLayout)
        self.appLayout.addWidget(self.form)

        self.submitB = QPushButton('submit')
        self.submitB.clicked.connect(self.populate_information)

        self.responses = QGroupBox()
        self.resLayout = QHBoxLayout()

        self.closeB = QPushButton('close')
        self.closeB.clicked.connect(self.app.quit)
        self.resLayout.addWidget(self.closeB)
        self.resLayout.addWidget(self.submitB)
        self.responses.setLayout(self.resLayout)

        self.appLayout.addWidget(self.responses)
        self.skeletonB.hide()

        self.repaint()
        self.parserB.show()

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
            message = QMessageBox()
            message.setText(f"{err} is a requied field")
            message.exec()
            return
        
        except AttributeError as err:
            message = QMessageBox()
            message.setText(str(err))
            message.exec()
            return
        
        except Exception as err:
            print(err)
            return
    
        make_html_skeleton(**self.information) # type: ignore

    def read_file_contents(self) -> None:
        pass


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
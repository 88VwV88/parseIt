from sys import argv
from parseit.app import App
from PySide6.QtWidgets import QApplication


def main() -> None:
    app = QApplication(argv)
    app.setApplicationName("ParseIT")

    with open("styles/app.css") as file:
        style: str = "".join(file.readlines()).replace("\\n", "")
        app.setStyleSheet(style)

    App(app)


if __name__ == "__main__":
    main()

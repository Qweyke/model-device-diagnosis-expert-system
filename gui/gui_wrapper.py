from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox
import sys

app = None


def ensure_app():
    global app
    if app is None:
        app = QApplication(sys.argv)


def gui_ask(title, question, items):
    ensure_app()

    item, ok = QInputDialog.getItem(None, title, question, items, 0, False)
    if not ok:
        sys.exit(0)

    return item.lower().strip()


def gui_message(text):
    ensure_app()
    QMessageBox.information(None, "Diagnosis Result", text)

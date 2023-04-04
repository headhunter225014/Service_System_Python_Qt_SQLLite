import sys  # needed for the sys.argv passed to QApplication below (command line arguments)
from PyQt6 import QtSql
from PyQt6.QtWidgets import QDialog, QApplication, QDataWidgetMapper, QMessageBox, QSpacerItem, QSizePolicy
from PyQt6.uic import loadUi  # special library to load .ui file directly
from pathlib import Path

class MyForm(QDialog):
    # constructor for this MyForm class
    def __init__(self, db_file=None):
        super().__init__()  # calls the constructor of the QDialog class that is inherited

        self.ui = loadUi('project_7_Damir_Zababuryn.ui', self)
        self.ui.pushButtonExit.clicked.connect(self.exitMethod)

        #
        db_file = 'veh_log.db'
        pathobj = Path(db_file)
        bool_is_there = pathobj.expanduser().is_file()

        if not bool_is_there:
            print("no path to db")

        self.conn = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.conn.setDatabaseName(db_file)
        self.conn.open()
        if self.conn.isOpenError():
            dialog2 = QMessageBox()
            dialog2.setWindowTitle("Cannot Open the database!")
            dialog2.setText(f"Database Error: {self.conn.lastError().databaseText()}\n"
                            "Click Ok to exit.")
            button = dialog2.exec()
            sys.exit(1)
        else:
            print("Connection has been established")





    def exitMethod(self):
        #self.conn.close()
        QApplication.instance().quit()


# the code below should not be changed and is constant for all GUI programs
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyForm()
    window.show()
    sys.exit(app.exec())  # note - sys.exit causes traceback in some editors if it does in yours just use app.exec()

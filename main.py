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

        #find a path to db
        db_file = 'veh_log.db'
        pathobj = Path(db_file)
        bool_is_there = pathobj.expanduser().is_file()

        if not bool_is_there:
            print("no path to db")

        #create connection with db
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

        self.model = QtSql.QSqlRelationalTableModel()
        self.delrow = -1

        # Set up the model.
        self.setupModels()

        # Set up the mapper.
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.setItemDelegate(QtSql.QSqlRelationalDelegate())

        self.mapper.addMapping(self.ui.comboBox, self.project_index)  # related field in Projects table




    def exitMethod(self):
        self.conn.close()
        QApplication.instance().quit()

    def setupModels(self):
        self.model.setTable('Maintenance')  # for editable QSqlTableModel()
        self.model.setEditStrategy(QtSql.QSqlTableModel.EditStrategy.OnFieldChange)  # for editable QSqlTableModel()

        ############################################################################
        # setup relationship of tasks.project_id to projects.id to get projects.name
        self.project_index = self.model.fieldIndex("maint_vin")
        self.model.setRelation(self.project_index,
                               QtSql.QSqlRelation("Vehicles", "veh_vin", "veh_name"))
        #############################################################################

        self.model.select()  # used for editable QSqlTableModel()
        #############################################################################
        # setup relationship model and link it to the combobox
        self.relModel = self.model.relationModel(self.project_index)
        self.ui.comboBox.setModel(self.relModel)
        self.ui.comboBox.setModelColumn(self.relModel.fieldIndex('veh_name'))
        #############################################################################


# the code below should not be changed and is constant for all GUI programs
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyForm()
    window.show()
    sys.exit(app.exec())  # note - sys.exit causes traceback in some editors if it does in yours just use app.exec()

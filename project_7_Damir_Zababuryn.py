import sys  # needed for the sys.argv passed to QApplication below (command line arguments)
from PyQt6 import QtSql
from PyQt6.QtCore import QDate
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

         # related field in Vehciles table

        self.mapper.addMapping(self.ui.lineEditMaintNumber, self.model.fieldIndex("maint_num"))
        self.mapper.addMapping(self.ui.comboBox, self.project_index)
        self.mapper.addMapping(self.ui.dateEdit,
                              self.model.fieldIndex("maint_date"))
        self.mapper.addMapping(self.ui.lineEditMileage, self.model.fieldIndex("maint_mi"))
        self.mapper.addMapping(self.ui.lineEditPerformed, self.model.fieldIndex("maint_by"))
        self.mapper.addMapping(self.ui.plainTextEdit, self.model.fieldIndex("maint_desc"))
        self.mapper.addMapping(self.ui.lineEditCost, self.model.fieldIndex("maint_cost"))
        self.mapper.addMapping(self.ui.lineEditDateDue, self.model.fieldIndex("maint_nxdate"))
        self.mapper.addMapping(self.ui.lineEditMileageDue, self.model.fieldIndex("maint_nxmi"))

        # Connect navigation buttons.
        self.pushButtonPrevious.clicked.connect(self.mapper.toPrevious)
        self.pushButtonNext.clicked.connect(self.mapper.toNext)
        self.mapper.currentIndexChanged.connect(self.updateButtons)
        self.ui.pushButtonAdd.clicked.connect(self.addrow)
        self.ui.pushButtonDelete.clicked.connect(self.deleterow)


        self.mapper.toFirst()

    def exitMethod(self):
        self.conn.close()
        QApplication.instance().quit()

    def updateButtons(self, row):
        self.ui.pushButtonPrevious.setEnabled(row > 0)
        self.ui.pushButtonNext.setEnabled(row < self.model.rowCount() - 1)


    def deleterow(self):
        row = self.model.rowCount() - 2
        self.model.removeRow(self.mapper.currentIndex())
        self.mapper.setCurrentIndex(row)
        self.model.select()
        self.ui.pushButtonNext.setEnabled(row < self.model.rowCount() - 1)
        self.mapper.setCurrentIndex(row)

    def addrow(self):
        print("exucting adding function")
        row = self.model.rowCount()  # this is one more than the zero-based index so it adds a new row
        self.model.insertRow(row)
        self.mapper.setCurrentIndex(row)
        self.ui.lineEditMaintNumber.setText(str(row + 1))  # make next task id next number!
        self.ui.dateEdit.setDate(QDate(2023, 4, 3))
        self.ui.lineEditMileage.setText("25")
        self.ui.lineEditPerformed.setText("Damir Zababuryn")
        self.ui.plainTextEdit.setPlainText("Added by Damir Zababuryn")
        self.ui.lineEditCost.setText("50$")
        self.ui.lineEditDateDue.setText("04/10/2023")
        self.ui.lineEditMileageDue.setText("100")
        self.ui.comboBox.setCurrentIndex(0)  # make project id a valid project
        self.mapper.submit()



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

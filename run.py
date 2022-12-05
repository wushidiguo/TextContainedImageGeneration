# -*- coding: utf-8 -*-

import sys
import random
from dataclasses import dataclass
from pathlib import Path
import pickle

from PyQt5 import QtWidgets

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt


class Main(QtWidgets.QMainWindow):

    def __init__(self,parent=None):
        QtWidgets.QMainWindow.__init__(self,parent)

        self.filename = ""

        self.changesSaved = True

        self.dummies = []

        self.initUI()

    def initToolbar(self):
        self.fontBox = QtWidgets.QFontComboBox(self)
        # self.fontBox.currentFontChanged.connect(lambda font: self.text.setCurrentFont(font))
        self.fontBox.currentFontChanged.connect(self.fontChanged)

        self.fontSize = QtWidgets.QSpinBox(self)
        self.fontSize.setSuffix(" pt")  
        self.fontSize.valueChanged.connect(lambda size: self.text.setFontPointSize(size))
        self.fontSize.setValue(28)

        fontColor = QtWidgets.QAction(QtGui.QIcon("icons/font-color.png"), "Change font color", self)
        fontColor.triggered.connect(self.fontColorChanged)

        boldAction = QtWidgets.QAction(QtGui.QIcon("icons/bold.png"), "Bold", self)
        boldAction.triggered.connect(self.bold)

        italicAction = QtWidgets.QAction(QtGui.QIcon("icons/italic.png"), "Italic", self)
        italicAction.triggered.connect(self.italic)

        underlAction = QtWidgets.QAction(QtGui.QIcon("icons/underline.png"), "Underline", self)
        underlAction.triggered.connect(self.underline)

        strikeAction = QtWidgets.QAction(QtGui.QIcon("icons/strike.png"), "Strike-out", self)
        strikeAction.triggered.connect(self.strike)

        superAction = QtWidgets.QAction(QtGui.QIcon("icons/superscript.png"), "Superscript", self)
        superAction.triggered.connect(self.superScript)

        subAction = QtWidgets.QAction(QtGui.QIcon("icons/subscript.png"), "Subscript", self)
        subAction.triggered.connect(self.subScript)

        backColor = QtWidgets.QAction(QtGui.QIcon("icons/highlight.png"), "Change background color", self)
        backColor.triggered.connect(self.highlight)

        setDummyAction = QtWidgets.QAction(QtGui.QIcon("icons/dummy.png"), "Set dummy", self)
        setDummyAction.triggered.connect(self.setDummy)

        deleteDummyAction = QtWidgets.QAction(QtGui.QIcon("icons/delete.png"), "Delete selected dummy", self)
        deleteDummyAction.triggered.connect(self.deleteDummy)

        saveAction = QtWidgets.QAction(QtGui.QIcon("icons/save.png"), "Save current image", self)
        saveAction.triggered.connect(self.save)
        
        saveAllAction = QtWidgets.QAction(QtGui.QIcon("icons/saveall.png"), "Save all inputs", self)
        saveAllAction.triggered.connect(self.saveAll)

        openAction = QtWidgets.QAction(QtGui.QIcon("icons/open.png"), "Open a saved file", self)
        openAction.triggered.connect(self.open)

        generateAction = QtWidgets.QAction(QtGui.QIcon("icons/generate.png"), "Generate images", self)
        generateAction.triggered.connect(self.generate)

        sampleAction = QtWidgets.QAction(QtGui.QIcon("icons/sample.png"), "Sample randomly", self)
        sampleAction.triggered.connect(self.sample)

        undoAction = QtWidgets.QAction(QtGui.QIcon("icons/undo.png"), "Undo last action", self)
        undoAction.triggered.connect(self.text.undo)

        redoAction = QtWidgets.QAction(QtGui.QIcon("icons/redo.png"), "Redo last undone thing", self)
        redoAction.triggered.connect(self.text.redo)

        self.toolbar = self.addToolBar("Options")

        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAllAction)
        self.toolbar.addAction(saveAction)

        self.toolbar.addSeparator()

        self.toolbar.addWidget(self.fontBox)
        self.toolbar.addWidget(self.fontSize)

        self.toolbar.addSeparator()

        self.toolbar.addAction(fontColor)
        self.toolbar.addAction(backColor)

        self.toolbar.addSeparator()

        self.toolbar.addAction(boldAction)
        self.toolbar.addAction(italicAction)
        self.toolbar.addAction(underlAction)
        self.toolbar.addAction(strikeAction)
        self.toolbar.addAction(superAction)
        self.toolbar.addAction(subAction)

        self.toolbar.addSeparator()

        self.toolbar.addAction(setDummyAction)
        self.toolbar.addAction(deleteDummyAction)
        self.toolbar.addAction(sampleAction)
        self.toolbar.addAction(generateAction)

        self.toolbar.addSeparator()

        self.toolbar.addAction(undoAction)
        self.toolbar.addAction(redoAction)

        self.addToolBarBreak()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()

        tlayout = QtWidgets.QVBoxLayout()   # top layout
        blayout = QtWidgets.QGridLayout()   # bottom layout

        layout.addLayout(tlayout, stretch=4)
        layout.addLayout(blayout, stretch=6)

        textWidget = QtWidgets.QWidget()
        labelWidget = QtWidgets.QWidget()
        tlayout.addWidget(textWidget, stretch=1)
        tlayout.addWidget(labelWidget, stretch=1)
        leftLayout = QtWidgets.QGridLayout()
        rightLayout = QtWidgets.QGridLayout()
        textWidget.setLayout(leftLayout)
        labelWidget.setLayout(rightLayout)

        self.text = TextEdit(self)
        leftLayout.addWidget(self.text)

        self.text.setTabStopWidth(33)
        self.text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.text.setFrameStyle(0)

        self.initToolbar()

        self.statusbar = self.statusBar()

        self.text.textChanged.connect(self.changed)
        self.text.selectionChanged.connect(self.instantview)

        self.label = QtWidgets.QLabel()
        rightLayout.addWidget(self.label)

        self.table = QtWidgets.QTableView(self)
        model = TableModel(self.dummies)
        self.table.setModel(model)
        self.table.setColumnWidth(2, 600)
        blayout.addWidget(self.table)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setGeometry(100,100,900,500)
        self.setWindowTitle("Text Contained Image Generation")
        self.setWindowIcon(QtGui.QIcon("icons/icon.png"))

        self.text.setText("T")
        self.fitcontents()
        self.text.clear()
        self.text.setFocus()

    def fontChanged(self, font):
        self.text.setCurrentFont(font)
        self.text.setFontPointSize(self.fontSize.value())

    
    def changed(self):
        self.changesSaved = False
        self.fitcontents()
        self.instantview()
        if not self.text.toPlainText():
            font = self.text.font()
            size = self.fontSize.value()
            font.setPointSize(size)
            self.text.setFont(font)

    def instantview(self):
        pixmap = QtGui.QPixmap(self.text.document().size().toSize())
        pixmap.fill(QtGui.QColorConstants.Transparent)
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Source)
        self.text.document().drawContents(painter)
        painter.end()
        self.label.setPixmap(pixmap)

    def fitcontents(self):
        if not self.text.document().toPlainText():
            return
        height = self.text.document().size().toSize().height() 
        if self.text.horizontalScrollBar().isVisible():
            height += self.text.horizontalScrollBar().size().height()
        self.text.setFixedHeight(height)

    def save(self, filename=None):
        if not filename:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save image", ".", "Image File (*.png *.jpg)")[0]
        if not filename:
            return
        if not filename.endswith((".jpg", ".png")):
            filename += ".png"
        pixmap = self.label.pixmap()
        if pixmap is not None: 
            pixmap.save(filename, "PNG", quality=100)

    def saveAll(self):
        if not self.filename:
          self.filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', ".", "(*.tig)")[0]

        if self.filename:
            contents = {
                "html": self.text.toHtml(),
                "dummies": self.dummies
            }
            with open (self.filename, "wb") as f:
                pickle.dump(contents, f)

            self.changesSaved = True

    def open(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',".","(*.tig)")[0]

        if self.filename:
            try:
                with open (self.filename, "rb") as f:
                    contents = pickle.load(f)
                self.text.setHtml(contents["html"])
                self.dummies = contents["dummies"]
                self.table.setModel(TableModel(self.dummies))
            except Exception:
                QtWidgets.QMessageBox.information(self, "Warning", f"Failed loading file {self.filename}.")


    def fontColorChanged(self):

        # Get a color from the text dialog
        color = QtWidgets.QColorDialog.getColor()

        # Set it as the new text color
        self.text.setTextColor(color)

    def highlight(self):

        color = QtWidgets.QColorDialog.getColor()

        self.text.setTextBackgroundColor(color)

    def bold(self):

        if self.text.fontWeight() == QtGui.QFont.Bold:

            self.text.setFontWeight(QtGui.QFont.Normal)

        else:

            self.text.setFontWeight(QtGui.QFont.Bold)

    def italic(self):

        state = self.text.fontItalic()

        self.text.setFontItalic(not state)

    def underline(self):

        state = self.text.fontUnderline()

        self.text.setFontUnderline(not state)

    def strike(self):

        # Grab the text's format
        fmt = self.text.currentCharFormat()

        # Set the fontStrikeOut property to its opposite
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())

        # And set the next char format
        self.text.setCurrentCharFormat(fmt)

    def superScript(self):

        # Grab the current format
        fmt = self.text.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QtGui.QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)

        else:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        # Set the new format
        self.text.setCurrentCharFormat(fmt)

    def subScript(self):

        # Grab the current format
        fmt = self.text.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QtGui.QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)

        else:

            fmt.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        # Set the new format
        self.text.setCurrentCharFormat(fmt)

    def backImage(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",".","Image File (*.jpg *.png)")[0]

        if filename:
            self.text.setStyleSheet(f"border-image: url({filename});")

        self.instantview()

    def resetBack(self):
        self.text.setStyleSheet("border-image: url();")

        self.instantview()

    def sample(self):
        if not self.dummies:
            return
        shift = 0
        for dummy in self.dummies:
            cursor = self.text.textCursor()
            cursor.setPosition(dummy.start + shift)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, dummy.end - dummy.start)

            if cursor.hasSelection() and dummy.text_bag:
                text = random.choice(dummy.text_bag)
                cursor.insertText(text)
                self.text.setTextCursor(cursor)
                shift += len(text) - (dummy.end - dummy.start)

    def generate(self):
        if not self.dummies:
            return

        text, ok = QtWidgets.QInputDialog.getText(self, "Please input", "Input the number of images you want to generate.", )
        
        if not ok:
            return
        try:
            val_int = int(text)
        except ValueError as e:
            QtWidgets.QMessageBox.information(self, "Warning", "Please input int value")
        else:
            number = val_int
        
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder to save images", ".")
        if not folder:
            return
        folder = Path(folder)
        original = self.text.toHtml()
        for i in range(number):
            self.sample()
            label = self.text.toPlainText()
            filename = folder / f"{i}.png"
            j = 0
            while filename.exists():
                j += 1
                filename = folder / f"{i}({j}).png"
            self.save(str(filename))
            with open(folder / "labels.txt", "a") as f:
                f.write(str(filename) + "\t" + label + "\n")
            self.text.setHtml(original)
        QtWidgets.QMessageBox.information(self, "Info", "Done!")
        
    def setDummy(self):
        if not self.text.document().toPlainText():
            return
        text_bag = []
        ret = QtWidgets.QMessageBox.question(self, "Please choose:", "Add text bag from file?", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',".","(*.txt *.csv)")[0]
            if filename:
                with open(filename,"rt", encoding="utf-8") as file:
                    text_bag = file.read().split(",")

        cursor = self.text.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
        else:
            start = 0 
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.EndOfLine)
            end = cursor.position()
        self.dummies.append(Dummy(start, end, text_bag))
        model = TableModel(self.dummies)
        self.table.setModel(model) 
        self.changesSaved = False 

    def deleteDummy(self):
        indexes = self.table.selectedIndexes()
        for idx in indexes:
            row = idx.row()
            self.dummies.pop(row)
        model = TableModel(self.dummies)
        self.table.setModel(model)
        self.changesSaved = False
    
    def closeEvent(self,event):
        if self.changesSaved:
            event.accept()
        else:
            popup = QtWidgets.QMessageBox(self)
            popup.setIcon(QtWidgets.QMessageBox.Warning)
            popup.setText("The document has been modified")
            popup.setInformativeText("Do you want to save your changes?")
            popup.setStandardButtons(QtWidgets.QMessageBox.Save   |
                                      QtWidgets.QMessageBox.Cancel |
                                      QtWidgets.QMessageBox.Discard)
            popup.setDefaultButton(QtWidgets.QMessageBox.Save)
            answer = popup.exec_()
            if answer == QtWidgets.QMessageBox.Save:
                self.saveAll()
            elif answer == QtWidgets.QMessageBox.Discard:
                event.accept()
            else:
                event.ignore() 


class TextEdit(QtWidgets.QTextEdit):
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            return
        super().keyPressEvent(event)


@dataclass
class Dummy:
    start: int
    end: int
    text_bag: list

    def toList(self):
        return [self.start, self.end, ",".join(self.text_bag)]

    @classmethod
    def toHeaderList(self):
        return ["start", "end", "text_bag"]

    def validateAndSetStart(self, start):
        try:
            val_int = int(start)
            if val_int >= 0:  
                self.start = val_int
                return True
        except ValueError:
            pass  # Non-integer value is invalid.
        return False

    def validateAndSetEnd(self, end):
        try:
            val_int = int(end)
            if val_int >= self.start:  
                self.end = val_int
                return True
        except ValueError:
            pass  
        return False
    
    def validateAndSetText(self, text):
        try:
            text = str(text)
            self.text_bag = text.split(",")
            return True
        except ValueError:
            pass
        return False


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, dummies, parent=None):
        super().__init__(parent)
        self.dummies = sorted(dummies, key=lambda dummy: dummy.start)
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self.dummies[index.row()].toList()[index.column()]
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.dummies)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(Dummy.toHeaderList())
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return Dummy.toHeaderList()[section]
            return "" 

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return self.dummies[index.row()].validateAndSetStart(value)
            elif index.column() == 1:
                return self.dummies[index.row()].validateAndSetEnd(value)
            elif index.column() == 2:
                return self.dummies[index.row()].validateAndSetText(value)
        return False

    def flags(self, index):
        if index.isValid():
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
        return Qt.ItemFlag.NoItemFlags 

    

def main():
    app = QtWidgets.QApplication(sys.argv)

    main = Main()
    main.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

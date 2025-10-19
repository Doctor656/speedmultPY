from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, pyqtSignal

import os

class FSM_Checkable(QFileSystemModel):
    checkStateChanged = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.checkStates = {}
        self.rowsInserted.connect(self.checkAdded)
        self.rowsRemoved.connect(self.checkParent)
        self.rowsAboutToBeRemoved.connect(self.checkRemoved)

    def getchecklist(self):
        temp = set()
        for i in set(self.checkStates):
            if self.checkStates[i] == Qt.CheckState.Unchecked or self.checkStates[i] == 0:
                if os.path.isdir(i):
                    for root, dirs, files in os.walk(i, topdown=False):
                        for name in files:
                            if name.endswith('.hkx'):
                                temp.add(os.path.join(root, name))
                else:
                    temp.add(i)
        return temp

    def checkState(self, index):
        return self.checkStates.get(self.filePath(index), Qt.CheckState.Checked)

    def setCheckState(self, index, state, emitStateChange=True):
        path = self.filePath(index)
        if self.checkStates.get(path) == state:
            return
        self.checkStates[path] = state
        if emitStateChange:
            self.checkStateChanged.emit(path, bool(state))

    def checkAdded(self, parent, first, last):
        # if a file/directory is added, ensure it follows the parent state as long
        # as the parent is already tracked; note that this happens also when 
        # expanding a directory that has not been previously loaded
        if not parent.isValid():
            return
        if self.filePath(parent) in self.checkStates:
            state = self.checkState(parent)
            for row in range(first, last + 1):
                index = self.index(row, 0, parent)
                path = self.filePath(index)
                if path not in self.checkStates:
                    self.checkStates[path] = state
        self.checkParent(parent)

    def checkRemoved(self, parent, first, last):
        # remove items from the internal dictionary when a file is deleted; 
        # note that this *has* to happen *before* the model actually updates, 
        # that's the reason this function is connected to rowsAboutToBeRemoved
        for row in range(first, last + 1):
            path = self.filePath(self.index(row, 0, parent))
            if path in self.checkStates:
                self.checkStates.pop(path)

    def checkParent(self, parent):
        # verify the state of the parent according to the children states
        if not parent.isValid():
            return
        childStates = [self.checkState(self.index(r, 0, parent)) for r in range(self.rowCount(parent))]
        if all(childStates):
            newState = Qt.CheckState.Checked
        elif all([not i for i in childStates]):
            newState = Qt.CheckState.Unchecked
        else:
            newState = Qt.CheckState.PartiallyChecked
        oldState = self.checkState(parent)
        if newState != oldState:
            self.setCheckState(parent, newState)
            self.dataChanged.emit(parent, parent)
        self.checkParent(parent.parent())

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            return self.checkState(index)
        return super().data(index, role)

    def setData(self, index, value, role = Qt.ItemDataRole.CheckStateRole, checkParent = True, emitStateChange = True):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            self.setCheckState(index, value, emitStateChange)
            for row in range(self.rowCount(index)):
                # set the data for the children, but do not emit the state change, 
                # and don't check the parent state (to avoid recursion)
                self.setData(self.index(row, 0, index), value, Qt.ItemDataRole.CheckStateRole, checkParent=False, emitStateChange=False)
            self.dataChanged.emit(index, index)
            if checkParent:
                self.checkParent(index.parent())
            return True

        return super().setData(index, value, role)
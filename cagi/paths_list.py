import os
from PyQt5.QtCore import QStringListModel, QModelIndex, QItemSelectionModel, Qt
from PyQt5.QtWidgets import QListView

FILES_PATH = "/".join(
    os.path.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])) + '/data/'


class PathsListView(QListView):
    """List all .csv files contained in the folder '../dados/'"""

    def __init__(self, parent=None):

        QListView.__init__(self, parent)

        self._model = QStringListModel()
        self.fetch_paths()
        self.setModel(self._model)
        self.setWindowTitle('PathsList')
        self.setFocusPolicy(Qt.ClickFocus)
        self.clicked[QModelIndex].connect(self.item_clicked)

        self.selectionModel().select(
            self._model.createIndex(0, 0), QItemSelectionModel.Select)

    def fetch_paths(self):
        """Fetch all valid paths to .csv files and display them"""

        pathList = [path for path in os.listdir(
            FILES_PATH) if path.endswith('.csv') and int(path[0]) > 3]
        pathList.sort(reverse=True)

        for i, path in enumerate(pathList):

            pathList[i] = path + ' - ' + str(
                round(float(os.path.getsize(FILES_PATH + path)) / pow(10, 6), 2)) + ' mb'

        self._model.setStringList(pathList)

    def get_path(self):
        """Get path of currently selected file

        Return:
            path (string): path of the current file
        """

        return FILES_PATH + self.selectedIndexes()[0].data().split(' ')[0]

    def item_clicked(self, index):
        """
        Check if step and number values, read GUI.misc_menu documentation, are valid.

        Inca se they aren't change them to default [1, 1]
        """

        values = [int(s)
                  for s in index.data().replace('.', '_').split('_') if s.isdigit()][2:]

        if len(values) != 2:
            values = [1, 1]

        self.parent().parent().set_san_values(values)

if __name__ == '__main__':
    pass

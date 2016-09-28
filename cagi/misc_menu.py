from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit


class MiscMenu(QLineEdit):
    """
    Miscellaneous menu contains step and number values

    Step represents the difference in micrometers between data points
    Number represents the number of data points used in each measn
    """

    def __init__(self, parent=None):

        QLineEdit.__init__(self, 'HUE')
        self.setParent(parent)

        self.setMaxLength(10)
        self.setText('1 | 1')
        self.setFixedWidth(110)
        self.setAlignment(Qt.AlignHCenter)
        self.setPlaceholderText('step | num')

    def set_san_values(self, values):
        """Set string with combination of step and number values

        Input:
            values ([int]): step and number values
        """

        self.setText(str(values[0]) + ' | ' + str(values[1]))

    def get_values(self):
        """Return values of step and number

        Return:
            values ([int]): step and number values
        """

        return [int(s) for s in self.text().replace(' ', '').split('|')]

    def is_valid(self):
        """
        Verify if current values are valid

        Its valid if both exist and are non negative integers
        """

        aux_string = self.text().replace(' ', '').split('|')

        if len(aux_string) != 2:
            return False

        for elem in aux_string:
            if not elem.isdigit():
                return False

        return True

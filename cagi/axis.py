from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QCheckBox


class Axis:
    """
    Axis determines which values will be retrieved from the data file

    The possibilities are:
        - 2 different LEDs, represents the distance between them
        - 1 LED and 1 coordinate, represents the value of this coordinate of the LED
        - Temperature or time, self explanatory

    No invalid combination of boxes can be checked
    """

    def create_boxes(self):
        """Organize the check boxes"""

        self._ctrl_leds = [False for i in range(5)]

        self.setFocusPolicy(Qt.ClickFocus)

        self._cb_l1 = QCheckBox('Led1', self)
        self._cb_l1.stateChanged.connect(self.change_led_state(1))
        self._cb_l1.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_l1)

        self._cb_l2 = QCheckBox('Led2', self)
        self._cb_l2.stateChanged.connect(self.change_led_state(2))
        self._cb_l2.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_l2)

        self._cb_l3 = QCheckBox('Led3', self)
        self._cb_l3.stateChanged.connect(self.change_led_state(3))
        self._cb_l3.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_l3)

        self._cb_l4 = QCheckBox('Led4', self)
        self._cb_l4.stateChanged.connect(self.change_led_state(4))
        self._cb_l4.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_l4)

        self._cb_x = QCheckBox('Linhas', self)
        self._cb_x.stateChanged.connect(self.change_coord_state(0))
        self._cb_x.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_x)

        self._cb_y = QCheckBox('Colunas', self)
        self._cb_y.stateChanged.connect(self.change_coord_state(1))
        self._cb_y.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_y)

        self._cb_temp = QCheckBox('Temp.', self)
        self._cb_temp.stateChanged.connect(self.change_others_state(1))
        self._cb_temp.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_temp)

        self._cb_time = QCheckBox('Tempo', self)
        self._cb_time.stateChanged.connect(self.change_others_state(0))
        self._cb_time.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_time)

        self._cb_pos = QCheckBox('Pos.', self)
        self._cb_pos.stateChanged.connect(self.change_others_state(2))
        self._cb_pos.setLayoutDirection(Qt.RightToLeft)
        self._box_lay.addWidget(self._cb_pos)

    def change_led_state(self, ind):
        """Logic behind when a LED box change state

        Input:
            ind (int): index of LED that changed state
        """

        def change_led():
            self._ctrl_leds[ind] = not self._ctrl_leds[ind]

            if self._ctrl_leds[ind] == True:
                if self.count_set_leds() == 1:
                    self.disable_others()

                    if self._cb_x.isChecked() or self._cb_y.isChecked():
                        self.disable_leds()
                else:
                    self.disable_leds()
                    self.disable_coords()
            else:
                self.enable_leds()
                if self.count_set_leds() == 1:
                    self.enable_coords()

                elif not self._cb_x.isChecked() and not self._cb_y.isChecked():
                        self.enable_others()

        return change_led

    def change_coord_state(self, ind):
        """Logic behind when a coordinate box is checked

        Input:
            ind (int): which coordinate box was checked, 0 for x and 1 for y
        """

        def change_coord():
            ctrl_aux = (ind == 0) * self._cb_x.isChecked() or (
                ind == 1) * self._cb_y.isChecked()

            if ctrl_aux == True:
                self.disable_others()
                self.disable_coords()

                if self.count_set_leds() == 1:
                    self.disable_leds()
            else:
                self.enable_coords()
                self.enable_leds()

                if self.count_set_leds() == 0:
                    self.enable_others()

        return change_coord

    def change_others_state(self, ind):
        """Logic behind when a time, temperature or distance box is checked

        Input:
            ind (int): which 'other' box was checked
        """

        def change_others():
            ctrl_aux = ((ind == 0) * self._cb_time.isChecked() or (ind == 1) * self._cb_temp.isChecked() or
                        (ind == 2) * self._cb_pos.isChecked())

            if ctrl_aux == True:
                self.disable_others()
                self.disable_coords()
                self.disable_leds()
            else:
                self.enable_others()
                self.enable_coords()
                self.enable_leds()

        return change_others

    def enable_coords(self):
        """Enable coordinates boxes"""

        self._cb_x.setEnabled(True)
        self._cb_y.setEnabled(True)

    def disable_coords(self):
        """Disable coordinates boxes"""

        self._cb_x.setDisabled(not self._cb_x.isChecked())
        self._cb_y.setDisabled(not self._cb_y.isChecked())

    def enable_others(self):
        """Enable time, temperature and distance boxes"""

        self._cb_time.setEnabled(True)
        self._cb_temp.setEnabled(True)
        self._cb_pos.setEnabled(True)

    def disable_others(self):
        """Disable time, temperature and distance boxes"""

        self._cb_time.setDisabled(not self._cb_time.isChecked())
        self._cb_temp.setDisabled(not self._cb_temp.isChecked())
        self._cb_pos.setDisabled(not self._cb_pos.isChecked())

    def enable_leds(self):
        """Enable LEDs boxes"""

        self._cb_l1.setEnabled(True)
        self._cb_l2.setEnabled(True)
        self._cb_l3.setEnabled(True)
        self._cb_l4.setEnabled(True)

    def disable_leds(self):
        """Disable LEDs boxes"""

        self._cb_l1.setDisabled(not self._cb_l1.isChecked())
        self._cb_l2.setDisabled(not self._cb_l2.isChecked())
        self._cb_l3.setDisabled(not self._cb_l3.isChecked())
        self._cb_l4.setDisabled(not self._cb_l4.isChecked())

    def count_set_leds(self):
        """Count the number of active LEDs boxes

        Return:
            val (int): number of LEDs with active boxes
        """

        return len([i for i in self._ctrl_leds if i == True])

    def is_valid(self):
        """Test if current combination of check boxes means a valid information from the data

        Return:
            valid (bool): True if combination is valid, false otherwise
        """

        if self.count_set_leds() == 1:
            return self._cb_x.isChecked() or self._cb_y.isChecked()
        elif self.count_set_leds() == 0:
            return self._cb_temp.isChecked() or self._cb_time.isChecked() or self._cb_pos.isChecked()

        return True

    def get_ind(self):
        """Indices in the data sheet that the current boxes combination represent

        Return:
            ind ([int]): Indices in the data sheet
        """

        ind = [2 * (i - 1) for i in range(5) if self._ctrl_leds[i] == True]

        if not ind:
            ind.append(8 * self._cb_temp.isChecked() + 9 *
                       self._cb_time.isChecked() + 10 * self._cb_pos.isChecked())

        if self._cb_y.isChecked():
            ind[0] += 1

        return ind


class YAxis(QWidget, Axis):

    """Vertical Axis"""

    def __init__(self, parent=None):
        QWidget.__init__(self)

        self._box_lay = QVBoxLayout()
        self.setLayout(self._box_lay)
        self.create_boxes()
        self._cb_pos.hide()

        # Initial State
        self._cb_l1.setChecked(True)
        self._cb_l2.setChecked(True)


class XAxis(QWidget, Axis):

    """Horizontal Axis"""

    def __init__(self, parent=None):
        QWidget.__init__(self)

        self._box_lay = QHBoxLayout()
        self.setLayout(self._box_lay)
        self.create_boxes()

        # Initial State
        self._cb_pos.setChecked(True)

if __name__ == '__main__':
    pass
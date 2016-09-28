#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QAction, qApp,
                            QHBoxLayout, QMessageBox, QWidget, QPushButton)

from cagi.mpl_canvas import MplCanvas
from cagi.paths_list import PathsListView
from cagi.axis import XAxis, YAxis
from cagi.misc_menu import MiscMenu


class AppForm(QMainWindow):

    """Dedicated interface to plot LEDs information"""

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Curves Analysis Graphic Interface')
        self.create_main_frame()

    def create_main_frame(self):
        """Creates interface, initialize widgets and organize screen"""

        self._main_frame = QWidget()

        self._canvas = MplCanvas(self._main_frame, width=6, height=5, dpi=100)
        self._paths_list = PathsListView(self._main_frame)
        self._yaxis = YAxis(self._main_frame)
        self._xaxis = XAxis(self._main_frame)
        self._misc = MiscMenu(self._main_frame)

        # Plot button
        self._plot_btn = QPushButton('Plot', self)
        self._plot_btn.resize(self._plot_btn.sizeHint())
        self._plot_btn.setStyleSheet("background-color: cyan")
        self._plot_btn.clicked.connect(self.plot_data)

        self.organize_screen()
        self.create_menus()

    def organize_screen(self):
        """Define layout of the screen"""

        box1 = QVBoxLayout()
        box1.addWidget(self._canvas)
        box1.addWidget(self._xaxis)

        box2 = QVBoxLayout()
        box2.addWidget(self._yaxis)
        box2.addWidget(self._misc)
        box2.addWidget(self._plot_btn)

        box3 = QHBoxLayout()
        box3.addLayout(box2)
        box3.addLayout(box1)

        box4 = QVBoxLayout()
        box4.addLayout(box3)
        box4.addWidget(self._paths_list)

        self._main_frame.setLayout(box4)
        self._main_frame.setFocus()
        self.setCentralWidget(self._main_frame)
        self.setGeometry(100, 100, 800, 750)

    def create_menus(self):
        """Creates menus on top of the screen"""

        # 'File' menu
        self._file_menu = self.menuBar().addMenu('&File')

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut(Qt.CTRL + Qt.Key_E)
        exit_action.triggered.connect(qApp.quit)

        about_action = QAction('&About', self)
        about_action.setShortcut(Qt.CTRL + Qt.Key_A)
        about_action.triggered.connect(self.about_message)

        refresh_paths_action = QAction('&Refresh', self)
        refresh_paths_action.setShortcut(Qt.Key_F5)
        refresh_paths_action.triggered.connect(self._paths_list.fetch_paths)

        self._file_menu.addAction(refresh_paths_action)
        self._file_menu.addAction(about_action)
        self._file_menu.addAction(exit_action)

        self._main_frame.addAction(refresh_paths_action)
        self._main_frame.addAction(about_action)
        self._main_frame.addAction(exit_action)

        # 'Plot' menu
        self._plot_menu = self.menuBar().addMenu('&Plot')

        plot_action = QAction('&Plot', self)
        plot_action.setShortcut(Qt.CTRL + Qt.Key_P)
        plot_action.triggered.connect(self.plot_data)

        linear_fit_action = QAction('&Linear Fit', self)
        linear_fit_action.setShortcut(Qt.CTRL + Qt.Key_L)
        linear_fit_action.triggered.connect(self._canvas.linear_regression)

        parabolic_fit_action = QAction('&Parabolic Fit', self)
        parabolic_fit_action.setShortcut(Qt.CTRL + Qt.Key_Q)
        parabolic_fit_action.triggered.connect(
            self._canvas.parabolic_regression)

        hyperbolic_fit_action = QAction('&Hyperbolic Fit', self)
        hyperbolic_fit_action.setShortcut(Qt.CTRL + Qt.Key_H)
        hyperbolic_fit_action.triggered.connect(
            self._canvas.hyperbolic_regression)

        remove_range_action = QAction('&Remove Points', self)
        remove_range_action.setShortcut(Qt.CTRL + Qt.Key_R)
        remove_range_action.triggered.connect(self._canvas.remove_points)

        compare_data_fit_action = QAction('&Compare Fit', self)
        compare_data_fit_action.setShortcut(Qt.CTRL + Qt.Key_D)
        compare_data_fit_action.triggered.connect(self._canvas.plot_diff_fit)

        add_stddev_segments_action = QAction('&Std. dev. Segments', self)
        add_stddev_segments_action.setShortcut(Qt.CTRL + Qt.Key_S)
        add_stddev_segments_action.triggered.connect(
            self._canvas.plot_stddev_fit)

        self._plot_menu.addAction(plot_action)
        self._plot_menu.addAction(remove_range_action)
        self._plot_menu.addAction(linear_fit_action)
        self._plot_menu.addAction(parabolic_fit_action)
        self._plot_menu.addAction(hyperbolic_fit_action)
        self._plot_menu.addAction(compare_data_fit_action)
        self._plot_menu.addAction(add_stddev_segments_action)

        self._main_frame.addAction(plot_action)
        self._main_frame.addAction(remove_range_action)
        self._main_frame.addAction(linear_fit_action)
        self._main_frame.addAction(parabolic_fit_action)
        self._main_frame.addAction(hyperbolic_fit_action)
        self._main_frame.addAction(compare_data_fit_action)
        self._main_frame.addAction(add_stddev_segments_action)

    def about_message(self):
        """About message"""

        QMessageBox.about(self._main_frame, 'About',
                          '''
                          Data analysis application.

                          Choose the csv file which contains the data,
                          select what information X and Y axis represent,
                          plot the data.

                          If necessary, remove non-useful data points.
                          Fit the best line to interpret the data.
                          Calculate the standard deviation of values, and compare them to the predicted values.
                          ''')

    def set_san_values(self, values):
        """Set step and n values in misc menu"""

        self._misc.set_san_values(values)

    def plot_data(self):
        """Plots data"""

        if not self._yaxis.is_valid() or not self._xaxis.is_valid() or not self._misc.is_valid():
            QMessageBox.question(
                self, 'Erro', 'Escolha plot valido', QMessageBox.Ok, QMessageBox.Ok)
            return

        self._canvas.plot_data(self._yaxis.get_ind(), self._xaxis.get_ind(),
                               self._misc.get_values(), self._paths_list.get_path())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

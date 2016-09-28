#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import matplotlib
matplotlib.use("Qt5Agg")
import numpy as np
from math import pow, sqrt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QSizePolicy, QMessageBox, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

OUTLIERS_RATIO = 15


class MplCanvas(FigureCanvas):
    """MatPlotLib Canvas is where data is plot and analyzed. It's a QWidget that contains a Canvas and
        useful methods for data analysis.

        This class does curve regression, with chosen degree, allows to manually remove plotted points,
        compares predicted values with real data and shows expected values in certain probability.

        Args:
            parent (QWidget): Parent widget, usually the main frame of application
            width (int): width in inches
            height (int): height in inches
            dpi (int): dots per inch

        Note:
            There are several boolean control variables, they're listed bellow:

            self._ctrl_ret: True when a selection rectangle is active in the image, used when removing
                            points of the data
            self._ctrl_diff: True when the graph of difference between fit line and real data is visible
            self._ctrl_curve: True when a curve is fit to the data
            self._ctrl_stddev: True when the lines of standard deviation ranges are shown in the plot
            self._is_removing_data: True when the feature of removing points is active
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.setParent(parent)
        self._axes = fig.add_subplot(111)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()

        # Matplotlib toolbar and events
        self.mpl_toolbar = NavigationToolbar(self, self.parent())
        self.mpl_toolbar.hide()
        self.mpl_connect('key_press_event', self.on_key_press)
        self.mpl_connect('button_press_event', self.cursor_press)
        self.mpl_connect('button_release_event', self.cursor_release)
        self.mpl_connect('figure_enter_event', self.cursor_enter_figure)
        self.mpl_connect('motion_notify_event', self.cursor_motion)
        self._selection_ret = Rectangle(
            (0, 0), 0, 0, facecolor='None', edgecolor='black')
        self._selection_ret.set_linestyle('dotted')
        self._selection_ret.set_linewidth(1)
        self._ctrl_ret = False

        [self._data, self._data_x, self._data_y, self._predicted_y] = [[]
                                                                       for i in range(4)]
        self._ind_x, self._ind_y = 0, 0
        self._fit_par = []
        self._prev_path = ""
        self._ctrl_diff = False
        self._ctrl_curve = False
        self._ctrl_stddev = False
        self._is_removing_data = False

    def plot_data(self, ind_y, ind_x, (step, n), path):
        """Plot data contained in 'path' in the MPL Canvas.

            ind_y and ind_x behave similarly, the only difference is which axis they represent.
            If ind has two elements the distance between the LEDs, represented by these elements in 'self._data',
            will be plot. Otherwise the only value in ind represents the index in 'self._data' that should be plot.

            Args:
                ind_y (int): Array of indices in 'self._data' elements to plot in Y axis
                ind_x (int): Array of indices in 'self._data' elements to plot in X axis
                step (int): The physical water level incremented between points in plot, measured in micrometers.
                n (int): Number of elements that should be used in each mean of values.
                path (str): Path to csv file that contains the data
        """

        self.fetch_data(path)

        [self._data_y, self._data_x, temp_x, temp_y], cont = [[]
                                                              for i in range(4)], 0

        for elem in self._data:

            temp_y.append(
                ((len(ind_y) == 1) and float(elem[ind_y[0]])) or
                ((len(ind_y) == 2) and sqrt(pow(float(elem[ind_y[0]]) - float(elem[ind_y[1]]), 2) +
                                            pow(float(elem[ind_y[0] + 1]) - float(elem[ind_y[1] + 1]), 2)))
            )

            if ind_x[0] <= 9:  # Otherwise X axis is "distance" and is not stored in 'self._data'
                temp_x.append(
                    ((len(ind_x) == 1) and float(elem[ind_x[0]])) or
                    ((len(ind_x) == 2) and sqrt(pow(float(elem[ind_x[0]]) - float(elem[ind_x[1]]), 2) +
                                                pow(float(elem[ind_x[0] + 1]) - float(elem[ind_x[1] + 1]), 2)))
                )

            if len(temp_y) == n:
                self._data_y.append(np.mean(self.remove_outliers(temp_y)))

                if not temp_x:  # X axis is "distance"
                    self._data_x.append(step * len(self._data_x))
                else:
                    self._data_x.append(np.mean(self.remove_outliers(temp_x)))

                temp_y, temp_x = [], []

        self._is_removing_data = False
        self._data_x = np.array(self._data_x)
        self._data_y = np.array(self._data_y)
        self._data_colors = np.linspace(1, 0, len(self._data_y))
        self._ind_x = ind_x
        self._ind_y = ind_y

        self.plot()

    def fetch_data(self, path):
        """Open csv file and store its content in a numpy 2D array. If the file's data is already
            stored nothing is done.

            Note:
                The format of the data must be as follows
                LED1.r | LED1.c | LED2.r | LED2.c | LED3.r | LED3.c | LED4.r | LED4.c | Temp. | Time

            Args:
                path (str): Path to csv file that contains the data
        """

        if path == self._prev_path:
            return

        self._data = []

        with open(path, 'r') as csv_file:
            data_rows = csv.reader(csv_file)

            self._headers = data_rows.next()

            for row in data_rows:
                self._data.append(row)

        self._data = np.array(self._data)
        self._prev_path = path

    def plot(self):
        """Plots data contained in 'self._data_y' and 'self._data_x'"""

        self._axes.cla()
        self._axes.grid(True)
        self._axes.scatter(self._data_x, self._data_y,
                           c=self._data_colors, cmap='winter', edgecolors='none')
        self._axes.set_title('Plot')
        self._axes.set_xlabel(self.generate_label(self._ind_x))
        self._axes.set_ylabel(self.generate_label(self._ind_y))
        self._ctrl_curve = False
        self._ctrl_diff = False
        self._ctrl_stddev = False
        self._ctrl_ret = False
        self.mpl_toolbar.update()
                                # Update mpl_toolbar control variables to new
                                # plot

        self.draw()

    def parabolic_regression(self):
        """Apply parabolic regression, curve regression degree 2, and creates the plot legend"""

        if self.poly_curve_reg(2):
            self._axes.legend([Rectangle((0, 0), 0, 0, alpha=0.0)],
                              ['A = {0:.6f} *10^-6\nB = {1:.6f}\nC = {2:.6f}\nSD = {3:.6f}'
                              .format(
                                  self._fit_par[
                                      2] * 10.0**6, self._fit_par[
                                          1], self._fit_par[
                                              0], self._fit_std_dev)],
                              handlelength=0, fontsize=8).draggable(True)

            self.draw()

    def linear_regression(self):
        """Apply linear regression, curve regression degree 1, to data and calculates its
            coefficient of determination. Also creates the plot legend.
        """

        if self.poly_curve_reg(1):
            mean_y = np.mean(self._data_y)
            self._fit_r2 = 1.0 - \
                np.sum((self._predicted_y - self._data_y)**2) / \
                np.sum((self._data_y - mean_y)**2)

            self._axes.legend([Rectangle((0, 0), 0, 0, alpha=0.0)],
                              ['A = {0:.6f}\nB = {1:.4f}\nR^2 = {2:.2f}%\nSD = {3:.6f}'
                              .format(
                                  self._fit_par[
                                      1], self._fit_par[
                                          0], self._fit_r2 * 100.0, self._fit_std_dev)],
                              handlelength=0, fontsize=8).draggable(True)

            self.draw()

    def poly_curve_reg(self, n):
        """Fit a curve to the current data. If a fit is already active the initial plot will be restores.

            Args:
                n (int): Degree of the fitting polynomial

            Return:
                value (Bool): True if the curve was successfully fit, False otherwise
        """

        if len(self._data_y) == 0:
            # QMessageBox.question(self, 'Erro', 'Faltam dados',
            # QMessageBox.Ok, QMessageBox.Ok)

            return False

        if self._ctrl_curve == True:
            self.plot()

            return False

        self._fit_par = np.polyfit(self._data_x, self._data_y, n)[::-1]
        self.gen_poly_curve()
        self._ctrl_curve = True
        self._fit_std_dev = sqrt(
            np.sum((self._predicted_y - self._data_y) ** 2) / (len(self._data_y) - 1))
        self._axes.plot(self._data_x, self._predicted_y, 'r')

        self.draw()

        return True

    def gen_poly_curve(self):
        """Find the Y values of the curve fit correspondent to the X values of 'self._data_x'"""

        self._predicted_y = []

        for i, y in enumerate(self._data_y):
            self._predicted_y.append(0.0)

            for j, par in enumerate(self._fit_par):
                self._predicted_y[i] += par * self._data_x[i] ** j

        self._predicted_y = np.array(self._predicted_y)

    def hyperbolic_regression(self):
        """Fits a hyperbolic curve to the data.

            The format of the curve is:
                self._data_y = a / (self._data_x + b)

                where a and b are parameters found on gen_hyper_curve().
        """

        if len(self._data_y) == 0 or len(self._ind_y) < 2:
            print 'hue'
            # QMessageBox.question(self, 'Erro', 'Faltam dados',
            # QMessageBox.Ok, QMessageBox.Ok)

            return False

        if self._ctrl_curve == True:
            self.plot()

            return False

        a, b = self.gen_hyper_curve()

        self._ctrl_curve = True
        self._fit_std_dev = sqrt(
            np.sum((self._predicted_y - self._data_y) ** 2) / (len(self._data_y) - 1))
        self._axes.plot(self._data_x, self._predicted_y, 'r')

        self._axes.legend([Rectangle((0, 0), 0, 0, alpha=0.0)],
                          ['a = {0:.3f}\nb = {1:.4f}\nSD = {2:.6f}'
                          .format(a, b, self._fit_std_dev)],
                          handlelength=0, fontsize=8).draggable(True)

        self.draw()

    def gen_hyper_curve(self):
        """Find the parameters of the hyperbole that fits the data.

            The format of the data is:
                self._data_y = a / (self._data_x + b)

            What leads to:
                y = A*x + B, where:

                 y = 1 / self._data_y
                 x = self._data_x
                 A = 1 / a
                 B = b / a

            A and B are found with a linear regression and therefore a and b are determined.

            Return:
                 a (float): Parameter found on hyperbolic regression
                 b (float): Parameter found on hyperbolic regression
        """

        self._fit_par = np.polyfit(self._data_x, 1 / self._data_y, 1)[::-1]

        a = 1 / self._fit_par[1]
        b = a * self._fit_par[0]

        self._predicted_y = a / (self._data_x + b)

        return a, b

    def plot_stddev_fit(self):
        """Plot a few parallel lines to the one found with linear regression.

            The new lines correspond to the range covered by n standard deviations from the
            line fit to the data.
        """

        if not self._ctrl_curve:
            return

        if self._ctrl_stddev:
            self.plot()

            return

        self.add_stddev_curves(1)
        self.add_stddev_curves(2)
        self.add_stddev_curves(3)

        self._ctrl_stddev = True

        self.draw()

    def add_stddev_curves(self, n=1):
        """Add 2 line segments parallel to the line found on curve regression. The new segments are
            n standard deviations distant from the line fit to the data.

            Note:
                This method doesn't draw the lines in the canvas, it simply add them. They will appear
                when FigureCanvas.draw() is called.

            Args:
                n (int): The number of standard deviations of the distance of the line
        """

        color_array = ['m', 'c', 'y']

        self._axes.plot(
            self._data_x, self._predicted_y + n * self._fit_std_dev, color_array[n - 1])
        self._axes.plot(
            self._data_x, self._predicted_y - n * self._fit_std_dev, color_array[n - 1])

    def plot_diff_fit(self):
        """Plots the difference between predicted data and real data"""

        if not self._ctrl_curve or len(self._data_y) == 0:
            # QMessageBox.question(self, 'Erro', 'Falta fitar uma linha',
            # QMessageBox.Ok, QMessageBox.Ok)

            return

        self._ctrl_diff = not self._ctrl_diff

        if self._ctrl_diff == True:
            self._axes.cla()
            self._axes.grid(True)
            self._axes.plot(
                self._data_x, self._data_y - self._predicted_y, 'r.')
            self._axes.set_title('Plot')
            self._axes.set_xlabel('?')
            self._axes.set_ylabel('diferenca (px)')
            self.draw()
        else:
            self.plot()

    def remove_outliers(self, data_array):
        """Remove a parameterized number of extreme (max and min) values from data list.

            Args:
                data_array (list): Array with comparable values

            Return:
                array (numpy array): Values from input list without outliers grouped in an numpy array
        """

        for i in range(len(data_array) / OUTLIERS_RATIO):
            data_array.remove(max(data_array))
            data_array.remove(min(data_array))

        return np.array(data_array)

    def remove_points(self):
        """Remove points feature is activated or deactivated. Cursor shape and control variables
            change accordingly.

            When this feature is active these event handler methods are possibly enabled:
                cursor_enter_figure()
                cursor_press()
                cursor_motion()
                cursor_release()
        """

        if len(self._data_y) == 0:
            QMessageBox.question(
                self, 'Erro', 'Faltam dados', QMessageBox.Ok, QMessageBox.Ok)
            return

        if not self._is_removing_data:
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        else:
            QApplication.restoreOverrideCursor()

        self._is_removing_data = not self._is_removing_data

    def cursor_enter_figure(self, event):
        """If remove data feature is active the cursor shape feedback will be restored.

            Args:
                event (MPL Event): matplotlib event triggered when cursor enters figure
        """

        if self._is_removing_data:
            QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

    def cursor_press(self, event):
        """Stores data values corresponding to position of cursor press.

            Args:
                event (MPL Event): Event triggered when cursor is pressed
        """

        if self._is_removing_data:
            self._click_init_X, self._click_init_Y = self.get_point_data(event)
            self._ctrl_ret = True
            self._axes.add_patch(self._selection_ret)

    def cursor_motion(self, event):
        """If remove data feature is active and cursor ir pressed draws rectangle determined by
            the point of cursor press and current location

            Args:
                event (MPL Event): Event triggered when cursor moves in the Figure
        """

        if self._ctrl_ret:
            click_mv_X, click_mv_Y = self.get_point_data(event)

            self._selection_ret.set_xy(
                (self._click_init_X, self._click_init_Y))
            self._selection_ret.set_width(click_mv_X - self._click_init_X)
            self._selection_ret.set_height(click_mv_Y - self._click_init_Y)

            self.draw()

    def cursor_release(self, event):
        """If remove data feature is active removes data points inside the rectangle determined by
            cursor press and cursor release points.

            Args:
                event (MPL Event): Event triggered when cursor is released
        """

        if self._ctrl_ret:
            click_end_X, click_end_Y = self.get_point_data(event)

            indices = np.array([((not a) | (not b)) for (a, b) in zip(
                [(x >= min(self._click_init_X, click_end_X) and
                  x <= max(
                      self._click_init_X, click_end_X)) for x in self._data_x],
                [(y >= min(self._click_init_Y, click_end_Y) and
                  y <= max(self._click_init_Y, click_end_Y)) for y in self._data_y]
            )])

            self._data_x = self._data_x[indices]
            self._data_y = self._data_y[indices]
            self._data_colors = self._data_colors[indices]

            self._selection_ret.remove()
            self._ctrl_ret = False

            self.plot()

    def on_key_press(self, event):
        """implement the default mpl key press events"""

        key_press_handler(event, self, self.mpl_toolbar)

    def get_point_data(self, event):
        """Finds which data values correspond to the point correspondent to the event argument.
            If the click wasn't inside the canvas it will be converted to it.

            Figures referential has origin at bottom left edge, gray area.

            Args:
                event (MPL event): Event triggered by on the figure

            Return:
                value (float, float): Predicted values in the axis data based on point position in the figure
        """

        if event.xdata is not None:
            return (event.xdata, event.ydata)

        posx, posy = event.x, event.y

        initCoord = self._axes.transData.transform_point(
            [self._axes.get_xlim()[0], self._axes.get_ylim()[0]])
        endCoord = self._axes.transData.transform_point(
            [self._axes.get_xlim()[1], self._axes.get_ylim()[1]])

        # Manages cases when selection is out of bounds, outside of the canvas
        if posx > endCoord[0]:
            posx = endCoord[0]
        if posx < initCoord[0]:
            posx = initCoord[0]

        if posy > endCoord[1]:
            posy = endCoord[1]
        if posy < initCoord[1]:
            posy = initCoord[1]

        return (self._axes.get_xlim()[0]
                + (self._axes.get_xlim()[1] - self._axes.get_xlim()[0]) / (
                    endCoord[0] - initCoord[0])
                * (posx - initCoord[0]),
                self._axes.get_ylim()[0]
                + (self._axes.get_ylim()[1] - self._axes.get_ylim()[0]) / (
                    endCoord[1] - initCoord[1])
                * (posy - initCoord[1])
                )

    def generate_label(self, ind):
        """Generates coerent label to axis.

            If ind has two elements the distance between the LEDs, represented by these elements in 'self._data',
            will be plot. Otherwise the only value in ind represents the index in 'self._data' that should be plot.

            Args:
                ind (int): Array of indices in 'self._data' elements to generate label

            Return:
                label (str): Label correspondent to ind in 'self._data'
        """

        if len(ind) == 2:
            return 'dist led' + str(ind[0] / 2 + 1) + ' - led' + str(ind[1] / 2 + 1) + ' (px)'
        if ind[0] == 10:
            return 'posicao (microm)'
        if ind[0] == 9:
            return 'tempo (s)'

        return self._headers[ind[0]] + ' (px)'

if __name__ == '__main__':
    pass
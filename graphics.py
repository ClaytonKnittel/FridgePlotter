from PIL import ImageFont

from files import font_location
from methods import order_of_magnitude, convert, unit_display, get_unit_display, get_unitless_display, round_int
from times import Time
from math import log10


font = ImageFont.truetype(font_location, 30)

table_sig_figs = 3
line_width = 3

""" ImageDraw done from top left of screen """

bg_color = '#ffffff'
axis_color = '#969696'
graph_color = '#6dceab'
title_color = '#000000'
table_color = '#000000'
word_color = axis_color
cell_word_color = '#000000'

swid = 0
sheight = 0
line_method = lambda poses, fill=(0, 0, 0, 0xff), width=1: None
text_method = lambda pos, txt, font=None, fill=(0, 0, 0, 0xff): None


def configure_draw_parameters(width, height, line_method_, text_method_=None):
    global swid, sheight, line_method, text_method
    swid = width
    sheight = height
    line_method = line_method_
    if text_method_ is not None:
        text_method = text_method_


# an abstract representation of anything to be displayed on the .png image
#
# containts a location (as an ordered pair of floats ranging from 0.0 to 1.0),
# a width, and a height of the component
class ImageComponent:

    # floats from 0 to 1
    # pos is top left of object
    __pos = ()
    __width = 0
    __height = 0

    def __init__(self, p, w, h):
        self.__width = w
        self.__height = h
        self.__pos = p

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    # sets the width, height to dim[0], dim[1], respectively
    def set_size(self, dim):
        self.__width = dim[0]
        self.__height = dim[1]

    def get_x(self):
        return self.__pos[0]

    def get_y(self):
        return self.__pos[1]

    def get_pos(self):
        return self.__pos

    # adds the input tuple to this position
    def move(self, pos):
        self.__pos = (self.get_x() + pos[0], self.get_y() + pos[1])


# an ImageComponent that is capable of drawing text to the image. It also is capable
# of converting input numbers of a given unit into more readable units
class TextBox(ImageComponent):

    # the text to be drawn to the image
    __text = ""

    # True if this TextBox is the title of something, False otherwise
    __is_title = False

    # True if this TextBox is for data on the vertical axis, False otherwise
    __is_vertical_axis = False

    # True if this data is in a Table
    __is_cell = False

    # if this text is a number, this is the units that number is in
    __units = ""

    # pos is position on axis to which the text refers
    def __init__(self, text, pos, is_vertical_axis=False, is_title=False, is_cell=False, units=""):
        self.__units = units
        if not isinstance(text, str):
            self.__text = get_unit_display(text, units)
        else:
            self.__text = text
        # ImageComponent.__init__(self, pos, font.getsize(self.get_text_str())[0], font.getsize(self.get_text_str())[1])
        ImageComponent.__init__(self, pos, font.getsize(self.__text)[0], font.getsize(self.__text)[1])
        self.__is_title = is_title
        self.__is_cell = is_cell
        self.__is_vertical_axis = is_vertical_axis

    # updates the dimensions of the TextBox in the ImageComponent class. Called whenever the text
    # is changed
    def update_size(self):
        # self.set_size(font.getsize(self.get_text_str()))
        self.set_size(font.getsize(self.__text))

    # returns the text in this box as a string
    def get_text(self):
        return self.__text

    # if this TextBox is a number, it returns that number, otherwise returning 1
    def get_value(self):
        try:
            return float(self.__text)
        except ValueError:
            return 1

    @staticmethod
    def datetime_box(date, time, i):
        return TextBox("Data from " + date.to_string_display() + ' at ' +
                       Time.get_time_without_seconds(time) + '        ' +
                       'Chamber ' + str(convert(i)).replace('_', ' '),
                       (.5, .02), is_cell=True)

    # draws the TextBox to the Image img with the drawing strategy draw
    def draw(self, color=None):
        px, py = self.get_x() * swid, self.get_y() * sheight
        pos = []
        if self.__is_cell:
            pos.append(px - self.get_width() / 2)
            pos.append(py - self.get_height() / 2)
        elif self.__is_vertical_axis:
            pos.append(px - self.get_width() - .023 * swid)
            pos.append(py - self.get_height() / 2)
        else:
            pos.append(px - self.get_width() / 2)
            pos.append(py + self.get_height() * 1.5)

        if color is None:
            if self.__is_title:
                color = title_color
            elif self.__is_cell:
                color = cell_word_color
            else:
                color = word_color
        # text_method(pos, self.get_text_str(), font=font, fill=color)
        text_method(pos, self.__text, font=font, fill=color)

    # if the text is not a number, returns the text,
    # otherwise, if the units are 'numeral', returns an integer form of this number,
    # otherwise, if the units are something else, it returns the number scaled correctly (between 0.1 and 100)
    # with the scaled form of the units (i.e. mm, nm, or km),
    # othwerise, if the units are empty, it returns the scientific notation form of the number
    # def get_text_str(self):
    #     try:
    #         float(self.__text)
    #     except ValueError:
    #         return self.__text
    #     if self.__units == 'numeral':
    #         return str(int(float(self.__text)))
    #     text = float(self.__text)
    #     return get_unit_display(text, self.__units)


# either vertical or horizonal, Axis instances have a list of markings (the lines drawn on the axes
# to indicate fine measurements) and measures (the values of specifically chosen places on the axis).
#
# an Axis can also have units, and if so, it will scale the numbers on that axis to be shown in nicer
# terms (between 0.1 and 100) and will label the axis with the appropriate scaled units.
class Axis(ImageComponent):

    # list of ordered pairs (position (away from origin), length)
    __markings = []

    # list of ordered pairs (position (away from origin), value)
    __measures = []

    # True if this is the vertical axis, False otherwise
    __is_vertical_axis = False

    # the units of the numbers on this axis, if appropriate
    __units = ""

    # initializes an Axis
    def __init__(self, graph, pos, length, is_vertical_axis, axis_markings=8, axis_label="", units="", log_vals=False):
        self.__is_vertical_axis = is_vertical_axis
        if is_vertical_axis:
            x, y = .01, length
        else:
            x, y = length, .01
        ImageComponent.__init__(self, pos, x, y)
        self.__markings = []
        self.__measures = []

        if log_vals:
            self.__units = 'log ' + units
        else:
            self.__units = units

        self.__middle_val = graph.get_med_temp()

        # the desired number of axis markings to be shown. Should be a power of 2
        self.__num_axis_markings = axis_markings
        self.__define_axis_markings(graph)

        if axis_label != "":
            self.__create_label(axis_label, log_vals, True)

    # creates a label at the top, if vertical axis, or bottom, if horizonal axis, to
    # indicate what measure is being displayed
    def __create_label(self, label, log_vals, is_title=False):
        if self.__is_vertical_axis:

            if log_vals:
                text = "log " + label
            else:
                text = label + ' (' + unit_display(self.__middle_val, self.__units) + ')'

            self.__add_measure_text(text,
                                    (self.get_x() + len(text) * .005, self.get_y() - self.get_height() * 1.03),
                                    is_title)

    def __define_axis_markings(self, graph):
        if self.__is_vertical_axis:
            min_temp, max_temp = graph.get_min_max_temp()
            # print(min_temp, max_temp)

            try:
                start, stop, increment, mark_increment = self.__find_nice_measure_vals(min_temp, max_temp)
            except ZeroDivisionError:
                print('min value and max value the same: ' + str(min_temp) + " " + str(max_temp))
                start, stop, increment, mark_increment = 0, 1, .1, 1
            # print(start, stop)

            x = 0
            while start + x * increment < stop:
                if max_temp >= start + x * increment >= min_temp:
                    self.__add_mark(start + x * increment, max_temp, min_temp, mark_increment)
                x += 1
        else:
            max_time = graph.get_max_time()
            min_time = graph.get_min_time()
            if min_time == max_time:
                max_time *= 1.3
                min_time /= 2
            start, stop, increment, mark_increment = self.__find_nice_time_vals(min_time, max_time)

            x = 0
            while start + x * increment < stop:
                if max_time >= start + x * increment >= min_time:
                    self.__add_mark_t(start + x * increment, mark_increment, max_time, min_time)
                x += 1

    # adds a mark to the Axis with the given value, ordinal (of axis markings),
    # max value, and min value on this axis
    def __add_mark(self, value, maxx, minn, mark_increment):
        length = 2
        idiv = round_int(value / mark_increment)
        div = value / mark_increment
        if abs(idiv - div) < .000001:
            if idiv & 1 == 0:
                length = 8
            else:
                length = 5
            self.__add_measure(value, minn, maxx)

        self.__markings.append(((value - minn) / (maxx - minn), length))

    def __add_mark_t(self, value, mark_increment, maxx, minn):
        length = 1
        v = value / mark_increment
        if v == int(v):
            length = 4
        elif int(v * 2) == v * 2 or int(v * 3) == v * 3 or int(v * 5) == v * 5:
            length = 2

        if length == 4:
            self.__add_measure(value, minn, maxx)
        length += 2

        self.__markings.append(((value - minn) / (maxx - minn), length))

    # adds a measure label at the given value. Works similarly to __add_mark.
    #
    # if is_title, the color of the text will be title_color rather than word_color
    def __add_measure(self, value, minn=0, maxx=1, is_title=False):
        # need * self.get_height() because textboxes have absolute coordinates, while marks are drawn in
        # the axis draw method, and are thus drawn with respect to the axis
        if self.__is_vertical_axis:
            # print(value, self.__units, self.__middle_val)
            self.__add_measure_text(get_unitless_display(value, self.__units, dummy_value=self.__middle_val),
                                    (self.get_x(), self.get_y() - ((value - minn) / (maxx - minn))
                                    * self.get_height()), is_title)
        else:
            value = self.__round_mod_60(value)
            self.__add_measure_text(Time.get_time_without_seconds(value), (self.get_x() + (value - minn) /
                                                                           (maxx - minn) * self.get_width(),
                                                                           self.get_y()), is_title)

    # adds the text at position pos to the list of measures
    def __add_measure_text(self, text, pos, is_title=False):
        self.__measures.append(TextBox(text, pos, self.__is_vertical_axis, is_title))

    # rounds this number to the nearest multiple of 60
    @staticmethod
    def __round_mod_60(val):
        difference = val % 60
        val -= difference
        if difference >= 30:
            val += 60
        return val

    # finds nice places to start and stop measuring on the vertical axis,
    # given the minimum and maximum value on the vertical axis
    # returns start, stop, increment size, div (ones, twos, fives)
    def __find_nice_measure_vals(self, minval, maxval):
        if minval == 0 and maxval == 0:
            return -.1, .9, .1, True, True

        d = maxval - minval
        mod = 10 / order_of_magnitude(d)
        start = Axis.downmod(minval, mod)
        end = Axis.upmod(maxval, mod)

        factors = (2, 2, 1.25, 2)
        s = len(factors)
        i = 0
        increment = mod

        while Axis.num_between(minval, maxval, increment) < 2 * self.__num_axis_markings:
            increment /= factors[i]
            i = Axis.__incr_mod(i, s)

        mark_increment = 5 * increment

        return start, end, increment, mark_increment

    @staticmethod
    def upmod(num, mod):
        if num < 0:
            return -Axis.downmod(-num, mod)
        low = int(num / mod) * mod
        if num - low == 0:
            return num
        return low + mod

    @staticmethod
    def downmod(num, mod):
        if num < 0:
            return -Axis.upmod(-num, mod)
        return int(num / mod) * mod

    # finds nice places to start and stop measuring on the horizontal axis,
    # given the first and last time of measurement of the data being displayed
    # on this Graph
    def __find_nice_time_vals(self, min_time, max_time):
        mod = 1
        d = max_time - min_time
        while mod < d:
            if mod < 3600:
                mod *= 60
            else:
                mod *= 12

        start = Axis.downmod(min_time, mod)
        stop = Axis.upmod(max_time, mod)

        factors_a = [2, 2, 3]
        factors_b = [2, 1.5, 2, 2, 2.5, 2]
        i = 0
        increment = mod
        la = len(factors_a)
        lb = len(factors_b)

        while Axis.num_between(min_time, max_time, increment) < 1.2 * self.__num_axis_markings:
            if increment > 3600:
                increment /= factors_a[i]
                i = Axis.__incr_mod(i, la)
            else:
                increment /= factors_b[i]
                i = Axis.__incr_mod(i, lb)

        if increment < 3600:
            if i == 1 or i == 4:
                mark_increment = 4 * increment
            elif i == 2 or i == 3:
                mark_increment = 3 * increment
            else:
                mark_increment = 5 * increment
        else:
            if i == 1 or i == 2:
                mark_increment = 4 * increment
            else:
                mark_increment = 3 * increment

        return start, stop, increment, mark_increment

    @staticmethod
    def __incr_mod(i, mod):
        if i == mod - 1:
            return 0
        return i + 1

    @staticmethod
    def num_between(minn, maxx, increment):
        m = int(minn / increment) * increment
        c = 0
        while m < maxx:
            c += 1
            m += increment
        return c

    # draws this axis and all labels associated with it
    def draw(self):
        w = swid
        h = sheight
        position = (self.get_x() * w, self.get_y() * h)

        for x in self.__measures:
            x.draw()

        if self.__is_vertical_axis:
            for x in self.__markings:
                line_method([(position[0] - 4 * x[1], position[1] - h * self.get_height() * x[0]),
                            (position[0], position[1] - h * self.get_height() * x[0])],
                            fill=axis_color, width=line_width)
        else:
            pass
            for x in self.__markings:
                line_method([(position[0] + w * self.get_width() * x[0], position[1]),
                            (position[0] + w * self.get_width() * x[0], position[1] + 4 * x[1])],
                            fill=axis_color, width=line_width)


# each Graph contains a list of output values (temperature in this case), a tuple of axes,
# a value for the width of the data function being drawn, and a proportion of the graph
# to be left blank between the minimum value and the x-axis
class Graph(ImageComponent):

    # a list of all output data (time of recording and value)
    __outputs = []

    # a tuple of Axis instances (one vertical and one horizontal)
    __axes = ()

    # the width of the function visualizing the data on the graph
    __graph_width = 1

    # the proportion of the graph to be left blank between the minimum value and the x-axis
    distance_between_min_and_x_axis = .12

    def __init__(self, data, pos, x, y, axis_label='', units='', graph_width=1, log_vals=False):
        ImageComponent.__init__(self, pos, x, y)
        if log_vals:
            x = 0
            while x < len(data):
                try:
                    data[x].act(abs)
                    data[x].act(log10)
                    x += 1
                except ValueError:
                    data = data[:x] + data[x + 1:]

        if len(data) == 0:
            raise Exception('Cannot have an output list of size 0')

        self.__outputs = data
        self.__define_axes(axis_label, units, log_vals)
        self.__graph_width = graph_width

    # initializes a Graph instance
    @staticmethod
    def fromfile(fridgefile, pos, x, y, graph_width=1, log_vals=False):
        output_list = fridgefile.get_outputs()

        axis_label, units = '', ''
        if fridgefile.data_type() == 'T':
            axis_label = 'Temperature'
            units = 'K'
        elif fridgefile.data_type() == 'maxigauge':
            axis_label = 'Pressure'
            units = 'bar'
        elif fridgefile.data_type() == 'Flowmeter':
            axis_label = 'Flowmeter'
            units = 'mol/s'

        return Graph(output_list, pos, x, y, axis_label=axis_label,
                     units=units, graph_width=graph_width, log_vals=log_vals)

    # creates the vertical and horizontal axis for this Graph
    def __define_axes(self, axis_label, units, log_vals):
        self.__axes = (Axis(self, (self.get_pos()[0], self.get_pos()[1] + self.get_height()), self.get_width(), False),
                       Axis(self, (self.get_pos()[0], self.get_pos()[1] + self.get_height()), self.get_height(), True,
                            axis_label=axis_label, units=units, log_vals=log_vals))

    # returns the absolute position of the left side of this Graph
    def xleft(self):
        return swid * self.get_x()

    # returns the absolute position of the top of this Graph
    def ytop(self):
        return sheight * self.get_y()

    # returns the absolute position of the right side of this Graph
    def xright(self):
        return self.xleft() + self.width()

    # returns the absolute position of the bottom of this Graph
    def ybottom(self):
        return self.ytop() + self.height()

    # returns the absolute width of this Graph
    def width(self):
        return swid * self.get_width()

    # returns the absolute height of this Graph
    def height(self):
        return sheight * self.get_height()

    # returns position of x'th temperature reading along the x-axis
    def get_x_position_in_range(self, x, max_time, min_time):
        if max_time == min_time:
            return .5
        return (self.__outputs[x].get_time().get_time() - min_time) / (max_time - min_time)

    # returns the x-coordinate of some data point measured at time t, given the max and min time on
    # the horizontal axis and the width w of the image
    def get_x_coord(self, t, max_time, min_time):
        return self.xleft() + self.width() * self.get_x_position_in_range(t, max_time, min_time)

    # draws this Graph
    def draw(self):
        minn, maxx = self.get_min_max_temp()
        den = self.height() / (maxx - minn)

        self.drawborders()
        for axis in self.__axes:
            axis.draw()
        points = []

        max_time = self.get_max_time()
        min_time = self.get_min_time()

        for x in range(0, len(self.__outputs)):
            pt = (self.get_x_coord(x, max_time, min_time), self.ybottom()
                  - ((self.__outputs[x].get_value() - minn) * den))
            points.append(pt)

        for x in range(0, len(points) - 1):
            line_method([points[x], points[x + 1]], fill=graph_color, width=self.__graph_width)

    # draws the borders of the graph, assuming the origin is (p1.x, p2.y), where
    # w and h are Image width and height
    def drawborders(self):
        line_method([(self.xleft(), self.ytop()), (self.xleft(), self.ybottom())], fill=axis_color, width=line_width)
        line_method([(self.xleft(), self.ybottom()),
                    (self.xright(), self.ybottom())], fill=axis_color, width=line_width)

    def get_min_max_temp(self):
        mine = self.__get_min_temp()
        maxe = self.__get_max_temp()
        if mine == maxe:
            if mine == 0:
                maxe = 1
            elif maxe < 0:
                maxe *= 4 / 5
            else:
                maxe *= 5 / 4

        mine -= (maxe - mine) / (1 / Graph.distance_between_min_and_x_axis - 1)
        return mine, maxe

    # returns the maximum temperature value displayed on this graph
    def __get_max_temp(self):
        maximum = self.__outputs[0].get_value()
        for x in self.__outputs:
            if maximum < x.get_value():
                maximum = x.get_value()
        return maximum

    # returns the minimum temperature value displayed on this graph
    def __get_min_temp(self):
        minimum = self.__outputs[0].get_value()
        for x in self.__outputs:
            if minimum > x.get_value():
                minimum = x.get_value()
        return minimum

    def get_med_temp(self):
        return self.__outputs[int(len(self.__outputs) / 2)].get_value()

    # returns the time the last data point was recorded
    def get_max_time(self):
        return self.__outputs[-1].get_time().get_time()

    # returns the time the first data point was recorded
    def get_min_time(self):
        return self.__outputs[0].get_time().get_time()


# each Table has a list of cells, each of which are a TextBox
class Table(ImageComponent):

    # a 2-dimensional list of TextBoxes
    __cells = ()

    # initializes the table
    def __init__(self, pos, x, y, column_titles, row_titles, column_units, data):
        ImageComponent.__init__(self, pos, x, y)
        self.__create_table(column_titles, row_titles, column_units, data)

    # creates the table, given the titles of both columns and rows (optional), and
    # the data, a 2-dimensional list
    def __create_table(self, column_titles, row_titles, column_units, data):
        cells = []
        for x in column_titles:
            cells.append([])
            cells[len(cells) - 1].append(x)
        for y in row_titles:
            cells[0].append(y)
        if len(row_titles) == 0:
            for x in data:
                cells[0].append(x)
        else:
            for y in range(0, len(cells) - 1):
                for x in data[y]:
                    cells[y + 1].append(x)
        self.__create_textbox_cells(cells, column_units)

    # fills the __cells variable with all of the Table data
    def __create_textbox_cells(self, cells, column_units):
        dcol = self.get_width() / len(cells)
        drow = self.get_height() / len(cells[0])
        cell_tuple = []
        for column in range(0, len(cells)):
            cell_tuple.append([])
            for row in range(0, len(cells[column])):
                cell_tuple[len(cell_tuple) - 1].append(TextBox(
                    cells[column][row], (self.get_x() + (column + .5) * dcol,
                                         self.get_y() + (row + .5) * drow),
                    is_cell=True, units=column_units[column]))
        self.__cells = tuple(cell_tuple)

    # draws this table to the image with drawing strategy draw
    def draw(self):
        xs = swid * self.get_x()
        ys = sheight * self.get_y()
        dx = swid * self.get_width() / len(self.__cells)
        dy = sheight * self.get_height() / len(self.__cells[0])

        for y in range(0, len(self.__cells[0]) + 1):
            line_method([(xs, ys + y * dy), (xs + dx * len(self.__cells), ys + y * dy)], fill=table_color, width=2)
        for x in range(0, len(self.__cells) + 1):
            line_method([(xs + x * dx, ys), (xs + x * dx, ys + dy * len(self.__cells[0]))], fill=table_color, width=2)

        for x in self.__cells:
            for y in x:
                y.draw()

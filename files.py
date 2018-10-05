from times import Time, Date
from getpass import getuser


file_type = ''
location = ''
save_to_location = ''
font_location = ''

lab_computer = getuser()

blue = 'Dian'
black = 'murchlab'
tester = 'claytonknittel'


def define_locations(lab_comp):
    global file_type
    global location
    global save_to_location
    global font_location
    if lab_comp == blue:
        file_type = '.log'
        location = 'Z:/FridgeLog/'
        save_to_location = 'Z:/FridgeLog/'
        font_location = 'C:/Users/Dian/Documents/CenturyGothic.ttf'
    elif lab_comp == black:
        file_type = '.log'
        location = 'Z:/FridgeLogB/'
        save_to_location = 'Z:/FridgeLogB/'
        font_location = 'C:/Users/murchlab/Desktop/fridgeprograms/CenturyGothic.ttf'
    else:
        file_type = '.txt'
        location = '/Users/claytonknittel/PycharmProjects/practice/LOG/'
        save_to_location = '/Users/claytonknittel/downloads/'
        font_location = '/Users/claytonknittel/PycharmProjects/practice/CenturyGothic.ttf'


define_locations(lab_computer)


graph_time = 60 ** 2 * 12


# represents one line from the data stored in LOG.
# each OutputLine has the date, time, and value of the
# data being recorded.
class OutputLine:

    __time = None
    __value = 0

    def __init__(self, output, data_type, chamber):
        s = output.split(',')
        if data_type == 'T' or data_type == 'P':
            self.__time = Time(str(s[1]))
            self.__value = self.__create_temp(str(s[2]))
            if self.__value < 0:
                print(self.__value)
        else:
            self.__time = Time(str(s[1]))
            self.__value = 0.001*self.__create_temp(str(s[6 * chamber - 1])[1:])

    @staticmethod
    def __create_temp(temp):
        try:
            return float(temp)
        except ValueError:
            print("-" + str(temp) + "-")
            exit(0)

    def get_time(self):
        return self.__time

    def get_value(self):
        return self.__value

    def add_n_days(self, n):
        self.__time.add_n_days(n)

    def act(self, funct):
        self.__value = funct(self.__value)

    def tostring(self):
        return self.__time.tostring() + ' ' + str(self.__value)


# FridgeFile stores information about where files are stored that are to be read,
# and it can return the outputs from a given file in the form of a list of OutputLines
class FridgeFile:

    # the day from which the data will be read
    __date = ''

    # either 'T', 'R', or 'P', which is the type of data to be read from the given chamber
    __data_type = ''

    # the chamber (1 - 6) where this data is from
    __chamber = 0

    # the File in the location of the given fridge log data
    __file = None

    # a list of OutputLines in this File
    __outputs = None

    # a list of strings that are from the .log files in LOG
    __read_lines = None

    def __init__(self, date, data_type='T', chamber=0):
        if isinstance(date, Date):
            self.__date = date.tostring()
        else:
            self.__date = date
        self.__data_type = data_type
        self.__chamber = chamber
        self.__file = None
        self.__outputs = None

    def data_type(self):
        return self.__data_type

    # opens this File
    def open(self):
        self.__file = open(self.tostring(), 'r')

    # closes this File
    def close(self):
        self.__file.close()

    # reads the data from this File and stores it in __read_lines
    def readlines(self):
        if self.__read_lines is None:
            self.__read_lines = self.__file.readlines()
        return self.__read_lines

    # returns the last measurement recorded on this day
    def get_last_measurement(self):
        try:
            outputs = self.get_outputs(self.__chamber)
            return outputs[-1].get_value()
        except IndexError:
            return 0

    # returns the time of the last measurement recorded
    def get_last_measurement_time(self):
        try:
            outputs = self.get_outputs()
            return outputs[-1].get_time().get_time()
        except IndexError:
            return 0

    # returns whether or not more files will need to be open (because the data
    # trying to be read extends before the beginning of this day)
    def is_first_measurement_time_yesterday(self):
        outputs = self.get_outputs()
        return outputs[-1].get_time().get_time() <= graph_time

    # returns the list of OutputLines created from the data in this file
    def __get_outputs(self, chamber):
        outputs = []
        for x in self.readlines():
            outputs.append(OutputLine(x, self.__data_type, chamber=chamber))
        return outputs

    # returns a specific selection of OutputLines from __output_lines
    def get_outputs(self, from_time=0, to_time=Time.seconds_in_day(), add_n_days=0):
        if self.__outputs is None or self.__chamber > 0:
            self.__outputs = self.__get_outputs(self.__chamber)
        ret = []
        for x in range(0, len(self.__outputs)):
            if from_time <= self.__outputs[x].get_time().get_time() + add_n_days * Time.seconds_in_day() <= to_time:
                val = self.__outputs[x]
                val.add_n_days(add_n_days)
                ret.append(val)
        return ret

    # returns this FridgeFile's file location
    def tostring(self):
        if self.__data_type == 'T' or self.__data_type == 'P':
            return FridgeFile.temp_string(self.__date, self.__data_type, self.__chamber)
        else:
            return FridgeFile.maxi_string(self.__date, self.__data_type)

    # returns the file location of the data from day date in chamber chamber
    # of type data_type
    @staticmethod
    def maxi_string(date, dtype):
        return location + date + '/' + dtype + ' ' + date + file_type

    @staticmethod
    def temp_string(date, dtype, chamber):
        return location + date + '/CH' + str(chamber) + ' ' + dtype + ' ' + date + file_type


class DynamicFile:

    def __init__(self, date, data_type, chamber, graphtime=graph_time, scale_nums=0):
        self.__files = []
        self.__last_record = 0
        self.__last_measurement = 0
        self.__graph_time = graphtime
        self.__load_all(date, data_type, chamber, lambda n: self.__criteria_helper(n), 0)
        self.__files.reverse()
        self.__scale = scale_nums

    def is_empty(self):
        return len(self.__files) == 0

    def __repr__(self):
        if self.is_empty():
            return 'empty dynamic file'
        return self.__files[-1].tostring()

    def __criteria_helper(self, n):
        if n == 0:
            return True
        return self.__last_record - self.__graph_time < 0

    def __load_all(self, date, data_type, chamber, criteria_function, n):
        while criteria_function(n):
            try:
                self.__files.append(FridgeFile(date.get_n_days_ago(n), data_type=data_type, chamber=chamber))
                self.__files[-1].open()
                if n == 0:
                    self.__last_record = self.__files[0].get_last_measurement_time()
                    self.__last_measurement = self.__files[0].get_last_measurement()
                else:
                    self.__last_record += Time.seconds_in_day()
                n += 1
            except FileNotFoundError:
                self.__files = self.__files[:-1]
                return

    def data_type(self):
        return self.__files[-1].data_type()

    def get_last_measurement_time(self):
        return self.__last_record

    def get_last_measurement(self):
        return self.__last_measurement

    def open(self):
        for file in self.__files:
            try:
                file.open()
            except IOError:
                print(str(file) + ' not found')

    def close(self):
        for file in self.__files:
            try:
                file.close()
            except IOError:
                pass

    def get_outputs(self):
        outputs = []
        n = 0
        for file in self.__files:
            outputs.extend(file.get_outputs(from_time=self.__last_record - self.__graph_time,
                                            to_time=self.__last_record, add_n_days=n))
            n += 1
        for o in outputs:
            o.act(lambda x: x * (1000 ** self.__scale))
        return outputs

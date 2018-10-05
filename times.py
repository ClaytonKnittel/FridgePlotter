

# a Date stores a list [year, month, day]
class Date:

    __date = []
    __days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__(self, date):
        self.__date = []
        s = date.split('-')
        if len(s) == 0:
            raise IOError("No temperature log files were found")
        self.__date.append((int(s[0]) % 100) + 2000)
        self.__date.append(int(s[1]))
        self.__date.append(int(s[2][:2]))

    def __repr__(self):
        return self.tostring()

    def __copy__(self):
        return Date(self.tostring())

    def get_date(self):
        return self.__date

    def get_day(self):
        return self.__date[2]

    def get_month(self):
        return self.__date[1]

    def get_year(self):
        return self.__date[0] % 100

    @staticmethod
    def num_string(n):
        if n < 10:
            p = '0'
        else:
            p = ''
        return p + str(n)

    def is_later(self, date):
        if self.get_year() == date.get_year():
            if self.get_month() == date.get_month():
                return self.get_day() >= date.get_day()
            return self.get_month() > date.get_month()
        return self.get_year() > date.get_year()

    def get_days_in_month(self, month, year):
        if month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return self.__days_in_month[month - 1] + 1
        return self.__days_in_month[month - 1]

    def subtract(self):
        if self.get_day() == 1:
            self.__date[1] -= 1
            if self.get_month() == 0:
                self.__date[1] = 12
                self.__date[0] -= 1
            self.__date[2] = self.get_days_in_month(int(self.__date[1]), int(self.__date[0]))
            return
        self.__date[2] -= 1

    # returns a new Date that is n days before this one
    def get_n_days_ago(self, n):
        new_date = Date(self.get_full_date())
        while n > 0:
            new_date.subtract()
            n -= 1
        return new_date

    # returns a string representation of this Date in the format 'yyyy-mm-dd'
    def get_full_date(self):
        return str(self.__date[0]) + '-' + str(self.__date[1]) + '-' + str(self.__date[2])

    # returns a string representation of this Date in the format 'yy-mm-dd'
    def tostring(self):
        return Date.num_string(self.get_year()) + '-' + Date.num_string(self.get_month())\
               + '-' + Date.num_string(self.get_day())

    # returns a string representation of this Date in the format 'Month day, year'
    def to_string_display(self):
        year = str(self.__date[0])
        if self.get_month() == 1:
            month = 'January'
        elif self.get_month() == 2:
            month = 'February'
        elif self.get_month() == 3:
            month = 'March'
        elif self.get_month() == 4:
            month = 'April'
        elif self.get_month() == 5:
            month = 'May'
        elif self.get_month() == 6:
            month = 'June'
        elif self.get_month() == 7:
            month = 'July'
        elif self.get_month() == 8:
            month = 'August'
        elif self.get_month() == 9:
            month = 'September'
        elif self.get_month() == 10:
            month = 'October'
        elif self.get_month() == 11:
            month = 'November'
        else:
            month = 'December'
        if self.get_day() % 10 == 1 and self.get_day() != 11:
            d = 'st'
        elif self.get_day() % 10 == 2 and self.get_day() != 12:
            d = 'nd'
        elif self.get_day() % 10 == 3 and self.get_day() != 13:
            d = 'rd'
        else:
            d = 'th'
        return month + ' ' + str(self.get_day()) + d + ', ' + year


# stores a time as an integer representing the number of seconds past 12:00 am it is
class Time:

    __time = 0

    def __init__(self, timedata):
        self.__time = self.__create_time(timedata)

    # takes in a string of the time as stored in the LOG files
    # in the format hr:min:sec
    @staticmethod
    def __create_time(timedata):
        splitnums = timedata.split(':')
        s = []
        for x in range(0, len(splitnums)):
            s.append(float(splitnums[x]))
        return Time.get_time_from_array(s)

    # returns the time in seconds past midnight
    def get_time(self):
        return self.__time

    # returns the time in seconds past midnight from an array of the form
    # [hour, minutes, seconds]
    @staticmethod
    def get_time_from_array(times):
        return int(times[2] + 60 * (times[1] + 60 * (times[0])))

    # returns 'am' or 'pm' based on the time of day the input (in seconds) is
    # referring to
    @staticmethod
    def is_morning(seconds):
        if seconds % Time.seconds_in_day() < 12 * (60 ** 2):
            return "am"
        return "pm"

    # returns the hour (1-12) as a string
    def __get_hour_string(self):
        return str(Time.get_hour(self.__time))

    # adds n days to this Time (used for the Graph when multiple days are being represented)
    def add_n_days(self, n):
        self.__time += n * Time.seconds_in_day()

    # returns the hour (1-12) of an input number of seconds, as an integer
    @staticmethod
    def get_hour(seconds):
        return int((seconds // (60 ** 2) + 11) % 12 + 1)

    # returns the minutes (1-60) of an input time as a string
    @staticmethod
    def get_minutes(seconds):
        return Time.__get_time_string((seconds // 60) % 60)

    # returns the seconds (1-60) of an input time as a string
    @staticmethod
    def get_seconds(seconds):
        return Time.__get_time_string(seconds % 60)

    # used to format times as strings. If the input is less than 10,
    # it returns '0' plus the number, otherwise it just returns the number
    # i.e. __get_time_string(4) returns '04' and __get_time_string(44) returns '44'
    @staticmethod
    def __get_time_string(num):
        if num >= 10:
            return str(int(num))
        return "0" + str(int(num))

    # returns this Time as a string in the form 'hr:min.sec'
    def tostring(self):
        return Time.get_time_from_seconds(self.__time)

    # returns this Time as a string in the form 'hr:min.sec'
    @staticmethod
    def get_time_from_seconds(seconds):
        pod = Time.is_morning(seconds)
        return str(Time.get_hour(seconds)) + ":" + str(Time.get_minutes(seconds))\
            + "." + str(Time.get_seconds(seconds)) + " " + pod

    # returns the given seconds as a string in the form 'hr:min'
    @staticmethod
    def get_time_without_seconds(seconds):
        pod = Time.is_morning(seconds)
        return str(Time.get_hour(seconds)) + ":" + str(Time.get_minutes(seconds)) + " " + pod

    # returns the number of seconds in a day
    @staticmethod
    def seconds_in_day():
        return (60 ** 2) * 24

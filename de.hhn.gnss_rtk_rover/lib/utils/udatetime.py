"""
Concrete date/time and related types.

Minimalist Micropython implementation of the CPython
datetime.py module

Totally incomplete, as only the necessary functions, which are needed
by this project were implemented. Feel free to extend this module

Created on 10 Sep 2022

:author: vdueck
"""


class Utime:
    """Simple Class representing time"""

    __slots__ = '_hour', '_minute', '_second', '_msecond'

    def __init__(self, hour=0, minute=0, second=0, msecond=0):
        """Constructor.

        Creates a new uTime object.

        :param int hour:        current hour (0-23)
        :param int minute:      current minute (0-60)
        :param int second:      current second (0-60)
        :param int msecond: current millisecond (0-99)
        :raises: UtimeParseError

        """
        # Check if input is valid
        if hour not in range(0, 24):
            raise UtimeParseError(
                "Incorrect input for hour. Given {}, but must be 0 - 23.".format(hour))
        if minute not in range(0, 60):
            raise UtimeParseError(
                "Incorrect input for minute. Given {}, but must be 0 - 60.".format(minute))
        if second not in range(0, 60):
            raise UtimeParseError(
                "Incorrect input for second. Given {}, but must be 0 - 60.".format(second))
        if hour not in range(0, 24):
            raise UtimeParseError(
                "Incorrect input for millisecond. Given {}, but must be 0 - 99.".format(msecond))

        self._hour = hour
        self._minute = minute
        self._second = second
        self._msecond = msecond

    def __repr__(self):
        """Convert to formal string, for repr()."""
        if self._msecond != 0:
            s = ", %d, %d" % (self._second, self._msecond)
        elif self._second != 0:
            s = ", %d" % self._second
        else:
            s = ""
        s = "%s.%s(%d, %d%s)" % (self.__class__.__module__,
                                 self.__class__.__qualname__,
                                 self._hour, self._minute, s)
        return s

    def __str__(self):
        """Return the time formatted according to ISO.

        The full format is 'HH:MM:SS.mmmmmm+zz:zz'. But here its simplistic:
        'HH:MM:SS.mmmm'

        """
        hours = "%02d" % (self._hour,)
        minutes = "%02d" % (self._minute,)
        seconds = "%02d" % (self._second,)
        millis = "%04d" % (self._msecond,)
        s = hours + ":" + minutes + ":" + seconds + "." + millis
        return s

    # Read-only field accessors
    @property
    def hour(self):
        """hour (0-23)"""
        return self._hour

    @property
    def minute(self):
        """minute (0-59)"""
        return self._minute

    @property
    def second(self):
        """second (0-59)"""
        return self._second

    @property
    def millisecond(self):
        """millisecond (0-9999)"""
        return self._msecond

    @classmethod
    def timeFromNmeaString(cls, nmeastr: str):
        """Create Utime object from given nmea time string

        :param str nmeastr: time string from NMEA Sentence hhmmss.ss
        :return: uTime object
        :rtype: Utime
        :raises: UtimeParseError
        """

        # check if string is not empty
        if not nmeastr:
            return Utime(0, 0, 0, 0)
        # split by dot
        pieces = nmeastr.split(".")
        print(nmeastr)
        if len(pieces) != 2:
            raise UtimeParseError("Invalid NMEA time string, could not separate millis")

        pieces_str = "%06d" % int(pieces[0])

        if len(pieces[1]) != 2 or len(pieces_str) != 6:
            raise UtimeParseError("Invalid NMEA time string, wrong length")


        # split hours, minutes and seconds
        hours = int(pieces_str[0:2])
        minutes = int(pieces_str[2:4])
        seconds = int(pieces_str[4:6])

        if len(pieces[1]) == 1:
            millis_int = int(pieces[1])
            m_temp = "%01d" % millis_int
            millis = int(m_temp + "000")
        if len(pieces[1]) == 2:
            millis_int = int(pieces[1])
            m_temp = "%02d" % millis_int
            millis = int(m_temp + "00")
        if len(pieces[1]) == 3:
            millis_int = int(pieces[1])
            m_temp = "%03d" % millis_int
            millis = int(m_temp + "0")
        if len(pieces[1]) == 4:
            millis = int(pieces[1])

        return Utime(hours, minutes, seconds, millis)

    def nmeaStringFromUtime(self) -> str:
        """Create NMEA time string from Utime object

        :return: time string as used in NMEA Sentence (hhmmss.ss)
        :rtype: str
        """

        hours = "%02d" % (self._hour,)
        minutes = "%02d" % (self._minute,)
        seconds = "%02d" % (self._second,)
        millisraw = "%04d" % (self._msecond,)
        millis = millisraw[0:2]

        return hours + minutes + seconds + "." + millis


class Udate:
    """
    Simple Class representing date
    Is not checking for incorrect dates -> invalid dates are possible (e.g. 31.02.2022)
    """

    __slots__ = '_year', '_month', '_day'

    def __init__(self, year=2000, month=1, day=1):
        """Constructor.

        Creates a new Udate object.

        :param int year:        current hour (1000 - 3000)
        :param int month:      current minute (1 -12)
        :param int day:      current day (1 - 31)
        :raises: UtimeParseError

        """
        # Check if input is valid
        if year not in range(1000, 3000):
            raise UtimeParseError(
                "Incorrect input for year. Given {}, but must be 1000 - 3000.".format(year))
        if month not in range(1, 12):
            raise UtimeParseError(
                "Incorrect input for month. Given {}, but must be 1 -12.".format(month))
        if day not in range(1, 31):
            raise UtimeParseError(
                "Incorrect input for second. Given {}, but must be 1 -31.".format(day))

        self._year = year
        self._month = month
        self._day = day

    def __repr__(self):
        """Convert to formal string, for repr()."""

        s = "%s.%s(%d, %d, %d)" % (self.__class__.__module__,
                                   self.__class__.__qualname__,
                                   self._year, self._month, self._day)
        return s

    def __str__(self):
        """Return the date formatted like yyyy-mm-dd"""

        years = "%04d" % (self._year,)
        months = "%02d" % (self._month,)
        days = "%02d" % (self._day,)
        s = years + "-" + months + "-" + days
        return s

    # Read-only field accessors
    @property
    def year(self):
        """hour (1000-3000)"""
        return self._year

    @property
    def month(self):
        """minute (1-12)"""
        return self._month

    @property
    def day(self):
        """second (1-31)"""
        return self._day

    @classmethod
    def dateFromNmeaString(cls, nmeastr: str):
        """Create Udate object from given nmea time string

        :param str nmeastr: date string from NMEA Sentence yymmdd
        :return: Udate object
        :rtype: Udate
        :raises: UtimeParseError
        """

        # split years, months and days
        years = 2000 + int(nmeastr[0:2])
        months = int(nmeastr[2:4])
        days = int(nmeastr[4:6])

        return Udate(years, months, days)

    def nmeaStringFromUdate(self) -> str:
        """Create NMEA time string from Utime object

        :return: time string as used in NMEA Sentence (hhmmss.ss)
        :rtype: str
        """

        year_str = str(self._year)
        years = year_str[2:4]
        months = "%02d" % (self._month,)
        days = "%02d" % (self._day,)

        return years + months + days


"""
Helper Methods and Exceptions
"""


class UtimeParseError(Exception):
    """
    Invalid Parameter in uTime Constructor
    """

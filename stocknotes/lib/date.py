
import re
import string
import time
from functools import total_ordering

number2month = {
    1:"January", 2:"February", 3:"March", 4:"April",
    5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October",
    11:"November", 12:"December" }

month2number = {}
for number in number2month.keys():
    smonth = number2month[number].lower()
    month2number[smonth] = number
    # add abbreviations such as "Jan" to the lookup
    month2number[smonth[0:3]] = number

daysPerMonth=[
    31, #jan
    28, #feb
    31, #mar
    30, #apr
    31, #may
    30, #jun
    31, #jul
    31, #aug
    30, #sep
    31, #oct
    31, #nov
    31] #dec

cumulativeDaysPerMonth=[]
c=0
for i in range(0,12):
    cumulativeDaysPerMonth.append(c)
    c += daysPerMonth[i]

class Date:

    """ simple Date class used by stocks. """
    
    year=1900
    month=1
    day=1

    def __init__(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day

    def __lt__(self,other):
        if self.year < other.year:
            return True
        elif self.year == other.year:
            if self.month < other.month:
                return True
            elif self.month == other.month:
                return self.day < other.day
        return False

    def __ge__(self,other):
        if self.year < other.year:
            return False
        elif self.year > other.year:
            return True
        else: # years are equal
            if self.month < other.month:
                return False
            elif self.month > other.month:
                return True
            else: # years and months are equal
                if self.day < other.day:
                    return False
                elif self.day >= other.day:
                    return True

        raise Exception("we should never get here")

    def __eq__(self,other):
        return self.year==other.year and self.month==other.month and self.day==other.day

    def wordy(self):
        return "%s %d, %d" % (number2month[self.month], self.day, self.year)
    def abbreviated(self):
        return "%s %2d, %d" % (number2month[self.month][:3], self.day, self.year)
    def __str__(self):
        return self.wordy()

    def __hash__(self):
        # is caching this important?
        return self.year*10000 + self.month*100 + self.day

    def decimalYear(self):
        return self.year+(cumulativeDaysPerMonth[self.month-1]+self.day)/365.0

__m=time.localtime(time.time())
today=Date(__m[0],__m[1],__m[2])
    
dateRe = re.compile(r"^\s*(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\s*$")

def parseDate(line):

    """Parses the given line of text and returns a Date object or None"""
    
    result = dateRe.search(line)
    if not result:
        return None
    smonth = result.group("month").lower()
    if not smonth in month2number:
        return None
    return Date(int(result.group("year")),
            month2number[smonth],
            int(result.group("day")),)


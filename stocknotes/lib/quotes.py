
from lib.date import Date
from lib.configuration import NOTIFY_QUOTES_FILE
import re
import string

class Quote:
    pass

dateRe = re.compile(r"^(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)$")

class Quotes:

    def __init__(self,downloadFile=NOTIFY_QUOTES_FILE):

        # we don't use the csv module since glottis uses an old version of
        # python that does not have the module

        self.quotes = {}  # ticker ==> Quote

        f=open(downloadFile)
        while 1:
            line=f.readline()
            if line=="":
                break
            row = line.split(",")
            ticker = _noQuotes(row[0])
            q=Quote()
            q.price=float(_noQuotes(row[1]))
            q.date=_parseCsvDate(_noQuotes(row[2]))
            self.quotes[ticker]=q
        f.close()

    def __getitem__(self,key):
        return self.quotes[key]

    def has_key(self,key):
        return key in self.quotes

def _parseCsvDate(s):
    if s=="N/A":
        return Date(1900,1,1)
    result = dateRe.search(s)
    if not result:
        raise ValueError("bad csv date format: "+s)
    return Date(
        int(result.group("year")),
        int(result.group("month")),
        int(result.group("day")))

def _noQuotes(s):
    i=0
    j=len(s)
    if i<j and s[0]=='"':
        i=i+1
    if j>i and s[j-1]=='"':
        j=j-1
    return s[i:j]



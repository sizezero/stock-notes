
import re

from fraction import Fraction

class Shares:
    """ combines the numerical share value with the split multiple. """
    def __init__(self,shares,mult):
        """ mult should be a Fraction object """
        self.shares=int(shares)
        self.mult=mult
    def atMult(self,mult):
        return int(self.shares*(mult/self.mult).toFloat())
    def __add__(self,other):
        if self.mult==other.mult:
            return Shares(self.shares+other.shares, self.mult)
        else:
            # this causes multiples to grow quickly
            # has potential for round off errors
            # not sure if other methods are any better
            return Shares(
                self.shares*other.mult.toFloat() + \
                other.shares*self.mult.toFloat(),
                self.mult*other.mult)
    def __sub__(self,other):
        if self.mult==other.mult:
            return Shares(self.shares-other.shares, self.mult)
        else:
            return Shares(
                self.shares*other.mult.toFloat() - \
                other.shares*self.mult.toFloat(),
                self.mult*other.mult)
    def __div__(self,other):
        return (self.shares*other.mult.toFloat()) / (other.shares*self.mult.toFloat())
    def __iadd__(self,other):
        return self + other
    def __isub__(self,other):
        return self - other
    def __cmp__(self,other):
        if self.shares==0 and other.shares==0:
            return 0
        if self.shares==other.shares and self.mult==other.mult:
            return 0
        return cmp(round(self.shares/self.mult.toFloat()),
                   round(other.shares/other.mult.toFloat()))

zero = Shares(0,Fraction(1,1))

stockRe = re.compile(r"^(?P<shares>\d+)$")

def parseShares(s,mult):
    result = stockRe.search(s)
    if result:
        try:
            return Shares(int(result.group("shares")),mult)
        except Exception:
            pass
    raise ValueError("share value must be a whole integer")


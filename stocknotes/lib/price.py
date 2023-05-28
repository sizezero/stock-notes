
import re

from lib.fraction import Fraction

class Price:
    """ combines the numerical share value with the split multiple. """
    def __init__(self,price,mult):
        """ mult should be a Fraction object """
        self.price=price
        self.mult=mult
    def atMult(self,mult):
        return self.price*(self.mult/mult).toFloat()
    def __cmp__(self,other):
        if self.price==0 and other.price==0:
            return 0
        if self.price==other.price and self.mult==other.mult:
            return 0
        return cmp(self.price*self.mult.toFloat(),
                   other.price*other.mult.toFloat())

priceRe = re.compile(r"^\$?(?P<price>\d+(\.\d+)?)$")

def parsePrice(s,mult):
    result = priceRe.search(s)
    if result:
        try:
            return Price(float(result.group("price")),mult)
        except Exception:
            pass
    raise ValueError("invalid price")

def dollar2str(f):
    if f>=0.0:
        return "$%.2f " % f
    else:
        return "($%.2f)" % -f


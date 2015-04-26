
import os
import re
import string

def string2Amount(s):
    if s is None or s.lower() == "none":
        return None
    else:
        return s

class Buy:
    def __init__(self,price1,price2):
        if price1 is None or price1 == "none":
            self.price1 = None
            self.price2 = None
        elif price2 is None or price2 == "none":
            self.price1 = float(price1)
            self.price2 = None
        else:
            if price1<price2:
                self.price1 = float(price1)
                self.price2 = float(price2)
            else:
                self.price1 = float(price2)
                self.price2 = float(price1)

class Sell:
    def __init__(self,price1,price2):
        if price1 is None or price1 == "none":
            self.price1 = None
            self.price2 = None
        elif price2 is None or price2.lower() == "none":
            self.price1 = float(price1)
            self.price2 = None
        else:
            if price1>price2:
                self.price1 = float(price1)
                self.price2 = float(price2)
            else:
                self.price1 = float(price2)
                self.price2 = float(price1)

_buy_re = re.compile(r"^BUY\s+(\S+)(\s+(\S+))?\s*$")
_sell_re = re.compile(r"^SELL\s+(\S+)(\s+(\S+))?\s*$")

def _parseArg(arg):
    if arg is None:
        return None
    elif arg.lower() == "none":
        return "none"
    elif len(arg) > 0 and arg[0]=='$':
        return arg[1:]
    else:
        return arg

def parseBuy(old, line):
    result = _buy_re.search(line)
    if result:
        n = Buy(_parseArg(result.group(1)), _parseArg(result.group(3)))
        if n.price1 is not None:
            return n
        else:
            return None
    return old

def parseSell(old, line):
    result = _sell_re.search(line)
    if result:
        n = Sell(_parseArg(result.group(1)), _parseArg(result.group(3)))
        if n.price1 is not None:
            return n
        else:
            return None
    return old


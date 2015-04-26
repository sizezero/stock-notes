
import re

from date import Date
import fraction
import price as pricem
import shares as sharesm

class Trade:
    date=Date(1900,1,1)
    
    def shareAdjust(self,shares):
        return shares

    def returnAdjust(self,mult):
        return 0

    def multAdjust(self,mult):
        return mult

    def getUnsold(self):
        return sharesm.zero

    def setUnsold(self,shares):
        pass

    def isBuy(self):
        return 0

    def isSell(self):
        return 0

class Buy(Trade):
    
    def __init__(self,date,shares,price,commission):
        self.date=date
        self.shares = shares
        self.price = price
        self.commission = commission

    def shareAdjust(self,shares):
        return shares + self.shares

    def returnAdjust(self,mult):
        return -(self.shares.atMult(mult)*self.price.atMult(mult)) - self.commission

    def getUnsold(self):
        return self.unsoldShares

    def setUnsold(self,shares):
        self.unsoldShares=shares

    def isBuy(self):
        return 1

class Sell(Trade):
    def __init__(self,date,shares,price,commission):
        self.date=date
        self.shares = shares
        self.price = price
        self.commission = commission

    def shareAdjust(self,shares):
        return shares - self.shares

    def returnAdjust(self):
        return self.shares.atMult(mult)*self.price.atMult(mult) - commission

    def isSell(self):
        return 1

class Split(Trade):
    def __init__(self,date,mult):
        self.date=date
        self.mult=mult
        
    def multAdjust(self,mult):
        return self.mult * mult

class Dividend(Trade):
    def __init__(self,date,payment):
        self.date=date
        self.payment=payment
    def returnAdjust(self,mult):
        return payment

################################################

def parseTrade(args,date,mult,trades):
    """
    TRADE buy nnn@nnn.nnn balance nnn commission nnn.nnn
    TRADE sell nnn@nnn.nnn balance nnn commission nnn.nnn
    TRADE split nnn:nnn balance nnn
    TRADE dividend nnn.nnn

    questions:
    cap gain on sale
    total gain on sale; cumulative return; cumulative dividend return
    gains by year (all, per ticker)
    
    It looks like we want to see gains by (ticker|all) (year range)
    It would also be nice to see pseudo sale gain buy current
    ticker price.  This would require prices and commissions.
    """
    a=args.lower().split()
    t=a.pop(0)
    if t=="buy":
        (shares,price,balance,commission)=parseBuySell(a,mult)
        return (Buy(date,shares,price,commission),balance)
    elif t=="sell":
        (shares,price,balance,commission)=parseBuySell(a,mult)
        return (Sell(date,shares,price,commission),balance)
    elif t=="split":
        argCount(a,3)
        multAdj=parseMult(a[0])
        argCheck(a[1],"balance")
        split=Split(date,multAdj)
        balance = sharesm.parseShares(a[2],split.multAdjust(mult))
        return (split,balance)
    elif t=="dividend":
        argCount(a,1)
        price=parseCash(a[0])
        return (Dividend(date,price),-1)
    else:
        raise ValueError("unrecognized trade: "+t)

def argCount(a,n):
    if len(a)!=n:
        raise ValueError("expected %d arguments" % n)

def argCheck(e,v):
    if e!=v:
        raise ValueError("expected "+v)

cashRe = re.compile(r"^\$?(?P<cash>\d+(\.\d+)?)$")

def parseCash(s):
    result = cashRe.search(s)
    if result:
        try:
            return float(result.group("cash"))
        except Exception:
            pass
    raise ValueError("invalid dollar amount")

sharesAtPriceRe = re.compile(r"^(?P<shares>[^@]+)@(?P<price>[^@]+)$")

def parseSharesAtPrice(s,mult):
    result = sharesAtPriceRe.search(s)
    if result:
        return (sharesm.parseShares(result.group("shares"),mult),
                pricem.parsePrice(result.group("price"),mult))
    raise ValueError("expected @")

def parseBuySell(a,mult):
    """
    returns (stock,price,balance,commission)
    default balance==None
    default commision==0.0
    """
    if len(a)<1:
        raise ValueError("price must be specified")
    (shares,price) = parseSharesAtPrice(a.pop(0),mult)
    balance=None
    commission=0.0
    while 1:
        if len(a)==0:
            return (shares,price,balance,commission)
        if len(a)==1:
            raise ValueError("unknown argument: "+a[0])
        name=a.pop(0)
        value=a.pop(0)
        if name=="balance":
            balance=sharesm.parseShares(value,mult)
        elif name=="commission":
            commission=parseCash(value)
        else:
            raise ValueError("expected 'balance' or 'commission'")

multRe = re.compile(r"^(?P<numerator>\d+):(?P<denominator>\d+)$")

def parseMult(s):
    result = multRe.search(s)
    if result:
        return fraction.Fraction(int(result.group("numerator")),
                                 int(result.group("denominator")))
    raise ValueError("expected mult ratio n:n")


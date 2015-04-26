#!/usr/bin/python

import re
import os
import os.path
import string
import sys

from date import Date,parseDate,today
import fraction
import notify
import shares
from trade import parseTrade
import buysell
from configuration import LOG_DIR

################################################

class Entry:
    ticker=""
    date=Date(1900,1,1)
    text=""

    def __init__(self,ticker,date,text):
        self.ticker = ticker
        self.date = date
        self.text = text

    def __cmp__(self,other):
        if self.ticker!=other.ticker:
            return cmp(self.ticker,other.ticker)
        return cmp(self.date,other.date)

################################################

class Company:
    ticker=""
    name="<nameless>"
    cid="<none>"
    entries=[]
    trades=[]
    keywords=[]

    def __init__(self,ticker):
        self.ticker = ticker
        self.entries=[]
        self.trades=[]
        self.notifies = notify.makeArray()
        self.keywords=[]
        self.buy = None
        self.sell = None

    def __cmp__(self,other):
        return cmp(self.ticker,other.ticker)

################################################

entries = []
companies = {} # ticker ==> companies

################################################

nameRe = re.compile(r"^NAME:(?P<name>.*)$")

cidRe = re.compile(r"^CID:(?P<cid>.*)$")

tradeRe = re.compile(r"^TRADE\s(?P<args>.*)$")

keywordsRe = re.compile(r"^KEYWORDS:\s(?P<args>.*)$")

# lowercase alphanumeric plus underscore
keywordRe = re.compile(r"^[a-z][a-z0-9_]*$")

def init():
    fileRe = re.compile(r"^(?P<ticker>[A-Za-z\.\-]+)\.txt$")
    files = os.listdir(LOG_DIR)
    files.sort()
    fail = 0
    for f in files:
        result = fileRe.search(f)
        if result:
            if not processFile(
                os.path.join(LOG_DIR,f),
                string.upper(result.group("ticker"))):
                fail = 1
        else:
            if not f.endswith(".txt") and not f.endswith("~"):
                print "invalid file: "+f
                fail = 1
    if fail:
        # bug: for some reason the importing code is still run
        sys.exit(1)

def processFile(fileName, ticker):
    global entries
    global companies
    company = Company(ticker)
    companies[ticker] = company
    date = None
    currentText = ""
    mult=fraction.one
    balance=shares.zero
    input = open(fileName,'r')
    lineNo = 0
    succeed = 1
    while 1:
        line = input.readline()
        lineNo = lineNo + 1
        if line=="":
            if date:
                e = Entry(ticker,date,currentText)
                company.entries.append(e)
                entries.append(e)
            break
        nextDate = parseDate(line)
        if nextDate:
            if date:
                if nextDate < date:
                    print "warning %s(%d) date entry out of order" \
                          % (fileName,lineNo)
                    succeed = None
                e = Entry(ticker,date,currentText)
                company.entries.append(e)
                entries.append(e)
            date = nextDate
            currentText = ""
            continue
        result = nameRe.search(line)
        if result:
            company.name=string.strip(result.group("name"))
            continue
        result = cidRe.search(line)
        if result:
            company.cid=string.strip(result.group("cid"))
            continue
        try:
            result = tradeRe.search(line)
            if result:
                (trade,parseBalance)=parseTrade(
                    result.group("args"),date,mult,company.trades)
                mult=trade.multAdjust(mult)
                balance=trade.shareAdjust(balance)
                if balance is None:
                    balance=shares.zero
                    raise ValueError("negative share balance")
                if parseBalance is not None and parseBalance!=balance:
                    raise ValueError("incorrect balance: %d != %d"
                                    % (balance.atMult(mult),
                                       parseBalance.atMult(mult)))
                company.trades.append(trade)
            if notify.notifyRe.search(line):
                notify.parseNotify(line,mult,company.notifies)
            company.buy = buysell.parseBuy(company.buy, line)
            company.sell = buysell.parseSell(company.sell, line)
            result = keywordsRe.search(line)
            if result:
                company.keywords = string.split(result.group("args"))
                for k in company.keywords:
                    result = keywordRe.search(k)
                    if not result:
                        raise ValueError("keywords must be lowercase alphanumeric")
        except ValueError, ex:
            print "warning %s(%d) %s" \
                  % (fileName,lineNo,str(ex))
            succeed = None
        currentText = currentText + line
    input.close()
    if balance.shares != 0:
        company.keywords.append("owned")
    return succeed

init()

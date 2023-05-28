#!/usr/bin/python3

import re
import os
import os.path
import string
import sys
from functools import total_ordering

from lib.date import Date,parseDate,today
import lib.fraction
import lib.notify
import lib.shares
from lib.trade import parseTrade
import lib.buysell
from lib.configuration import LOG_DIR

################################################

class Entry:
    ticker=""
    date=Date(1900,1,1)
    text=""

    def __init__(self,ticker,date,text):
        self.ticker = ticker
        self.date = date
        self.text = text

    def __lt__(self,other):
        if self.ticker!=other.ticker:
            return self.ticker < other.ticker
        return self.date < other.date

    def __eq__(self,other):
        return self.ticker==other.ticker and self.date==other.date

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
        self.notifies = lib.notify.makeArray()
        self.keywords=[]
        self.buy = None
        self.sell = None

    def __lt__(self,other):
        return self.ticker < other.ticker

    def __eq__(self,other):
        return self.ticker == other.ticker

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
                result.group("ticker").upper()):
                fail = 1
        else:
            if not f.endswith(".txt") and not f.endswith("~"):
                print("invalid file: "+f)
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
    mult=lib.fraction.one
    balance=lib.shares.zero
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
                    print("warning %s(%d) date entry out of order" \
                          % (fileName,lineNo))
                    succeed = None
                e = Entry(ticker,date,currentText)
                company.entries.append(e)
                entries.append(e)
            date = nextDate
            currentText = ""
            continue
        result = nameRe.search(line)
        if result:
            company.name=result.group("name").strip()
            continue
        result = cidRe.search(line)
        if result:
            company.cid=result.group("cid").strip()
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
            if lib.notify.notifyRe.search(line):
                lib.notify.parseNotify(line,mult,company.notifies)
            company.buy = lib.buysell.parseBuy(company.buy, line)
            company.sell = lib.buysell.parseSell(company.sell, line)
            result = keywordsRe.search(line)
            if result:
                company.keywords = result.group("args").split()
                for k in company.keywords:
                    result = keywordRe.search(k)
                    if not result:
                        raise ValueError("keywords must be lowercase alphanumeric")
        except ValueError as ex:
            print("warning %s(%d) %s" \
                  % (fileName,lineNo,str(ex)))
            succeed = None
        currentText = currentText + line
    input.close()
    if balance.shares != 0:
        company.keywords.append("owned")
    else:
        if len(company.trades)>0:
            company.keywords.append("sold")
    if company.buy is not None or company.sell is not None:
        company.keywords.append("watching")
    return succeed

init()

#!/usr/bin/python3

import re
import os
import os.path
import string
import sys
from functools import total_ordering

from lib.date import Date,parseDate,today
from lib.configuration import CASH_DIR

################################################

class Account:
    name=""
    date=None
    balance=None # integer value
    
    def __init__(self,name):
        self.name = name
        self.date = None
        self.balance = None

    def __lt__(self,other):
        return self.name < other.name

    def __eq__(self,other):
        return self.name == other.name

    def balanceString(self):
        s = ""
        i=0
        b = str(self.balance)
        while (len(b)<3):
            b = "0"+b
        for c in reversed(str(b)):
            s += c
            i += 1
            if (i == 2):
                s += "."
            if (i>2 and i<len(b) and (i-2) % 3 == 0):
                s += ","
        s += "$"
        return "".join(reversed(s))

    def balanceFloat(self):
        return float(self.balance)/100.0
    
################################################

entries = []
accounts = {} # name ==> accounts

################################################

balanceRe = re.compile(r"^BALANCE:\s*\$(?P<balance>[\d,]+\.\d{2})$")

def init():
    fileRe = re.compile(r"^(?P<account>[A-Za-z\.\-]+)\.txt$")
    files = os.listdir(CASH_DIR)
    files.sort()
    fail = 0
    for f in files:
        result = fileRe.search(f)
        if result:
            if not processFile(
                os.path.join(CASH_DIR,f),
                result.group("account").upper()):
                fail = 1
        else:
            if not f.endswith(".txt") and not f.endswith("~"):
                print("invalid file: "+f)
                fail = 1
    if fail:
        # bug: for some reason the importing code is still run
        sys.exit(1)

def processFile(fileName, accountName):
    global entries
    global accounts
    account = Account(accountName)
    accounts[accountName] = account
    input = open(fileName,'r')
    lineNo = 0
    succeed = 1
    while 1:
        line = input.readline()
        lineNo = lineNo + 1
        if line=="":
            break
        nextDate = parseDate(line)
        if nextDate:
            if account.date:
                print("warning %s(%d) date already entered" \
                          % (fileName,lineNo))
                succeed = None
            account.date = nextDate
            continue
        result = balanceRe.search(line)
        if result:
            if account.balance:
                print("warning %s(%d) balance already entered" \
                          % (fileName,lineNo))
                succeed = None
            account.balance=int(re.sub('[.,]','',result.group("balance")))
            continue
    input.close()
    if account.balance is None:
        print("warning %s balance not entered" \
            % (fileName))
        succeed = None
    return succeed
        
init()

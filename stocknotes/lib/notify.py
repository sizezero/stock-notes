
import os
import re
import string

import lib.date
import lib.price

class Notify:

    def isTriggered(self, currentPrice, currentDate):
        return 0

    def lineItem(self,company,mult):
        return ""

    def email(self,company,mult,to):
        pass

    def needsPrice(self):
        return 0

lineItemFormat = "%6s %12s %s"

factoryIndex=0

class NotifyFactory:

    def __init__(self):
        global factoryIndex
        self.index = factoryIndex
        factoryIndex = factoryIndex + 1

    def parse(self,line,mult,notifies):
        """
        Returns true if the line was parsed and notifies was updated.
        """
        return 0

class NotifyNull(Notify):
    pass

notifyNull = NotifyNull()

class NotifyPrice(Notify):
    
    def __init__(self,comp,price,comment):
        self.comp=comp
        self.price=price
        self.comment=comment

    def isTriggered(self, currentPrice, currentDate):
        if self.comp=="<":
            return currentPrice < self.price
        else:
            return currentPrice > self.price

    def lineItem(self,company,mult):
        return lineItemFormat % (company.ticker,self.comp+price.dollar2str(self.price.atMult(mult)),self.comment)

    def email(self,company,mult,to):
        s= "%6s %s%s" % (company.ticker,self.comp,price.dollar2str(self.price.atMult(mult)))
        sendEmail(to,s,self.comment)

    def needsPrice(self):
        return 1

class NotifyPriceFactory(NotifyFactory):

    def __init__(self,comp):
        NotifyFactory.__init__(self)
        self.regex = re.compile(r"^NOTIFY\s+price\s+(?P<compare>"+comp+")\s+(?P<price>[$\d\.]+)\s+(?P<comment>.+)$")
        self.nullRegex = re.compile(r"^NOTIFY\s+price\s+off\s*$")

    def parse(self,line,mult,notifies):
        result = self.regex.search(line)
        if result:
            notifies[self.index] = NotifyPrice(
                result.group("compare"),
                lib.price.parsePrice(result.group("price"),mult),
                result.group("comment"))
            return 1
        if self.nullRegex.search(line):
            notifies[self.index] = notifyNull
            return 1
        return 0

class NotifyDate(Notify):

    def __init__(self,date,comment):
        self.date=date
        self.comment=comment

    def isTriggered(self, currentPrice, currentDate):
        return currentDate >= self.date
        
    def lineItem(self,company,mult):
        return lineItemFormat % (company.ticker,self.date.abbreviated(),self.comment)

    def email(self,company,mult,to):
        s = "%6s %s" % (company.ticker,str(self.date))
        sendEmail(to,s,self.comment)

    def getIndex(self):
        return 2

class NotifyDateFactory(NotifyFactory):

    def __init__(self):
        NotifyFactory.__init__(self)
        self.regex = re.compile(r"^NOTIFY\s+date\s+(?P<date>[A-Za-z]+\s+\d{1,2},\s*\d{4})\s+(?P<comment>.+)\s*$")
        self.nullRegex = re.compile(r"^NOTIFY\s+date\s+off\s*$")

    def parse(self,line,mult,notifies):
        result = self.regex.search(line)
        if result:
            notifies[self.index] = NotifyDate(
                lib.date.parseDate(result.group("date")),
                result.group("comment"))
            return 1
        if self.nullRegex.search(line):
            notifies[self.index] = notifyNull
            return 1
        return 0

def sendEmail(to,subject,body):
    if not re.compile("^\w+@[\w\.]+$").search(to):
        raise ValueError("bad email address")
    # remove singled quotes and backslashes which can cause problems
    # on the command line
    subject=string.replace(subject,"'","")
    subject=string.replace(subject,"\\","")
    body=string.replace(body,"'","")
    body=string.replace(body,"\\","")
    cmd = "echo '%s' | mail -s '%s' %s" % (body,subject,to)
    input = os.popen(cmd)
    out = input.read()
    ret = input.close()
    
################################################

notifyRe = re.compile(r"^NOTIFY\s")

factories = [
    NotifyDateFactory(),
    NotifyPriceFactory("<"),
    NotifyPriceFactory(">")
    ]

notifiesTemplate = [notifyNull] * len(factories)

def makeArray():
    return list(notifiesTemplate)

def parseNotify(line,mult,notifies):
    for f in factories:
        if f.parse(line,mult,notifies):
            return
    raise ValueError("bad NOTIFY statement")

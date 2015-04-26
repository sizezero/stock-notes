#!/usr/bin/python

import cgi
import re
import os
import string
import sys

reTicker = re.compile(r"^[a-z\.]+$")

def main():
    #print "Content-type: text/plain\n"
    print "Content-type: text/html\n"
    form = cgi.FieldStorage()
    if not form.has_key("ticker"):
        print "need ticker argument"
        return
    ticker = str(form["ticker"].value)
    if not reTicker.search(ticker):
        print "invalid ticker: "+ticker
        return
    disp2(ticker)

def disp1(ticker):
    cmd = "cat ../log/"+ticker+".txt"
    input=os.popen(cmd)
    print input.read()
    input.close()
    
def disp2(ticker):
    fileName="../log/"+ticker+".txt"
    input = open(fileName,'r')
    lineNo = 0
    print "Ticker: "+string.upper(ticker)+"<br><br>"
    while 1:
        line = input.readline()
        lineNo = lineNo + 1
        if line=="":
            break
        print cgi.escape(line)+"<br>"
    input.close()

main()

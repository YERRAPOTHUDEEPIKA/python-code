#Overlap period of Financial years 1st April to 15th April - Change 9th January 2022
'''
In RentalInvoiceTable Invoice Date is stored in both hyphenated eg: 2022-12-13 16:36:29.223000 form
as well in dotted form (as used by user) eg: 01.12.2022 though not standard, abide by for the user.
To differentiate them use the following logic
dbinvdate = str(inv.get("Invoice Date"))
	if "-" in dbinvdate:
		print("hyphen",inv.get("Invoice Date"), inv.get("InvoiceTenantGSTKey"), inv.get("Invoice No"))
		print(dbinvdate[0:4]) #for the year
	if "." in dbinvdate[0:10]:
		print("dotted",inv.get("Invoice Date"), inv.get("InvoiceTenantGSTKey"), inv.get("Invoice No"))
		print(dbinvdate[6:10]) #for the year

'''
from flask import Flask, request, url_for, redirect, session, render_template, json, send_file
from flask_session import Session
import pymongo
import cryptocode
import datetime
import pandas as pd
from datetime import date
import time
from datetime import datetime, timedelta
import random
import inflect
from fpdf import FPDF
import os
import fnmatch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from num2words import num2words
import decimal 
import webbrowser
import shutil
import math
import csv 
#import fuzzy
#soundex = fuzzy.Soundex(4)
import zipfile
#05012023
#from pynput.keyboard import Key, Controller
from apscheduler.schedulers.background import BackgroundScheduler


RentInvoice = Flask(__name__)
RentInvoice.config["SESSION_PERMANENT"] = False
RentInvoice.config["SESSION_TYPE"] = "filesystem"
import hashlib
secret_string = str(datetime.now())
result = hashlib.sha256(secret_string.encode())

result_hex = result.hexdigest()
secret_key = result_hex.encode('ASCII')
#print(secret_key)
RentInvoice.config['SECRET_KEY'] = secret_key
#RentInvoice.config['SECRET_KEY'] = b'1db9a6ffaf6a8566338d6d2f8db1f812a7c23a4e25299ab6ab228a81e9cfdaf0'
Session(RentInvoice)
Session(RentInvoice)

global staticpath
global mycwd, mydrive


global mycwd, mydrive
global okdate, inv34, bank1, bank2, bank3, bank4, bank5, bank6, bank7, owner, newinvno
global inproperty, newinvno, tenantgst, newinvdate, proper_newinvdate, proper_changeinvdate
global owner, tenantphone, bank1, bank2, bank3, bank4, bank5, bank6
global rbt, sgst, cgst, totalrent, totalgst, tenantemail
global inrbt, insgst, incgst, intotalrent, intotalgst
global reprint, proper_changeinvdate
global calmalllastinvoice
global calmallsno
global wsdgshare, netamt
global tdsneeded, tdspercent, tdsamt
global fpusername
global igstflag, ingst, igststate
global yyyychoice
reprint = False
cancelflag = False
editinvflag = False
tdsneeded = False
tdspercent = "0"
tdsamt = "0"

mycwd= os.getcwd()
mydrive = mycwd[0:2]


def print_date_time():
	#Solving the intermittent hanging problem?
	print("Hello, this is a scheduled message")
	print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"),'\n','\r')
	print("scheduled message ends")


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="interval", seconds=3600)
scheduler.start()
	

def myround(amt_to_round):
	decpart = amt_to_round % 1
	if decpart == 0.5:
		rounded = 1 + round(amt_to_round)
	else:
		rounded = round(amt_to_round)
	return rounded

def findfile(pattern, path):
	result = []
	for root, dirs, files in os.walk(path):
	    for name in files:
	        if fnmatch.fnmatch(name, pattern):
	            result.append(os.path.join(root, name))
	return result

def currency_in_indian_format(n):
	""" Convert a number (int / float) into indian formatting style """
	d = decimal.Decimal(str(n))

	if d.as_tuple().exponent < -2:
		s = str(n)
	else:
		s = '{0:.2f}'.format(n)

	l = len(s)
	i = l - 1

	res, flag, k = '', 0, 0
	while i >= 0:
		if flag == 0:
			res += s[i]
			if s[i] == '.':
				flag = 1
		elif flag == 1:
			k += 1
			res += s[i]
			if k == 3 and i - 1 >= 0:
				res += ','
				flag = 2
				k = 0
		else:
			k += 1
			res += s[i]
			if k == 2 and i - 1 >= 0:
				res += ','
				flag = 2
				k = 0
		i -= 1

	return res[::-1]
#currency in indian format ends here

def word(number):
	x = str(number)
	if x == "" or x == "0":
		word = "Zero"
	else:
		rupees, paise = x.split('.')
		rupees_word = num2words(rupees, lang ='en_IN') + ' '
		if int(paise) > 0:
			paise_word = ' and ' + num2words(paise, lang ='en_IN') + ' Paise'
			word =  rupees_word + paise_word
		else:
			word = rupees_word
		word = word.replace(',','').title()                                      
	return word
#number to word ends here

#State Dictionaries
stategst_lookup = {
	'ANDAMAN AND NICOBAR ISLANDS' : '35',
	'ANDHRA PRADESH' : '37',
	'ARUNACHAL PRADESH' : '12',
	'ASSAM' : '18',
	'BIHAR' : '10',
	'CHANDIGARH' : '4',
	'CHHATTISGARH' : '22',
	'DADRA AND NAGAR HAVELI' : '26',
	'DAMAN AND DIU' : '26',
	'DELHI' : '7',
	'GOA' : '30',
	'GUJARAT' : '24',
	'HARYANA' : '6',
	'HIMACHAL PRADESH' : '2',
	'JAMMU AND KASHMIR' : '1',
	'JHARKHAND' : '20',
	'KARNATAKA' : '29',
	'KERALA' : '32',
	'LAKSHADWEEP' : '31',
	'MADHYA PRADESH' : '23',
	'MADHYAPRADESH' : '23',
	'MAHARASHTRA' : '27',
	'MANIPUR' : '14',
	'MEGHALAYA' : '17',
	'MIZORAM' : '15',
	'NAGALAND' : '13',
	'ORISSA' : '21',
	'PONDICHERRY' : '97',
	'PUNJAB' : '3',
	'RAJASTHAN' : '8',
	'SIKKIM' : '11',
	'TAMIL NADU' : '33',
	'TAMILNADU' : '33',
	'TRIPURA' : '16',
	'TRIPURA' : '16',
	'UTTAR PRADESH' : '9',
	'UTTARPRADESH' : '9',
	'UTTARAKHAND' : '5',
	'WESTBENGAL' : '19',
	'WEST BENGAL' : '19'
}

statecode_lookup = {
'ANDAMAN AND NICOBAR ISLANDS' : 'AN',
'ANDHRA PRADESH' : 'AP',
'ARUNACHAL PRADESH' : 'AR',
'ASSAM' : 'AS',
'BIHAR' : 'BR',
'CHANDIGARH' : 'CH',
'CHHATTISGARH' : 'CG',
'DADRA AND NAGAR HAVELI' : 'DH',
'DAMAN AND DIU' : 'DD',
'DELHI' : 'DL',
'GOA' : 'GA',
'GUJARAT' : 'GJ',
'HARYANA' : 'HR',
'HIMACHAL PRADESH' : 'HP',
'JAMMU AND KASHMIR' : 'JK',
'JHARKHAND' : 'JH',
'KARNATAKA' : 'KA',
'KERALA' : 'KL',
'LAKSHADWEEP' : 'LD',
'MADHYA PRADESH' : 'MP',
'MAHARASHTRA' : 'MH',
'MANIPUR' : 'MN',
'MEGHALAYA' : 'ML',
'MIZORAM' : 'MZ',
'NAGALAND' : 'NL',
'ORISSA' : 'OR',
'PONDICHERRY' : 'PY',
'PUNJAB' : 'PB',
'RAJASTHAN' : 'RJ',
'SIKKIM' : 'SK',
'TAMIL NADU' : 'TN',
'TAMIL NADU' : 'TN',
'TRIPURA' : 'TR',
'TRIPURA' : 'TR',
'UTTAR PRADESH' : 'UP',
'UTTARAKHAND' : 'UK',
'WESTBENGAL' : 'WB',
'WEST BENGAL' : 'WB',

}

def dbopen():
	global Invoice_dbclient, Invoice_db, Invoice_dbCollection, Invoice_Receipt, Rent_Ledger
	global Invoice_Users_Collection, Owners, calmalllastinvoice, opbalance, environ
	global staticpath, thisenv
	Invoice_dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
	Invoice_db = Invoice_dbclient["RentalInvoiceDbClient"]
	Invoice_Users_Collection = Invoice_db["InvoiceUsersTable"]
	Invoice_dbCollection = Invoice_db["RentalInvoiceTable"]
	Invoice_Receipt = Invoice_db["InvoiceReceipt"]
	Rent_Ledger = Invoice_db["RentLedger"]
	Owners = Invoice_db["Owners"]
	#calmalllastinvoice = Invoice_db["CalMallLastInvoice"]
	opbalance = Invoice_db["OpeningBalance"]
	environ = Invoice_db["Environment"]
	# Difference in Dev and Prod environment is the static path
	envlist = environ.find({})
	envlist  = list(envlist)
	for envrec in envlist:
		if envrec.get("Environment") == "Production":
			staticpath = "/RentInvoice/Scripts/static/"
			thisenv = "Production"
		elif envrec.get("Environment") == "Development":
			staticpath = "/RentInvoice/Scripts/static/"
			thisenv = "Development"
		else:
			staticpath = "/RentInvoice/Scripts/static/"
			thisenv = "Production"

def pdfcreate():
				global proper_newinvdate, inproperty, editinvflag
				global proper_changeinvdate, changeremarks, changetenantemail
				global inproperty
				global state
				global rbt
				global sgst
				global cgst
				global totalrent
				global totalgst
				global pathpdfname
				global inrbt, insgst, incgst, intotalrent, intotalgst
				global reprint
				global cancelflag
				global staticpath, mydrive
				global wsdgshare, netamt
				global tdsneeded, tdspercent, tdsamt
				global igstflag, inigst, igststate
				# Add a page
				pdf = FPDF('P', 'mm', 'A4')
				pdf.set_margins(left= 20, top= 20, right = -1)
				pdf.add_page()
				#inv number
				pdf.set_font("Arial", "", 9)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				topx = xpos
				topy = ypos
				pdf.multi_cell(w=50, h = 8, txt ="Invoice No:", align = 'L')
				pdf.set_font("Arial", "B", 9)
				pdf.set_xy(xpos+20,ypos)
				#For Emarald mall show the full invoice number else only first 14 chars
				if session['owner'] == "BENCY & COMPANY":
					pdfinv = session['newinvno']
				else:
					pdfinv = session['newinvno'][:14]
				pdf.multi_cell(w=30, h = 8, txt =pdfinv)
				#invoice date
				pdf.set_xy(xpos+140,ypos)
				pdf.set_font("Arial", "", 9)
				pdf.multi_cell(w=50, h = 8, txt ="Dated:", align = 'L')
				pdf.set_xy(xpos+120,ypos)
				pdf.set_font("Arial", "B", 9)
				if reprint or editinvflag:
					pdf.multi_cell(w=50, h = 8, txt = proper_changeinvdate, align = 'R')
				else:
					pdf.multi_cell(w=50, h = 8, txt = session['proper_newinvdate'], align = 'R')
				pdf.set_font("Arial", "", 5)
				propdesc = "Property No."+inproperty
				pdf.set_xy(topx, topy+8)
				pdf.multi_cell(w=30, h = 6, txt = propdesc, align = 'L')
				pdf.set_xy(topx, topy+10)
				pdf.set_font("Arial", "B", 10)
				pdf.multi_cell(w=160, h = 5, txt =session['owner'], align = 'C')
				pdf.set_font("Arial", "", 8)
				pdf.multi_cell(w=160, h = 5, txt =session['ownergstadd'], align = 'C')
				pdf.multi_cell(w=160, h = 5, txt ="GSTIN/UIN:"+session['ownergst'], align = 'C')
				#state and code
				pdf.multi_cell(w=160, h = 5, txt ="State:"+session['state']+" Code:"+statecode_lookup[state.strip()], align = 'C')
				pdf.set_font("Arial", "B", 12)
				pdf.multi_cell(w=160, h = 5, txt ="")
				pdf.multi_cell(w=160, h = 5, txt ="Rental Invoice", align = 'C')
				pdf.multi_cell(w=160, h = 5, txt ="")
				pdf.set_font("Arial", "", 9)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=50, h = 8, txt ="Party:", align = 'L')
				pdf.set_xy(xpos+10,ypos)
				pdf.set_font("Arial", "B", 9)
				pdf.multi_cell(w=160, h = 5, txt =session['tenantname'])
				pdf.set_font("Arial", "", 9)
				pdf.set_xy(xpos+10,ypos+5)
				pdf.multi_cell(w=100, h = 5, txt =session['premise'], align = 'L')
				pdf.multi_cell(w=50, h = 5, txt ="GSTIN/UIN:"+session['tenantgst'], align = 'L')
				#check igst for state
				if igstflag:
					pdf.multi_cell(w=100, h = 8, txt ="State:"+igststate+" Code:"+statecode_lookup[igststate.upper().strip()], align = 'L')
				else:
					pdf.multi_cell(w=100, h = 8, txt ="State:"+session['state']+" Code:"+statecode_lookup[state.strip()], align = 'L')
				#tabular
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=10, h = 8, txt = "Sl No", border = "LTBR", align = 'L', fill = False)
				pdf.set_xy(xpos+10, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=40, h = 8, txt = "Particulars", border = "LTBR", align = 'C', fill = False)
				pdf.set_xy(xpos+40, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=20, h = 8, txt = "HSN/SAC", border = "LTBR", align = 'C', fill = False)
				pdf.set_xy(xpos+20, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=30, h = 8, txt = "Quantity", border = "LTBR", align = 'C', fill = False)
				pdf.set_xy(xpos+30, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=15, h = 8, txt = "Rate %", border = "LTBR", align = 'C', fill = False)
				pdf.set_xy(xpos+15, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=50, h = 8, txt = "Amount", border = "LTBR", align = 'C', fill = False)
				if isinstance(inrbt,str):
					inrbt =myround(float(inrbt))
				if isinstance(insgst,str):
					insgst =round(float(insgst.strip()),2)
				if isinstance(incgst,str):
					incgst =round(float(incgst.strip()),2)
				if isinstance(intotalrent,str):
					intotalrent =myround(float(intotalrent))
				if isinstance(wsdgshare,str):
					wsdgshare = myround(float(wsdgshare))
				if isinstance(netamt,str):
					netamt =myround(float(netamt))
				else:
					netamt = myround(netamt)
				if isinstance(intotalgst,str):
					intotalgst =round(float(intotalgst),2)
				#inigst = intotalgst
				if isinstance(inigst,str):
					inigst =round(float(inigst.strip()),2)
				rbtformat = str("{}".format(currency_in_indian_format(inrbt))) 
				sgstformat = str("{}".format(currency_in_indian_format(insgst)))
				cgstformat = str("{}".format(currency_in_indian_format(incgst)))
				igstformat = str("{}".format(currency_in_indian_format(inigst)))
				if session['owner'] == "BENCY & COMPANY":
					newtotalformat = str("{}".format(currency_in_indian_format(netamt)))
				else:
					newtotalformat = str("{}".format(currency_in_indian_format(intotalrent)))
				newgstformat = str("{}".format(currency_in_indian_format(intotalgst)))
				dgshareformat = str("{}".format(currency_in_indian_format(wsdgshare)))
				strip_newtotal = newtotalformat.replace(',','')
				strip_newgst = newgstformat.replace(',','')
				if tdsneeded:
					ptdsamt = float(tdsamt)
					tdsformat = str("{}".format(currency_in_indian_format(ptdsamt)))
				#detail line
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=10, h = 8, txt = "1", border = "LR", align = 'L', fill = False)
				pdf.set_xy(xpos+10, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "B", 9)
				pdf.multi_cell(w=40, h = 8, txt = "Rent", border = "LR", align = 'C', fill = False)
				pdf.set_xy(xpos+40, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "", 9)
				pdf.multi_cell(w=20, h = 8, txt = "997212", border = "LR", align = 'C', fill = False)
				pdf.set_xy(xpos+20, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
				pdf.set_xy(xpos+30, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=15, h = 8, txt = "", border = "LR", align = 'R', fill = False)
				pdf.set_xy(xpos+15, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "B", 9)
				pdf.multi_cell(w=50, h = 8, txt = rbtformat, border = "LR", align = 'R', fill = False)
				#check if it is igst invoice and print accordingly
				if igstflag:
					#igst line
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=10, h = 8, txt = "", border = "LR", align = 'L', fill = False)
					pdf.set_xy(xpos+10, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=40, h = 8, txt = "IGST", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+40, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "", 9)
					pdf.multi_cell(w=20, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+30, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=15, h = 8, txt = "18%", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+15, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=50, h = 8, txt = igstformat, border = "LR", align = 'R', fill = False)
				else: #not igst invoice
					#sgst line
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=10, h = 8, txt = "", border = "LR", align = 'L', fill = False)
					pdf.set_xy(xpos+10, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=40, h = 8, txt = "SGST", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+40, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "", 9)
					pdf.multi_cell(w=20, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+30, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=15, h = 8, txt = "9%", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+15, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=50, h = 8, txt = sgstformat, border = "LR", align = 'R', fill = False)

					#cgstline
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=10, h = 8, txt = "", border = "LR", align = 'L', fill = False)
					pdf.set_xy(xpos+10, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=40, h = 8, txt = "CGST", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+40, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "", 9)
					pdf.multi_cell(w=20, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+30, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=15, h = 8, txt = "9%", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+15, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=50, h = 8, txt = cgstformat, border = "LR", align = 'R', fill = False)
				#endif igstflag check
				#dgshare
				emptyline = 3
				if session['owner'] == "BENCY & COMPANY" and wsdgshare > 0:
					emptyline = 2
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=10, h = 8, txt = "", border = "LR", align = 'L', fill = False)
					pdf.set_xy(xpos+10, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=40, h = 8, txt = "DG SHARE", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+40, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "", 9)
					pdf.multi_cell(w=20, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+30, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=15, h = 8, txt = "", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+15, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=50, h = 8, txt = dgshareformat, border = "LR", align = 'R', fill = False)
				#endif dgshare line	
				#leave some blank lines with same format (for future details change)
				if tdsneeded:
					#tds line
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=10, h = 8, txt = "", border = "LR", align = 'L', fill = False)
					pdf.set_xy(xpos+10, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=40, h = 8, txt = "Less TDS", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+40, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "", 9)
					pdf.multi_cell(w=20, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+30, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=15, h = 8, txt = tdspercent+"%", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+15, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=50, h = 8, txt = "-"+tdsformat, border = "LR", align = 'R', fill = False)
					emptyline = emptyline - 1
				#endif tdsneeded
				for z in range(1,emptyline):
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=10, h = 8, txt = "", border = "LR", align = 'L', fill = False)
					pdf.set_xy(xpos+10, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=40, h = 8, txt = "", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+40, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "", 9)
					pdf.multi_cell(w=20, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=30, h = 8, txt = "", border = "LR", align = 'C', fill = False)
					pdf.set_xy(xpos+30, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=15, h = 8, txt = "", border = "LR", align = 'R', fill = False)
					pdf.set_xy(xpos+15, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.set_font("Arial", "B", 9)
					pdf.multi_cell(w=50, h = 8, txt = "", border = "LR", align = 'R', fill = False)
				#last Total line
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=10, h = 8, txt = "", border = "BLRT", align = 'L', fill = False)
				pdf.set_xy(xpos+10, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "B", 9)
				pdf.multi_cell(w=40, h = 8, txt = "Total", border = "BLRT", align = 'R', fill = False)
				pdf.set_xy(xpos+40, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "", 9)
				pdf.multi_cell(w=20, h = 8, txt = "", border = "BLRT", align = 'C', fill = False)
				pdf.set_xy(xpos+20, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=30, h = 8, txt = "", border = "BLRT", align = 'C', fill = False)
				pdf.set_xy(xpos+30, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=15, h = 8, txt = "", border = "BLRT", align = 'R', fill = False)
				pdf.set_xy(xpos+15, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "B", 9)
				#raw_text = "\u20B9"
				pdf.multi_cell(w=50, h = 8, txt = "INR "+newtotalformat, border = "BLRT", align = 'R', fill = False)
				pdf.set_font("Arial", "", 7)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=50, h = 5, txt = "Amount Chargeable (in words)",  align = 'L', fill = False)
				pdf.set_xy(xpos+120,ypos)
				pdf.multi_cell(w=50, h = 5, txt = "E. & O.E",  align = 'R', fill = False)
				totalwords = word(strip_newtotal)
				pdf.set_font("Arial", "B", 9)
				pdf.multi_cell(w=160, h = 8, txt = "INR "+totalwords+" only",  align = 'L', fill = False)
				#second table
				pdf.set_font("Arial", "", 8)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=20, h = 5, txt = "HSN/SAC", border = "LTR", align = 'C', fill = False)
				pdf.set_xy(xpos+20, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				if igstflag:
					pdf.multi_cell(w=35, h = 5, txt = "Taxable", border = "LTR", align = 'C', fill = False)
					pdf.set_xy(xpos+35, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=65, h = 5, txt = "Integrated Goods and Services Tax", border = "LTBR", align = 'C', fill = False)
					pdf.set_xy(xpos+65, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					#pdf.multi_cell(w=35, h = 5, txt = "State Tax", border = "LTBR", align = 'C', fill = False)
					#pdf.set_xy(xpos+35, ypos)
					#ypos = pdf.get_y()
					#xpos = pdf.get_x()
					pdf.multi_cell(w=40, h = 5, txt = "Total", border = "LTR", align = 'C', fill = False)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					#2nd line
					pdf.multi_cell(w=20, h = 5, txt = "", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=35, h = 5, txt = "Value", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+35, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=27, h = 5, txt = "Rate", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+27, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=38, h = 5, txt = "Amount", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+38, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					#pdf.multi_cell(w=17, h = 5, txt = "Rate", border = "LRB", align = 'C', fill = False)
					#pdf.set_xy(xpos+17, ypos)
					#ypos = pdf.get_y()
					#xpos = pdf.get_x()
					#pdf.multi_cell(w=18, h = 5, txt = "Amount", border = "LRB", align = 'C', fill = False)
					#pdf.set_xy(xpos+18, ypos)
					#ypos = pdf.get_y()
					#xpos = pdf.get_x()
				else: #not igst invoice
					pdf.multi_cell(w=35, h = 5, txt = "Taxable", border = "LTR", align = 'C', fill = False)
					pdf.set_xy(xpos+35, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=35, h = 5, txt = "Central Tax", border = "LTBR", align = 'C', fill = False)
					pdf.set_xy(xpos+35, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=35, h = 5, txt = "State Tax", border = "LTBR", align = 'C', fill = False)
					pdf.set_xy(xpos+35, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=40, h = 5, txt = "Total", border = "LTR", align = 'C', fill = False)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					#2nd line
					pdf.multi_cell(w=20, h = 5, txt = "", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+20, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=35, h = 5, txt = "Value", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+35, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=17, h = 5, txt = "Rate", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+17, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=18, h = 5, txt = "Amount", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=17, h = 5, txt = "Rate", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+17, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=18, h = 5, txt = "Amount", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
				#endif igstflag check
				pdf.multi_cell(w=40, h = 5, txt = "Tax Amount", border = "LRB", align = 'C', fill = False)

				# 3rd line values
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=20, h = 5, txt = "997212", border = "LRB", align = 'C', fill = False)
				pdf.set_xy(xpos+20, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=35, h = 5, txt = rbtformat, border = "LRB", align = 'C', fill = False)
				pdf.set_xy(xpos+35, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				if igstflag:
					pdf.multi_cell(w=27, h = 5, txt = "18%", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+27, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=38, h = 5, txt = igstformat, border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+38, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					#pdf.multi_cell(w=17, h = 5, txt = "9%", border = "LRB", align = 'C', fill = False)
					#pdf.set_xy(xpos+17, ypos)
					#ypos = pdf.get_y()
					#xpos = pdf.get_x()
					#pdf.multi_cell(w=18, h = 5, txt = sgstformat, border = "LRB", align = 'C', fill = False)
					#pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=40, h = 5, txt = newgstformat, border = "LRB", align = 'C', fill = False)
				else:
					pdf.multi_cell(w=17, h = 5, txt = "9%", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+17, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=18, h = 5, txt = cgstformat, border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=17, h = 5, txt = "9%", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+17, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=18, h = 5, txt = sgstformat, border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=40, h = 5, txt = newgstformat, border = "LRB", align = 'C', fill = False)
				#last line of 2nd table
				pdf.set_font("Arial", "B", 8)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=20, h = 5, txt = "Total", border = "LRB", align = 'R', fill = False)
				pdf.set_xy(xpos+20, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=35, h = 5, txt = rbtformat, border = "LRB", align = 'C', fill = False)
				pdf.set_xy(xpos+35, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				if igstflag:
					pdf.multi_cell(w=27, h = 5, txt = "", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+27, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=38, h = 5, txt = igstformat, border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+38, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					#pdf.multi_cell(w=17, h = 5, txt = "", border = "LRB", align = 'C', fill = False)
					#pdf.set_xy(xpos+17, ypos)
					#ypos = pdf.get_y()
					#xpos = pdf.get_x()
					#pdf.multi_cell(w=18, h = 5, txt = sgstformat, border = "LRB", align = 'C', fill = False)
					#pdf.set_xy(xpos+18, ypos)
					#ypos = pdf.get_y()
					#xpos = pdf.get_x()
					pdf.multi_cell(w=40, h = 5, txt = newgstformat, border = "LRB", align = 'C', fill = False)
				else:
					pdf.multi_cell(w=17, h = 5, txt = "", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+17, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=18, h = 5, txt = cgstformat, border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=17, h = 5, txt = "", border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+17, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=18, h = 5, txt = sgstformat, border = "LRB", align = 'C', fill = False)
					pdf.set_xy(xpos+18, ypos)
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=40, h = 5, txt = newgstformat, border = "LRB", align = 'C', fill = False)
				gstwords = word(strip_newgst)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "", 9)
				pdf.multi_cell(w=160, h = 8, txt = "Tax Amount (in words) :", border = "", align = 'L', fill = False)
				pdf.set_xy(xpos+40, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.set_font("Arial", "B", 9)
				pdf.multi_cell(w=140, h = 8, txt = "INR "+ gstwords +" only", border = "", fill = False)
				pdf.set_font("Arial", "I", 8)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=30, h = 5, txt = "Remarks:", border = "", align = "L", fill = False)
				pdf.set_xy(xpos+80, ypos)
				pdf.set_font("Arial", "", 9)
				pdf.multi_cell(w=50, h = 5, txt = "Company's Bank Details:", border = "", fill = False)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				if reprint or editinvflag:
					pdf.multi_cell(w=80, h = 5, txt = changeremarks, border = "", fill = False)
				else:
					pdf.multi_cell(w=80, h = 5, txt = session['wsremarks'], border = "", fill = False)
				pdf.set_xy(xpos+80, ypos)
				pdf.set_font("Arial", "B", 7)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=80, h = 5, txt = bank1, border = "", fill = False)
				pdf.set_xy(xpos, ypos+3)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=80, h = 5, txt = bank2, border = "", fill = False)
				pdf.set_xy(xpos, ypos+3)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=80, h = 5, txt = bank3, border = "", fill = False)
				pdf.set_xy(xpos, ypos+3)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=80, h = 5, txt = bank4, border = "", fill = False)
				pdf.set_xy(xpos, ypos+3)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=80, h = 5, txt = bank5, border = "", fill = False)
				pdf.set_xy(xpos, ypos+3)
				if bank6 != "nil" :
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=80, h = 5, txt = bank6, border = "", fill = False)
					pdf.set_xy(xpos, ypos+3)
				if bank7 != "nil":
					ypos = pdf.get_y()
					xpos = pdf.get_x()
					pdf.multi_cell(w=80, h = 5, txt = bank7, border = "", fill = False)
				pdf.set_font("Arial", "", 8)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				pdf.multi_cell(w=80, h = 5, txt = "", border = "", align = "L",fill = False)
				pdf.set_font("Arial", "B", 8)
				pdf.set_xy(xpos, ypos)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				namelen = len(session['owner'])
				pos = 160 - namelen
				pdf.set_xy(pos, ypos)
				#too long owner names to fit in
				print_owner = session['owner']
				if len(print_owner) > 48:
					ownerpart1 = print_owner[:48]+"-"
					ownerpart2 = print_owner[48:]
					pdf.multi_cell(w=160,  h = 5, txt = ownerpart1, border = "",fill = False)
					ypos = ypos + 5
					pdf.set_xy(pos, ypos)
					pdf.multi_cell(w=160,  h = 5, txt = ownerpart2, border = "",fill = False)
				else:
					pdf.multi_cell(w=160,  h = 5, txt = print_owner, border = "",fill = False)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				#CR#2 Begin
				#dummy lines 3
				pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
				pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
				pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
				#pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
				ypos = pdf.get_y()
				xpos = pdf.get_x()
				#CR#2 End
				pdf.set_xy(xpos, ypos)
				pdf.multi_cell(w=160, h = 5, txt = "Authorised Signatory", border = "", align = "R",fill = False)
				pdf.set_font("", "U", 7)
				pdf.multi_cell(w=180, h = 5, txt = "This is a computer generated invoice and does not require signature", border = "", align = "C",fill = False)
				invforpdfname = newinvno.replace("/", "_")
				invforpdfname = invforpdfname+"-"+session['tenantgst']
				invforpdfname = invforpdfname.replace(" ","_")
				newpdfname = "Invoice_"+ invforpdfname+".pdf"
				pathpdfname = mydrive + staticpath + newpdfname
				pdf.output(pathpdfname)
				if cancelflag:
					#merge with the watermark
					mergecommand = "pdftk "+ pathpdfname + \
					" background " + mydrive + staticpath + "canwatermark.pdf output " + \
					mydrive + staticpath + "Cancel_"+ invforpdfname +".pdf"
					os.system(mergecommand)
					session['pdf_file'] = "Cancel_"+ invforpdfname +".pdf"
					cancelflag = False
				else:
					session['pdf_file'] = newpdfname
				cancelflag = False
				

#end of pdfcreate


@RentInvoice.route('/showpdf',methods = ['POST', 'GET'])
def showpdf():
	global pathpdfname
	global receiver, tenantemail, changetenantemail, reprint, cancelflag, editinvflag
	global inproperty, newinvno, tenantgst, newinvdate, proper_newinvdate, proper_changeinvdate
	global staticpath, thisenv, owner
	global calmallsno
	global cancelkey, selkey, tdsamt, tdsneeded
	global prevtotalrent, changeremarks, tenantphone
	global igstflag, igststate, inigst
	if request.method == 'POST':
		if request.form['submit_button'] == 'Send mail':
			session['justmailed'] = False
			wspdfname = session['pdf_file']
			if 'Cancel' in wspdfname:
				pdfcancel = True
			else:
				pdfcancel = False
			if editinvflag or reprint or pdfcancel:
				receiver = session['tenantemail']
			else:
				if not pdfcancel:
					receiver = tenantemail
			if thisenv == "Development":
				receiver = 'ramadas@kappsoft.com'
			if receiver == "nil":
				receiver = 'anees@emarald.in'
			message = MIMEMultipart()
			message['From'] = "rentalinvoices@emarald.in"
			message['To'] = receiver
			message['Subject'] =  " Rental Invoice Attached "
			bodytext = "Please open attachment for Rental Invoice\n"
			bodytext = bodytext + "Property: "+session['premise']+"\n"
			bodytext = bodytext + "Belonging to: "+session['owner']+"\n"
			message.attach(MIMEText(bodytext, 'plain'))
			pdfname = pathpdfname
			# open the file in bynary
			try:
				binary_pdf = open(pdfname, 'rb')
			except FileNotFoundError:
				text_box.insert(END, 'Not found:'+pdfname+'\n')
				#print ('Not found:',pdfname)
			payload = MIMEBase('application', 'octate-stream', Name=pdfname)
			# payload = MIMEBase('application', 'pdf', Name=pdfname)
			payload.set_payload((binary_pdf).read())
			#print ('done payload')

			# enconding the binary into base64
			encoders.encode_base64(payload)
			#print ('done encoding the binary')

			# add header with pdf name
			payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
			message.attach(payload)
			#print ('done header with pdf name')
			#use mail with port
			mailsession = smtplib.SMTP('mail.emarald.in', 587, timeout=360)
			# print ('done port of webmail')
			#enable security
			mailsession.starttls()
			#print ('done sessions.starttls')
			#login with mail_id and password
			sender = "rentalinvoices@emarald.in"
			empassword = "Emarald123#"
			mailsession.login(sender, empassword)
			#print ('done mail sessions login')
			text = message.as_string()
			mailsession.sendmail(sender, receiver, text)
			textline = 'sent mail to '+ receiver+'\n'
			session['justmailed'] = True
			#print ('sent mail to ', receiver )
			mailsession.quit()
			session['receiver'] = receiver
			global intotalrent
			if pdfcancel:
				now = datetime.now()
				rquery = { "InvoiceTenantGSTKey" : cancelkey }
				nval = { "$set": 
										{ 
										 "TimeStamp": now,
										 "InvoiceTenantGSTKey" : "Cancel_"+cancelkey
										}
							}
				Invoice_dbCollection.update_one(rquery, nval)
				
				NewLedgerDict = {
						"TransTimeStamp": now, 
						"Narration1" : "Cancel_"+cancelkey,
						"Amount" : intotalrent,
						"CreditAccountHead" : session['tenantname'],
						"DebitAccountHead" : "RENTS RECEIVABLE",
						"UpdatedBy" : session['username']
					}
				newledger = Rent_Ledger.insert_one(NewLedgerDict)
			#endif pdfcancel
			if not reprint and not pdfcancel and not editinvflag:
				#store invoice and append rent ledger
				now = datetime.now()
				invtengstkey = inproperty + "~" + newinvno+"~"+tenantgst
				#Check whether the same key record is there, if so add one to version
				vers = []
				vercount = 0
				doc_count  = Invoice_dbCollection.count_documents({"InvoiceTenantGSTKey" : invtengstkey})
				findwithkey = Invoice_dbCollection.find({"InvoiceTenantGSTKey" : invtengstkey})
				if doc_count > 0:
					maxval = doc_count
					vercount = 0
					for doc in findwithkey:
						vers.append(doc.get("Record Version"))   
						if vers[vercount] > maxval:
							maxval = vers[vercount]
							vercount = vercount + 1
					presentversion = maxval + 1
				else:
					presentversion = 1
					global owner, tenantphone, bank1, bank2, bank3, bank4, bank5, bank6
					global rbt, sgst, cgst, totalrent, totalgst
					global inrbt, insgst, ingst, intotalgst, calmallsno, wsdgshare, netamt
					global inigst
					NewInvoiceDict = { 
						"TimeStamp": now, 
						"InvoiceTenantGSTKey" : invtengstkey,
						"Record Version" : presentversion,
						"Property No": int(inproperty),
						"Invoice Date": proper_newinvdate,
						"Invoice No": newinvno,
						"Tenant GST No": tenantgst,
						"Premise Address": session['premise'],
						"Tenant Email ID": session['tenantemail'],
						"Tenant Contact No": tenantphone,
						"State": session['state'],
						"Rental Type": "Commercial",
						"OWNER OF THE PREMISE": owner,
						"OWNER GST ADDRESS": session['ownergstadd'],
						"OWNER GST NO": session['ownergst'],
						"OWNER BANK ACCOUNT L1": bank1,
						"OWNER BANK ACCOUNT L2": bank2,
						"OWNER BANK ACCOUNT L3": bank3,
						"OWNER BANK ACCOUNT L4": bank4,
						"OWNER BANK ACCOUNT L5": bank5,
						"OWNER BANK ACCOUNT L6": bank6,
						"OWNER BANK ACCOUNT L7": bank7,
						"Tenant Name": session['tenantname'],
						"RBT": inrbt,
						"SGST": insgst,
						"CGST": incgst,
						"Total Rent": intotalrent,
						"TDS": float(tdsamt),
						"RAT": intotalrent,
						"TDSPER" : int(tdspercent),
						"Remarks": session['wsremarks'],
						"GST Part": intotalgst,
						"Commencement Date": "",
						"Expiry Date": "",
						"RENT": 0,
						"Received" : 0,
						"Dispute in Credit" : 0,
						"Received Month" :"",
						"Receipt Narration" : "",
						"Security Deposit":"",
						"DGShare" : wsdgshare,
						"NETAMT" : netamt,
						"IGSTFLAG" : igstflag,
						"IGSTState" : igststate,
						"IGST": inigst,
						"UpdatedBy" : session['username']
					}
					newdoc  = Invoice_dbCollection.insert_one(NewInvoiceDict)
					#rent ledger update 
					NewLedgerDict = {
						"TransTimeStamp": now, 
						"Narration1" : invtengstkey,
						"Amount" : intotalrent,
						"DebitAccountHead" : session['tenantname'],
						"CreditAccountHead" : "RENTS RECEIVABLE",
						"UpdatedBy" : session['username']
					}
					newledger = Rent_Ledger.insert_one(NewLedgerDict)
					#tds update in rent ledger
					if tdsneeded:
						NewLedgerDict = {
							"TransTimeStamp": now, 
							"Narration1" : invtengstkey+ "TDS FROM "+ session['tenantname'] ,
							"Amount" : float(tdsamt),
							"DebitAccountHead" : "RENTS RECEIVABLE",
							"CreditAccountHead" : "TDS FROM "+ session['tenantname'],
							"UpdatedBy" : session['username']
						}
						newledger = Rent_Ledger.insert_one(NewLedgerDict)
					#update the last invoice number in CalMallLastInvoice table in that case
					if owner == "BENCY & COMPANY" :
						lookno = calmallsno - 1
						rectquery = { "LastInvoice" : lookno }
						newval = { "$set": 
										{ 
										"LastInvoice" : calmallsno
										}
							}
						calmalllastinvoice.update_one(rectquery, newval)
			#endif (not reprint)
			if editinvflag:
				#Check whether the same key record is there, if so add one to version
				vers = []
				vercount = 0
				doc_count  = Invoice_dbCollection.count_documents({"InvoiceTenantGSTKey" : selkey})
				findwithkey = Invoice_dbCollection.find({"InvoiceTenantGSTKey" : selkey})
				if doc_count > 0:
					maxval = doc_count
					vercount = 0
					for doc in findwithkey:
						vers.append(doc.get("Record Version"))   
						if int(vers[vercount]) > maxval:
							maxval = vers[vercount]
							vercount = vercount + 1
					presentversion = maxval + 1
				now = datetime.now()
				NewInvoiceDict = { 
						"TimeStamp": now, 
						"InvoiceTenantGSTKey" : "Edited_"+selkey,
						"Record Version" : presentversion,
						"Property No": int(inproperty),
						"Invoice Date": proper_changeinvdate,
						"Invoice No": newinvno,
						"Tenant GST No": tenantgst,
						"Premise Address": session['premise'],
						"Tenant Email ID": session['tenantemail'],
						"Tenant Contact No": tenantphone,
						"State": session['state'],
						"Rental Type": "Commercial",
						"OWNER OF THE PREMISE": owner,
						"OWNER GST ADDRESS": session['ownergstadd'],
						"OWNER GST NO": session['ownergst'],
						"OWNER BANK ACCOUNT L1": bank1,
						"OWNER BANK ACCOUNT L2": bank2,
						"OWNER BANK ACCOUNT L3": bank3,
						"OWNER BANK ACCOUNT L4": bank4,
						"OWNER BANK ACCOUNT L5": bank5,
						"OWNER BANK ACCOUNT L6": bank6,
						"OWNER BANK ACCOUNT L7": bank7,
						"Tenant Name": session['tenantname'],
						"RBT": inrbt,
						"SGST": insgst,
						"CGST": incgst,
						"Total Rent": intotalrent,
						"TDS": float(tdsamt),
						"TDSPER" : int(tdspercent),
						"RAT": intotalrent,
						"Remarks": changeremarks,
						"GST Part": intotalgst,
						"Commencement Date": "",
						"Expiry Date": "",
						"RENT": 0,
						"Received" : 0,
						"Dispute in Credit" : 0,
						"Received Month" :"",
						"Receipt Narration" : "",
						"Security Deposit":"",
						"DGShare" : wsdgshare,
						"NETAMT" : netamt,
						"IGSTFLAG" : igstflag,
						"IGSTState" : igststate,
						"IGST": inigst,
						"UpdatedBy" : session['username']
					}
				newdoc  = Invoice_dbCollection.insert_one(NewInvoiceDict)
				#rent ledger update 
				NewLedgerDict = {
					"TransTimeStamp": now, 
					"Narration1" : "Edited_"+selkey,
					"Amount" : intotalrent,
					"DebitAccountHead" : session['tenantname'],
					"CreditAccountHead" : "RENTS RECEIVABLE",
					"UpdatedBy" : session['username']
				}
				newledger = Rent_Ledger.insert_one(NewLedgerDict)
				NewLedgerDict = {
					"TransTimeStamp": now, 
					"Narration1" : "Edited_"+selkey,
					"Amount" : prevtotalrent,
					"DebitAccountHead" : "RENTS RECEIVABLE",
					"CreditAccountHead" : session['tenantname'],
					"UpdatedBy" : session['username']
				}
				newledger = Rent_Ledger.insert_one(NewLedgerDict)
			#endif (editinvflag)
			#copy pdf file to proper user path and delete it from static path
			source = mydrive+ staticpath +session['pdf_file']
			destination = mydrive+"/PAYMENTS/Renting/"+session['pdf_file']
			shutil.copy2(source, destination)
			reprint = False
			cancelflag = False
			pdfcancel = False
			editinvflag = False
			tdsneeded = False
			igstflag = False
			igststate =""
			session['igststate'] =""
			session['igstflag'] = False
			inigst = 0.00
			return  redirect(url_for('downloadpdf'))
				
		elif request.form['submit_button'] == 'Exit':
			return  redirect(url_for('InvoiceMenu'))
	return render_template('showpdf.html')

@RentInvoice.route('/InvoiceMenu',methods = ['POST', 'GET'])
def InvoiceMenu():
	return render_template('InvoiceMenu.html')

@RentInvoice.route('/invoicegenerate', methods=['GET', 'POST'])
def invoicegenerate():
	global inproperty, inv34, tdsneeded, tdspercent, tdsamt
	global pathpdfname, calmalllastinvoice
	global  bank1, bank2, bank3, bank4, bank5, bank6, bank7, owner, newinvno
	global  tenantgst, newinvdate, state, owner, rbt, sgst, cgst, totalrent
	global totalgst, remarks, tenantphone, tenantemail, proper_newinvdate
	global inrbt, insgst, incgst, intotalrent, intotalgst
	global calmallsno, wsdgshare, netamt
	global igstflag, inigst, igststate
	global yyyychoice
	todayDay = datetime.now().day
	todayMonth = datetime.now().month
	todayYear = datetime.now().year
	#todayMonth = 4 #uncomment for demo purpose
	#todayDay = 15 #uncomment for demo purpose
	if (todayMonth >= 4 and todayMonth < 6  ) :
		#april and may
		session['chooseyyyy'] = True
		thisyy = str(todayYear)[2:]
		nextyy = str(int(thisyy) + 1)
		prevyy = str(int(thisyy) - 1)
		session['prevyyyy'] = prevyy+"-"+thisyy
		session['presyyyy'] = thisyy+"-"+nextyy
		session['finyrchosen'] = False
	else: #not financial year changing period
		session['chooseyyyy'] = False
		session['prevyyyy'] = ""
		session['presyyyy'] = ""
		session['finyrchosen'] = True
		#usual period
	#endif (financial year changing period)
	allprop = list(Invoice_dbCollection.find({}))
	proplist =[]
	for rec in allprop:
		proplist.append(rec.get("Property No"))
	proplist = sorted(set(proplist))
	session['proplist'] = proplist
	if request.method == 'POST':
		if request.form['submit_button'] == 'Get Financial Year':
			if session.get('chooseyyyy'):
				yyyychoice = request.form['yyyychoice']
				session['yyyychoice'] = yyyychoice
				#print(yyyychoice)
			else:
				#print("no choice")
				session['yyyychoice'] = ""
				yyyychoice =""
			#endif (april month )
			session['finyrchosen'] = True
		elif request.form['submit_button'] == 'Get Invoice Key':
			#Property No
			inproperty = request.form['property'] 
			proplist = []
			proplist.append(inproperty)
			session['proplist'] = proplist
			if isinstance(inproperty, str):
				recbysno  = list(Invoice_dbCollection.find({"Property No" : int(inproperty)}))
			else:
				recbysno  = list(Invoice_dbCollection.find({"Property No" : inproperty}))
			keylist=[]
			for rec in recbysno:
				keylist.append(rec.get("InvoiceTenantGSTKey"))
			session['invkey'] = keylist
			post1 = True
			session['finyrchosen'] = True
		elif request.form['submit_button'] == 'Get Invoice Details':
			proplist = []
			proplist.append(inproperty)
			session['proplist'] = proplist
			selkey = request.form['invkey'] 
			keylist = []
			keylist.append(selkey)
			session['invkey'] = keylist
			invrec = list(Invoice_dbCollection.find({"InvoiceTenantGSTKey" : selkey}))
			for rec in invrec:
				session['invno'] = rec.get("Invoice No")
				session['owner'] = rec.get("OWNER OF THE PREMISE")
				session['premise'] = rec.get("Premise Address")
				session['ownergst'] = rec.get("OWNER GST NO")
				session['tenantgst'] = rec.get("Tenant GST No")
				session['ownergstadd'] = rec.get("OWNER GST ADDRESS")
				session['state'] = rec.get("State")
				session['tenantname'] = rec.get("Tenant Name")
				wsphone = rec.get("Tenant Contact No")
				if '.' in wsphone:
					phone, useless = wsphone.split('.')
				else:
					phone = wsphone
				session['tenantphone'] = phone
				session['tenantemail'] = rec.get("Tenant Email ID")
				session['rbt'] = rec.get("RBT")
				#dg share for emarald mall 26 Jul
				session['dgshare'] = rec.get("DGShare")
				wsdgshare = rec.get("DGShare")
				#igst change
				session['igststate'] = "NOT IGST"
				if rec.get("IGSTFLAG"):
					session['igststate'] = rec.get("IGSTState")
					igststate = rec.get("IGSTState")
					session['igst'] = rec.get("IGST")
					igstflag = True
				else:
					session['igststate'] = "NOT IGST"
					igststate = "NOT IGST"
					session['igst'] = 0.00
					igstflag = False
				session['netamt'] = rec.get("NETAMT")
				session['tds'] = rec.get("TDS")
				session['rat'] = rec.get("RAT")
				if not isinstance(rec.get("RBT"),str):
					session['rbt'] = myround(rec.get("RBT"))
					#session['rbt'] = "{:.2f}".format(rec.get("RBT"))
				if not isinstance(rec.get("TDS"),str):
					session['tds'] = myround(rec.get("TDS"))
					#session['tds'] = "{:.2f}".format(rec.get("TDS")) 
				if not isinstance(rec.get("RAT"),str):
					session['rat'] = myround(rec.get("RAT")) 
					#session['rat'] = "{:.2f}".format(rec.get("RAT")) 
				session['remarks'] = rec.get("Remarks")
				session['rentrecd'] = rec.get("Received")
				session['dispamt'] = rec.get("Dispute in Credit")
				session['recddate'] = rec.get("Received Month")
				session['narration'] = rec.get("Receipt Narration")
				bank1 = " "
				bank2 = " "
				bank3 = " "
				bank4 = " "
				bank5 = " "
				bank6 = " "
				bank7 = " "
				bank1 = rec.get("OWNER BANK ACCOUNT L1")
				bank2 = rec.get("OWNER BANK ACCOUNT L2")
				bank3 = rec.get("OWNER BANK ACCOUNT L3")
				bank4 = rec.get("OWNER BANK ACCOUNT L4")
				bank5 = rec.get("OWNER BANK ACCOUNT L5")
				bank6 = rec.get("OWNER BANK ACCOUNT L6")
				bank7 = rec.get("OWNER BANK ACCOUNT L7")
				session['bank'] = bank1 +" " +\
						bank2 + " " +\
						bank3 + " " +\
						bank4 + " " +\
						bank5 + " " + \
						bank6 + " " + \
						bank7
				state =  session['state']
				owner = session['owner']
				#Generate new Invoice number
				#Major change 9th January 2022
				#if present month is jan to mar prevyr+thisyear else thisyear+nextyear
				currentMonth = datetime.now().month
				#currentMonth = 4 #uncomment for demo purpose only
				currentYear = datetime.now().year
				prevyr = str(currentYear - 1)
				nextyr = str(currentYear + 1)
				thisyr = str(currentYear)
				if currentMonth < 4:
					invyr = prevyr[-2:]+"-"+thisyr[-2:]
				else:
					invyr = thisyr[-2:]+"-"+nextyr[-2:]
				#financil year change Jan 2023
				if session.get('chooseyyyy'):
					wsfinyear = '-'+yyyychoice+'-'
				else:
					wsfinyear = '-'+invyr+'-'
				stateinv  = list(Invoice_dbCollection.find({"State" : state, "OWNER OF THE PREMISE" : owner, 'Invoice No':{'$regex' : wsfinyear} }))
				maxrunning = 0
				for statedoc in stateinv:
					wsinv = statedoc.get("Invoice No")
					if wsinv != 'nil' and len(wsinv.strip()) != 0 :
						runno = int(wsinv[6:8])
						if runno > maxrunning:
							maxrunning = runno
						#endif
					#endif
				#endfor
				#add 1 to that running number
				new_running = maxrunning + 1
				session['shortnameerr'] = False
				inv01=""
				if len(owner.strip()) == 0 or owner == "nil":
					inv01 = ""
				else:
					owninv  = list(Owners.find({ "OwnerName" : owner }))
					if len(owninv) == 0:
						session['shortnameerr'] = True
						inv01="EE"
					else:
						session['shortnameerr'] = False
						for r in owninv:
							inv01 = r.get("ShortName")
				inv34 = statecode_lookup[state.strip()]
				#invyr = invno[-5:]
				if session.get('chooseyyyy'):
					newinvno = inv01+"/"+inv34+"-"+str(new_running).rjust(2,"0")+"-"+yyyychoice+"-"+inproperty
				else:
					newinvno = inv01+"/"+inv34+"-"+str(new_running).rjust(2,"0")+"-"+invyr+"-"+inproperty
				#different invoice numbering for Emarald Mall -21 07 2022 Change
				#Like this : BC/KL-22-23/182
				if owner.strip() == "BENCY & COMPANY":
					if session.get('chooseyyyy'):
						wsfinyear = yyyychoice
					else:
						wsfinyear = invyr
					bcinv  = list(Invoice_dbCollection.find({'Invoice No':{'$regex' : "BC/KL-"+wsfinyear} }))
					maxrunning_calmall = 0
					for bcinvdoc in bcinv:
						wsbcinv = bcinvdoc.get("Invoice No")
						if wsbcinv != 'nil' and len(wsbcinv.strip()) != 0 :
							bcrunno = int(wsbcinv[12:])
							if bcrunno > maxrunning_calmall:
								maxrunning_calmall = bcrunno
							#endif
						#endif
					#endfor
					#add 1 to that running number
					new_bcrunning = maxrunning_calmall + 1
					calmallsno = new_bcrunning
					#malllastinvoice = calmalllastinvoice.find({})
					#malllastinvoice = list(malllastinvoice)
					#lastinv = 0
					#for irec in malllastinvoice:
					#	lastinv = irec.get("LastInvoice")
					#calmallsno = lastinv + 1
					newinvno = "BC/KL-"+wsfinyear+"/"+str(calmallsno)
				#endif bency
				#new invno generate over
				session['newinvno'] = newinvno
				post2 = True
				session['finyrchosen'] = True
		elif request.form['submit_button'] == 'Create & Mail New Invoice':
				newinvdate = request.form['newinvdate']
				yyyy = newinvdate[0:4]
				mm = newinvdate[5]+newinvdate[6]
				dd = newinvdate[8]+newinvdate[9]
				proper_newinvdate = dd+"."+mm+"."+yyyy
				print(proper_newinvdate)
				session['proper_newinvdate'] = proper_newinvdate
				tenantgst = request.form['tenantgst']
				#igst change
				inigst = 0.00
				igststate = request.form['igststate']
				if igststate == "NOT IGST":
					igstflag = False
					gstflag = request.form['gstflag']
					if gstflag == 'gsty':
						inrbt = request.form['rbt']
						insgst = request.form['sgst']
						incgst = request.form['cgst']
						intotalrent = request.form['totalrent']
						intotalgst = request.form['totalgst']
					else: #no gst
						inrbt = request.form['rbt']
						insgst = 0.00
						incgst = 0.00
						intotalrent = request.form['totalrent']
						intotalgst = 0.00
				else: #it is an igst invoice
						igstflag = True
						inrbt = request.form['rbt']
						inigst = request.form['igst']
						insgst = 0.00
						incgst = 0.00
						intotalrent = request.form['totalrent']
						intotalgst = request.form['totalgst']
				#For TDS 13th Sep 2022
				tdscheckbox = request.form.getlist('tdsinvyes') 
				if len(tdscheckbox) !=0:
					tdsneeded = True
					tdspercent = request.form['tdspercent']
					tdsamt = request.form['tdsamt']
					rentaftertds = request.form['rentaftertds']
					#hey intotalrent becomes rentaftertds here
					intotalrent = request.form['rentaftertds']
				else:
					tdsneeded = False
					tdspercent = "0"
					tdsamt = "0"
					rentaftertds = "0"
				tenantemail = request.form['tenantemail']
				wsdgshare = request.form['dgshare']
				if float(wsdgshare) > 0:
					netamt = float(intotalrent) + float(wsdgshare)
				else:
					netamt = float(intotalrent)
				session['tenantemail'] = tenantemail
				session['renterr'] = False
				if float(intotalrent) < 1:
					session['renterr'] = True
				else:
					session['renterr'] = False
				
				remarks = request.form['remarks']
				session['wsremarks'] = remarks
				print(remarks)
				tenantphone = request.form['tenantphone']
				#Aug 10'2022
				session['tenantname'] = request.form['tenantname']
				#pdf creation
				#
				pdfcreate()
				#
				session['finyrchosen'] = True
				return redirect(url_for('showpdf'))
		elif request.form['submit_button'] == 'Exit':
			for key in list(session.keys()):
				if key != 'username' \
				and key != 'User_type' \
				and key != 'justmailed' \
				and key != 'dummyinvoice' :
					session.pop(key)
			post1 = False
			post2 = False 
			post3 = False
			session['finyrchosen'] = True
			return  redirect(url_for('InvoiceMenu'))
		else:
			session['finyrchosen'] = True
			return render_template('invoicegenerate.html')
	return render_template('invoicegenerate.html')

@RentInvoice.route('/afterlogin/')
def afterlogin():

		gotname = session.get("username")
		gotpassword = session.get("password")
		dbopen()
		global environ
		finduser = Invoice_Users_Collection.find({"User_id" : gotname})
		finduserlist = list(finduser)
		if len(finduserlist) != 0:
			for re_cord in finduserlist:
				dbpassword = re_cord.get("User_password")
				mykey = re_cord.get("User_passkey")
				session['User_type'] = re_cord.get("User_type")
				decoded = cryptocode.decrypt(dbpassword,mykey)
				if decoded == gotpassword:
					error = False
					session['error'] = error
					session['password'] =""
					print(session['username']," logged in at ", datetime.now())
					return redirect(url_for('InvoiceMenu'))
				else:
					error = True
					session['error'] = error
					return  redirect(url_for('rinv'))
			#endfor
		else:
			error = True
			session['error'] = error
			return redirect(url_for('rinv'))

@RentInvoice.route('/forgot1', methods=['GET', 'POST'])
def forgot1():
	dbopen()
	global fpusername
	session['sentotp'] = False
	session['nouser'] = False
	session['noemail'] = False 
	session['nootp'] = False
	session['nomatch'] = False
	if request.method == 'POST':
		if request.form['submit_button'] == 'Mail me one time password':
			fpusername = request.form['fpusername']
			session['fpusername'] = fpusername
			if fpusername is None:
				session['nouser'] = True
				render_template('forgot1.html')
			else:
				session['nouser'] = False
			fpemailid  = request.form['fpemailid']
			finduser = Invoice_Users_Collection.find({"User_id" : fpusername})
			finduserlist = list(finduser)
			if len(finduserlist) == 0:
				session['nouser'] = True
				render_template('forgot1.html')
			else:
				session['nouser'] = False
				for re_cord in finduserlist:
					wsemail = re_cord.get('User_email')
					if wsemail != fpemailid:
						session['noemail'] = True
						render_template('forgot1.html')
					else:
						session['noemail'] = False 
						myotp, mytime = sendotp(wsemail)
						Invoice_Users_Collection.update_one(re_cord, {'$set': {'otp': myotp}})
						finduser = Invoice_Users_Collection.find({"User_id" : fpusername})
						finduserlist = list(finduser)
						for re_cord1 in finduserlist:
							Invoice_Users_Collection.update_one(re_cord1, {'$set': {'otptime': mytime}})
						session['sentotp'] = True
		if request.form['submit_button'] == 'Submit':
			fpusername = session.get('fpusername')
			if fpusername is None:
				session['nouser'] = True
				render_template('forgot1.html')
			else:
				session['nouser'] = False
			finduser = Invoice_Users_Collection.find({"User_id" : fpusername})
			finduserlist = list(finduser)
			otpassword = request.form['otppassword']
			for re_cord in finduserlist:
				storedotp = re_cord.get('otp')
				storedotptime = re_cord.get('otptime')
				timenow = time.time()
				if (timenow - storedotptime) > 180:
					session['nootp'] = True
					render_template('forgot1.html')
				else:
					if storedotp != otpassword:
						session['nootp'] = True
						render_template('forgot1.html')
					else:
						session['nootp'] = False
						newpassword1 = request.form['newpassword1']
						newpassword2 = request.form['newpassword2']
						if newpassword1 != newpassword2:
							session['nomatch'] = True
							render_template('forgot1.html')
						else:
							fpusername = session.get('fpusername')
							if fpusername is None:
								session['nouser'] = True
								render_template('forgot1.html')
							else:
								session['nouser'] = False
							finduser = Invoice_Users_Collection.find({"User_id" : fpusername})
							finduserlist = list(finduser)
							encoded = cryptocode.encrypt(newpassword1,"211219630525")
							for re_cord1 in finduserlist:
								Invoice_Users_Collection.update_one(re_cord1, {'$set': { 
                                	"User_password" : encoded,
                                	"User_passkey"  : "211219630525"
                                }})
							return redirect(url_for('rinv'))
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('rinv'))
	return render_template('forgot1.html')

@RentInvoice.route('/rinv', methods=['GET', 'POST'])
def rinv():
	error = None
	if request.method == 'POST':
		if request.form['submit_button'] == 'Login':
			wsusername = request.form['username'] 
			if session.get('username') == wsusername:
				error = True
				print(wsusername,' has another session logged in')
			session['username'] = wsusername
			session['password'] = request.form['password']
			return redirect(url_for('afterlogin'))
		if request.form['submit_button'] == 'Forgot Password':
			return redirect(url_for('forgot1'))
	return render_template('rinv.html')

def sendotp(emailid):
	receiver = emailid
	digits = "0123456789"
	OTP = ""
	for i in range(5) :
		OTP += digits[math.floor(random.random() * 10)]
	otpgentime = time.time()
	message = MIMEMultipart()
	message['From'] = "rentalinvoices@emarald.in"
	message['To'] = receiver
	message['Subject'] =  " OTP for Rental Invoice Reset Password "
	message.attach(MIMEText(OTP, 'plain'))
	mailsession = smtplib.SMTP('mail.emarald.in', 587, timeout=360)
	mailsession.starttls()
	sender = "rentalinvoices@emarald.in"
	empassword = "Emarald123#"
	mailsession.login(sender, empassword)
	text = message.as_string()
	mailsession.sendmail(sender, receiver, text)
	mailsession.quit()
	return OTP, otpgentime




@RentInvoice.route('/showfiles', methods = ['POST', 'GET'])
def showfiles():
	if request.method == 'POST':
		if request.form['submit_button'] == 'Download':
			gotfilelist = request.form.getlist('selfiles[]')
			zipname = request.form['zipname']
			zipname = zipname+'.zip'
			with zipfile.ZipFile(zipname,'w',  zipfile.ZIP_DEFLATED) as zip:
				for eachfile in gotfilelist:
					zip.write(eachfile)
			zip.close()
			return send_file(zipname)
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('auditview'))
	return render_template('showfiles.html')

@RentInvoice.route('/auditview', methods = ['POST', 'GET'])
def auditview():
	allinvoices = list(Invoice_dbCollection.find({}))
	datelist = []
	for rec in allinvoices:
		if len(str(rec.get("Invoice Date"))) > 0 and len(rec.get("InvoiceTenantGSTKey")) > 0:
			datelist.append(str(rec.get("Invoice Date"))+"|"+rec.get("InvoiceTenantGSTKey"))
	for each_element in datelist:
		if '-' not in each_element[0:10]:
			yyyy = each_element[6:10]
			mm = each_element[3]+each_element[4]
			dd = each_element[0]+each_element[1]
			dispinvdate = yyyy+"-"+mm+"-"+dd
			mod_each_element = each_element[10:]
			each_element = dispinvdate+mod_each_element
	ownerlist = []
	for rec in allinvoices:
		if len(rec.get("OWNER OF THE PREMISE")) > 0 and len(rec.get("State")) > 0:
			ownerlist.append(rec.get("OWNER OF THE PREMISE")+"~"+rec.get("State"))
	ownerlist = sorted(set(ownerlist))
	session['ownerlist'] = ownerlist
	tenlist = []
	for rec in allinvoices:
		if len(rec.get("Tenant Name")) > 0 :
			tenlist.append(rec.get("Tenant Name"))
	tenlist = sorted(set(tenlist))
	session['tenlist'] = tenlist
	statelist = []
	for rec in allinvoices:
		if len(rec.get("State")) > 0:
			statelist.append(rec.get("State"))
	statelist = sorted(set(statelist))
	session['statelist'] = statelist
	proplist = []
	for rec in allinvoices:
		proplist.append(rec.get("Property No"))
	proplist = sorted(set(proplist))
	session['proplist'] = proplist
	invlist = []
	for rec in allinvoices:
		if len(rec.get("Invoice No")) > 0:
			invlist.append(rec.get("Invoice No"))
	invlist = sorted(set(invlist))
	session['invlist'] = invlist
	keylist = []
	for rec in allinvoices:
		if len(rec.get("InvoiceTenantGSTKey")) > 0:
			keylist.append(rec.get("InvoiceTenantGSTKey"))
	keylist = sorted(set(keylist))
	session['keylist'] = keylist

	chosendone = False
	if request.method == 'POST':
		if request.form['submit_button'] == 'Show Invoice PDFs':
			if request.form['downchoice'] == "byowner":
				selownerstate = request.form['selowner']
				ownerpart = selownerstate.split('~')[0]
				statepart = selownerstate.split('~')[1]
				selectedinvoices = list(Invoice_dbCollection.find({"OWNER OF THE PREMISE" : ownerpart, "State": statepart}))
				chosendone = True
			if request.form['downchoice'] == "bystate":
				selstate = request.form['selstate']
				selectedinvoices = list(Invoice_dbCollection.find({"State": selstate}))
				chosendone = True
			if request.form['downchoice'] == "bydate":
				date1 = request.form['frominvdate']
				date2 = request.form['toinvdate']
				if date1 > date2:
					extemp = date1
					date1 = date2
					date2 = extemp
				datelist2 = []
				for each_element in datelist:
					datepart = each_element.split('|')[0]
					if datepart >= date1 and datepart <= date2:
						datelist2.append(each_element)
				chosendone = False 
				pdflist = []
				for z in datelist2:
					key1 =  z.split('|')[1]
					needed_part = key1.split('~')[1]
					if len(needed_part) > 0:
						needed_part = needed_part.replace('/','_')
						needed_part = "*"+needed_part+"*"
						foundfiles = findfile(needed_part, staticpath)
						if len(foundfiles) > 0:
							for z1 in foundfiles:
								pdflist.append(z1)
				pdflist = sorted(set(pdflist))
				session['pdflist'] = pdflist
				return redirect(url_for('showfiles'))
			if request.form['downchoice'] == "byprop":
				selprop = request.form['selprop']
				selectedinvoices = list(Invoice_dbCollection.find({"Property No": int(selprop)}))
				chosendone = True
			if request.form['downchoice'] == "byinvno":
				selinv = request.form['selinv']
				selectedinvoices = list(Invoice_dbCollection.find({"Invoice No": selinv}))
				chosendone = True
			if request.form['downchoice'] == "bydbkey":
				selkey = request.form['selkey']
				selectedinvoices = list(Invoice_dbCollection.find({"InvoiceTenantGSTKey": selkey}))
				chosendone = True
			if request.form['downchoice'] == "bytenant":
				seltenant = request.form['seltenant']
				selectedinvoices = list(Invoice_dbCollection.find({"Tenant Name": seltenant}))
				chosendone = True
			if chosendone:
				pdflist = []
				for z in selectedinvoices:
					key1 = z.get("InvoiceTenantGSTKey")
					needed_part = key1.split('~')[1]
					if len(needed_part) > 0:
						needed_part = needed_part.replace('/','_')
						needed_part = "*"+needed_part+"*"
						foundfiles = findfile(needed_part, mydrive+staticpath)
						if len(foundfiles) > 0:
							for z1 in foundfiles:
								pdflist.append(z1)
				pdflist = sorted(set(pdflist))
				session['pdflist'] = pdflist
				return redirect(url_for('showfiles'))
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('auditview.html')

@RentInvoice.route('/invdet', methods = ['POST', 'GET'])
def invdet():
	global Invoice_dbclient, Invoice_db, Invoice_dbCollection, seltenant, selinv, premise, totalrent, invoicekey
	global Invoice_Receipt, Rent_Ledger
	if request.method == 'POST':
		rentpaid = request.form.get('rentpaid')
		if not is_number(rentpaid):
			rentpaid=0
		datereceipt = request.form.get('datereceipt')
		remarks =  request.form.get('remarks')
		tds =  request.form.get('tds')
		otherded =  request.form.get('otherded')
		if request.form['submit_button'] == 'Submit':
			now = datetime.now()
			RentReceiptDict = { 
				"TimeStamp": now, 
				"InvoiceTenantGSTKey" : invoicekey,
				"Invoice No" : selinv,
				"Tenant Name" : seltenant,
				"Premise Address" : premise,
				"RentDue" : totalrent,
				"RentReceived" : float(rentpaid),
				"ReceivedDate" : datereceipt,
				"TDS" : float(tds),
				"OtherDeductions" : float(otherded),
				"Remarks" : remarks,
				"UpdatedBy" : session['username']
			}
			newdoc  = Invoice_Receipt.insert_one(RentReceiptDict)
			#update the other table too
			newdisp = float(totalrent) - float(rentpaid)
			rectquery = { "InvoiceTenantGSTKey" : invoicekey }
			newvalues = { "$set": 
									{ 
									"Received" : float(rentpaid),
									"Dispute in Credit" : newdisp,
									"Received Month" : datereceipt,
									"Receipt Narration" : remarks,
									"TDS" : float(tds),
									"UpdatedBy" : session['username']
									}
						}
			Invoice_dbCollection.update_one(rectquery, newvalues)
			#Insert Debit Rents Receivable Credit the Tenant
			#Debit Rents Receivable by adding rentpaid + tds + otherdedutions
			debitrent = float(rentpaid) + float(tds) + float(otherded)
			#important part
			rentledgerdict = {
				"TransTimeStamp" : datereceipt,
				"Narration1" : invoicekey,
				"Narration2" : remarks,
				"Amount" : float(debitrent),
				"DebitAccountHead" : "RENTS RECEIVABLE",
				"CreditAccountHead" : seltenant,
				"UpdatedBy" : session['username']
			}
			Rent_Ledger.insert_one(rentledgerdict)
			#TDS
			rentledgerdict = {
				"TransTimeStamp" : datereceipt,
				"Narration1" : invoicekey,
				"Narration2" : remarks,
				"Amount" : float(tds),
				"DebitAccountHead" : "TDS Deduction by Tenant",
				"CreditAccountHead" : "TDS Paid",
				"UpdatedBy" : session['username']
			}
			Rent_Ledger.insert_one(rentledgerdict)
			#Other Deductions
			rentledgerdict = {
				"TransTimeStamp" : datereceipt,
				"Narration1" : invoicekey,
				"Narration2" : remarks,
				"Amount" : float(otherded),
				"DebitAccountHead" : "Other Deductions by Tenant",
				"CreditAccountHead" : "Other Deductions Paid",
				"UpdatedBy" : session['username']
			}
			return redirect(url_for('InvoiceMenu'))
		elif request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
		else:
			return render_template('invdet.html')
	return render_template('invdet.html')

@RentInvoice.route('/popinv', methods = ['POST', 'GET'])
def popinv():
	global Invoice_dbclient, Invoice_db, Invoice_dbCollection, seltenant, selinv, premise, totalrent, invoicekey
	#render_template('popinv.html')
	session['disptenant'] = seltenant
	allinv = list(Invoice_dbCollection.find({"Tenant Name" : seltenant}))
	invoicelist =['On Demand Rent Receipt']
	for rec in allinv:
		invoicelist.append(rec.get("Invoice No"))
	session['invoicelist'] = invoicelist
	if request.method == 'POST':
		selinv =  request.form['invoice']
		session['invoice'] = selinv
		findinv = list(Invoice_dbCollection.find({"Invoice No" : selinv}))
		for rec1 in findinv:
			premise = rec1.get("Premise Address")
			totalrent = rec1.get("Total Rent")
			invoicekey = rec1.get("InvoiceTenantGSTKey")
			session['premise'] = premise
			session['totalrent'] = totalrent
			return redirect(url_for('invdet'))
	return render_template('popinv.html')

@RentInvoice.route('/rentreceipt', methods = ['POST', 'GET'])
def rentreceipt():
	global Invoice_dbclient, Invoice_db, Invoice_dbCollection, seltenant
	#dbopen()
	alldoc  = list(Invoice_dbCollection.find({}))
	tenantlist = []
	for doc in alldoc:
		tenantlist.append(doc.get("Tenant Name"))
	tenantlist = sorted(set(tenantlist))
	session['tenantlist'] = tenantlist
	if request.method == 'POST':
		if request.form['submit_button'] == 'Populate Invoices':
			seltenant =  request.form['tenant']
			return redirect(url_for('popinv'))
		elif request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('rentreceipt.html')


@RentInvoice.route('/cancelinv', methods = ['POST', 'GET'])
def cancelinv():
	global cancelflag, reprint, proper_changeinvdate, inproperty, newinvno, proper_newinvdate
	global state, owner, bank1, bank2, bank3, bank4, bank5, bank6, bank7
	global inrbt, incgst, ingst, insgst, intotalgst, intotalrent, changeremarks, wsdgshare, netamt, remarks
	global cancelkey, inigst

	allinv  = list(Invoice_dbCollection.find({}))
	keylist=[]
	for rec in allinv:
		if "Cancel" not in rec.get("InvoiceTenantGSTKey"):
			keylist.append(rec.get("InvoiceTenantGSTKey"))
	session['invkey'] = keylist	
	if request.method == 'POST':
		if request.form['submit_button'] == 'Get Invoice Details':
			selkey = request.form['invkey'] 
			cancelkey = selkey
			keylist = []
			keylist.append(selkey)
			session['invkey'] = keylist
			invrec = list(Invoice_dbCollection.find({"InvoiceTenantGSTKey" : selkey}))
			for rec in invrec:
				inproperty = str(rec.get("Property No"))
				session['newinvno'] = rec.get("Invoice No")
				newinvno = rec.get("Invoice No")
				session['oldinvdate'] = rec.get("Invoice Date")
				wsinvdate = str(rec.get("Invoice Date"))
				yyyy = wsinvdate[0:4]
				mm = wsinvdate[5]+wsinvdate[6]
				dd = wsinvdate[8]+wsinvdate[9]
				proper_newinvdate = dd+"."+mm+"."+yyyy
				session['proper_newinvdate'] = proper_newinvdate
				print(proper_newinvdate)
				session['owner'] = rec.get("OWNER OF THE PREMISE")
				session['premise'] = rec.get("Premise Address")
				session['ownergst'] = rec.get("OWNER GST NO")
				session['tenantgst'] = rec.get("Tenant GST No")
				session['ownergstadd'] = rec.get("OWNER GST ADDRESS")
				session['state'] = rec.get("State")
				session['tenantname'] = rec.get("Tenant Name")
				wsphone = rec.get("Tenant Contact No")
				if '.' in wsphone:
					phone, useless = wsphone.split('.')
				else:
					phone = wsphone
				session['tenantphone'] = phone
				session['tenantemail'] = rec.get("Tenant Email ID")
				session['rbt'] = rec.get("RBT")
				session['sgst'] = rec.get("SGST")
				session['cgst'] = rec.get("CGST")
				session['totalrent'] = rec.get("Total Rent")
				session['totalgst'] = rec.get("GST Part")
				session['dgshare'] = rec.get("DGShare")
				if not isinstance(rec.get("RBT"),str):
					session['rbt'] = myround(rec.get("RBT"))
					#session['rbt'] = "{:.2f}".format(rec.get("RBT"))
				if not isinstance(rec.get("SGST"),str):
					#session['sgst'] = myround(rec.get("SGST"))
					session['sgst'] = "{:.2f}".format(rec.get("SGST"))
				if not isinstance(rec.get("CGST"),str):
					#session['cgst'] = myround(rec.get("CGST"))
					session['cgst'] = "{:.2f}".format(rec.get("CGST"))
				if not isinstance(rec.get("Total Rent"),str):
					session['totalrent'] = myround(rec.get("Total Rent"))
					#session['totalrent'] = "{:.2f}".format(rec.get("Total Rent"))
				if not isinstance(rec.get("totalgst"),str):
					#session['totalgst'] = myround(rec.get("GST Part"))
					session['totalgst'] = "{:.2f}".format(rec.get("GST Part"))
				if not isinstance(rec.get("dgshare"),str):
					session['dgshare'] = myround(rec.get("DGShare"))
					#session['dgshare'] = "{:.2f}".format(rec.get("DGShare"))
				session['remarks'] = rec.get("Remarks")
				bank1 = rec.get("OWNER BANK ACCOUNT L1")
				bank2 = rec.get("OWNER BANK ACCOUNT L2")
				bank3 = rec.get("OWNER BANK ACCOUNT L3")
				bank4 = rec.get("OWNER BANK ACCOUNT L4")
				bank5 = rec.get("OWNER BANK ACCOUNT L5")
				bank6 = rec.get("OWNER BANK ACCOUNT L6")
				bank7 = rec.get("OWNER BANK ACCOUNT L7")
				session['bank'] = bank1 +" " +\
						bank2 + " " +\
						bank3 + " " +\
						bank4 + " " +\
						bank5 + " " + \
						bank6 + " " + \
						bank7
				state =  session['state']
				owner = session['owner']
				inrbt = session['rbt']
				insgst = session['sgst']
				incgst = session['cgst']
				intotalrent = session['totalrent']
				intotalgst = session['totalgst']
				wsdgshare = session['dgshare']
				netamt = float(intotalrent) + float(wsdgshare)
		if request.form['submit_button'] == "Cancel this Invoice":
			cancelflag  = True
			#changeinvdate = request.form['changeinvdate']
			#yyyy = changeinvdate[0:4]
			#mm = changeinvdate[5]+changeinvdate[6]
			#dd = changeinvdate[8]+changeinvdate[9]
			#proper_changeinvdate = dd+"."+mm+"."+yyyy
			#changetenantemail = request.form['tenantemail']
			#session['tenantemail'] = changetenantemail 
			remarks = request.form['remarks']
			session['wsremarks'] = remarks
			pdfcreate()
			cancelflag = False
			return redirect(url_for('showpdf'))
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('cancelinv.html')

@RentInvoice.route('/downloadpdf', methods = ['POST', 'GET'])
def downloadpdf():
	if request.method == 'POST':
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('downloadpdf.html')

@RentInvoice.route('/editinv', methods = ['POST', 'GET'])
def editinv():
	global editinvflag, reprint, proper_changeinvdate, inproperty, newinvno
	global state, owner, bank1, bank2, bank3, bank4, bank5, bank6, bank7
	global inrbt, incgst, ingst, insgst, intotalgst, intotalrent, changeremarks, wsdgshare, netamt, inigst
	global prevtotalrent, selkey, tenantgst, tenantphone, changetenantemail, changeremarks, tdsneeded, tdspercent, tdsamt
	global igstflag, igststate, inigst
	
	#change this after 03 Oct
	tdsneeded = False
	allinv  = list(Invoice_dbCollection.find({}))
	keylist=[]
	for rec in allinv:
		if "Cancel" not in rec.get("InvoiceTenantGSTKey"):
			keylist.append(rec.get("InvoiceTenantGSTKey"))
	session['invkey'] = keylist	
	if request.method == 'POST':
		if request.form['submit_button'] == 'Get Invoice Details':
			selkey = request.form['invkey'] 
			keylist = []
			keylist.append(selkey)
			session['invkey'] = keylist
			invrec = list(Invoice_dbCollection.find({"InvoiceTenantGSTKey" : selkey}))
			for rec in invrec:
				inproperty = str(rec.get("Property No"))
				session['newinvno'] = rec.get("Invoice No")
				newinvno = rec.get("Invoice No")
				session['oldinvdate'] = rec.get("Invoice Date")
				session['owner'] = rec.get("OWNER OF THE PREMISE")
				session['premise'] = rec.get("Premise Address")
				session['ownergst'] = rec.get("OWNER GST NO")
				session['tenantgst'] = rec.get("Tenant GST No")
				session['ownergstadd'] = rec.get("OWNER GST ADDRESS")
				session['state'] = rec.get("State")
				session['tenantname'] = rec.get("Tenant Name")
				wsphone = rec.get("Tenant Contact No")
				if '.' in wsphone:
					phone, useless = wsphone.split('.')
				else:
					phone = wsphone
				session['tenantphone'] = phone
				session['tenantemail'] = rec.get("Tenant Email ID")
				session['rbt'] = rec.get("RBT")
				session['sgst'] = rec.get("SGST")
				session['cgst'] = rec.get("CGST")
				session['totalrent'] = rec.get("Total Rent")
				prevtotalrent = rec.get("Total Rent")
				session['totalgst'] = rec.get("GST Part")
				session['dgshare'] = rec.get("DGShare")
				if rec.get("IGSTFLAG"):
					session['igststate'] = rec.get("IGSTState")
					igststate = rec.get("IGSTState")
					session['igst'] = rec.get("IGST")
					igstflag = True
					inigst = rec.get("IGST")
				else:
					session['igststate'] = "NOT IGST"
					igststate = ""
					session['igst'] = 0.00
					igstflag = False
					inigst= 0.00
				session['igstflag'] = igstflag
				if not isinstance(rec.get("RBT"),str):
					session['rbt'] = myround(rec.get("RBT"))
					#session['rbt'] = "{:.2f}".format(rec.get("RBT"))
				if not isinstance(rec.get("SGST"),str):
					#session['sgst'] = myround(rec.get("SGST"))
					session['sgst'] = "{:.2f}".format(rec.get("SGST"))
				if not isinstance(rec.get("CGST"),str):
					#session['cgst'] = myround(rec.get("CGST"))
					session['cgst'] = "{:.2f}".format(rec.get("CGST"))
				if not isinstance(rec.get("Total Rent"),str):
					session['totalrent'] = myround(rec.get("Total Rent"))
					#session['totalrent'] = "{:.2f}".format(rec.get("Total Rent"))
				if not isinstance(rec.get("totalgst"),str):
					#session['totalgst'] = myround(rec.get("GST Part"))
					session['totalgst'] = "{:.2f}".format(rec.get("GST Part"))
				if not isinstance(rec.get("dgshare"),str):
					session['dgshare'] = myround(rec.get("DGShare"))
					#session['dgshare'] = "{:.2f}".format(rec.get("DGShare"))
				session['tdspercent'] = rec.get("TDSPER")
				session['tdsamt'] = rec.get("TDS")
				session['rentaftertds'] = rec.get("RAT")
				session['remarks'] = rec.get("Remarks")
				bank1 = rec.get("OWNER BANK ACCOUNT L1")
				bank2 = rec.get("OWNER BANK ACCOUNT L2")
				bank3 = rec.get("OWNER BANK ACCOUNT L3")
				bank4 = rec.get("OWNER BANK ACCOUNT L4")
				bank5 = rec.get("OWNER BANK ACCOUNT L5")
				bank6 = rec.get("OWNER BANK ACCOUNT L6")
				bank7 = rec.get("OWNER BANK ACCOUNT L7")
				session['bank'] = bank1 +" " +\
						bank2 + " " +\
						bank3 + " " +\
						bank4 + " " +\
						bank5 + " " + \
						bank6 + " " + \
						bank7
				state =  session['state']
				owner = session['owner']
				inrbt = session['rbt']
				insgst = session['sgst']
				incgst = session['cgst']
				intotalrent = session['totalrent']
				intotalgst = session['totalgst']
				wsdgshare = session['dgshare']
				netamt = float(intotalrent) + float(wsdgshare)
		if request.form['submit_button'] == "Reprint & Mail Edited Invoice":
			reprint = True
			editinvflag = True
			changeinvdate = request.form['changeinvdate']
			yyyy = changeinvdate[0:4]
			mm = changeinvdate[5]+changeinvdate[6]
			dd = changeinvdate[8]+changeinvdate[9]
			proper_changeinvdate = dd+"."+mm+"."+yyyy
			tenantgst = request.form['tenantgst']
			session['tenantgst'] = tenantgst
			session['tenantname'] = request.form['tenantname']
			#igst change
			print("igstflag;",igstflag)
			if not igstflag:
				inigst = 0.00
				gstflag = request.form['gstflag']
				if gstflag == 'gsty':
					inrbt = request.form['rbt']
					insgst = request.form['sgst']
					incgst = request.form['cgst']
					intotalrent = request.form['totalrent']
					intotalgst = request.form['totalgst']
				else: #no gst
					inrbt = request.form['rbt']
					insgst = 0.00
					incgst = 0.00
					intotalrent = request.form['totalrent']
					intotalgst = 0.00
			else: #it is an igst invoice
					igstflag = True
					igststate = request.form['igststate']
					inrbt = request.form['rbt']
					inigst = request.form['igst']
					insgst = 0.00
					incgst = 0.00
					intotalrent = request.form['totalrent']
					intotalgst = request.form['totalgst']
			'''
			#commented due to igst change 28 12 2022
			gstflag = request.form['gstflag']
			if gstflag == 'gsty':
				inrbt = request.form['rbt']
				insgst = request.form['sgst']
				incgst = request.form['cgst']
				intotalrent = request.form['totalrent']
				intotalgst = request.form['totalgst']
			elif gstflag == 'gstn':
				inrbt = request.form['rbt']
				insgst = 0.00
				incgst = 0.00
				intotalrent = request.form['totalrent']
				intotalgst = 0.00
			else:
				inrbt = request.form['rbt']
				insgst = request.form['sgst']
				incgst = request.form['cgst']
				intotalrent = request.form['totalrent']
				intotalgst = request.form['totalgst']
			#end of igst commenting
			'''
			tdscheckbox = request.form.getlist('tdsinvyes') 
			if len(tdscheckbox) !=0:
				tdsneeded = True
				tdspercent = request.form['tdspercent']
				tdsamt = request.form['tdsamt']
				rentaftertds = request.form['rentaftertds']
				#hey intotalrent becomes rentaftertds here
				intotalrent = request.form['rentaftertds']
			else:
				tdsneeded = False
				tdspercent = "0"
				tdsamt = "0"
				rentaftertds = "0"
			tdspercent = request.form['tdspercent']
			tdsamt = request.form['tdsamt']
			if int(tdspercent) > 0 :
				tdsneeded = True
			else:
				tdsneeded = False
			tenantemail = request.form['tenantemail']
			wsdgshare = request.form['dgshare']
			if float(wsdgshare) > 0:
				netamt = float(intotalrent) + float(wsdgshare)
			else:
				netamt = float(intotalrent)
			session['tenantemail'] = tenantemail
			session['renterr'] = False
			if float(intotalrent) < 1:
				session['renterr'] = True
			else:
				session['renterr'] = False
			
			remarks = request.form['remarks']
			session['wsremarks'] = remarks
			print(remarks)
			tenantphone = request.form['tenantphone']
			#Aug 10'2022
			session['tenantname'] = request.form['tenantname']
		
			changetenantemail = request.form['tenantemail']
			session['tenantemail'] = changetenantemail 
			changeremarks = request.form['remarks']
			pdfcreate()
			return redirect(url_for('showpdf'))
		if request.form['submit_button'] == 'Exit':
			for key in list(session.keys()):
				if key != 'username' \
				and key != 'User_type' \
				and key != 'justmailed' \
				and key != 'dummyinvoice' :
					session.pop(key)
			return redirect(url_for('InvoiceMenu'))
	return render_template('editinv.html')

@RentInvoice.route('/reprintinv', methods = ['POST', 'GET'])
def reprintinv():
	global reprint, proper_changeinvdate, inproperty, newinvno, editinvflag
	global state, owner, bank1, bank2, bank3, bank4, bank5, bank6, bank7
	global inrbt, incgst, ingst, insgst, intotalgst, intotalrent, changeremarks, wsdgshare, netamt, inigst
	global tdsneeded, tdspercent, tdsamt
	global igstflag, igststate
	editinvflag = False
	tdsneeded = False
	tdspercent = "0"
	tdsamt = "0"
	allinv  = list(Invoice_dbCollection.find({}))
	keylist=[]
	for rec in allinv:
		if "Cancel" not in rec.get("InvoiceTenantGSTKey"):
			keylist.append(rec.get("InvoiceTenantGSTKey"))
	session['invkey'] = keylist	
	if request.method == 'POST':
		if request.form['submit_button'] == 'Get Invoice Details':
			selkey = request.form['invkey'] 
			keylist = []
			keylist.append(selkey)
			session['invkey'] = keylist
			invrec = list(Invoice_dbCollection.find({"InvoiceTenantGSTKey" : selkey}))
			for rec in invrec:
				inproperty = str(rec.get("Property No"))
				session['newinvno'] = rec.get("Invoice No")
				newinvno = rec.get("Invoice No")
				oldinvdate = str(rec.get("Invoice Date"))
				if "-" in oldinvdate:
					yyyy = oldinvdate[0:4]
					dd = oldinvdate[5]+oldinvdate[6]
					mm = oldinvdate[8]+oldinvdate[9]
					proper_changeinvdate = dd+"."+mm+"."+yyyy
				else:
					proper_changeinvdate = oldinvdate
				session['oldinvdate'] = proper_changeinvdate
				session['owner'] = rec.get("OWNER OF THE PREMISE")
				session['premise'] = rec.get("Premise Address")
				session['ownergst'] = rec.get("OWNER GST NO")
				session['tenantgst'] = rec.get("Tenant GST No")
				session['ownergstadd'] = rec.get("OWNER GST ADDRESS")
				session['state'] = rec.get("State")
				session['tenantname'] = rec.get("Tenant Name")
				wsphone = rec.get("Tenant Contact No")
				if '.' in wsphone:
					phone, useless = wsphone.split('.')
				else:
					phone = wsphone
				session['tenantphone'] = phone
				session['tenantemail'] = rec.get("Tenant Email ID")
				session['rbt'] = rec.get("RBT")
				session['sgst'] = rec.get("SGST")
				session['cgst'] = rec.get("CGST")
				session['totalrent'] = rec.get("Total Rent")
				session['totalgst'] = rec.get("GST Part")
				session['dgshare'] = rec.get("DGShare")
				#igst change
				if rec.get("IGSTFLAG"):
					session['igststate'] = rec.get("IGSTState")
					igststate = rec.get("IGSTState")
					session['igst'] = rec.get("IGST")
					inigst = rec.get("IGST")
					igstflag = True
				else:
					session['igststate'] = "NOT IGST"
					igststate = ""
					session['igst'] = 0.00
					inigst = 0.00
					igstflag = False
				session['igstflag'] = igstflag
				if not isinstance(rec.get("RBT"),str):
					session['rbt'] = myround(rec.get("RBT"))
					#session['rbt'] = "{:.2f}".format(rec.get("RBT"))
				if not isinstance(rec.get("SGST"),str):
					#session['sgst'] = myround(rec.get("SGST"))
					session['sgst'] = "{:.2f}".format(rec.get("SGST"))
				if not isinstance(rec.get("CGST"),str):
					#session['cgst'] = myround(rec.get("CGST"))
					session['cgst'] = "{:.2f}".format(rec.get("CGST"))
				if not isinstance(rec.get("Total Rent"),str):
					session['totalrent'] = myround(rec.get("Total Rent"))
					#session['totalrent'] = "{:.2f}".format(rec.get("Total Rent"))
				if not isinstance(rec.get("totalgst"),str):
					#session['totalgst'] = myround(rec.get("GST Part"))
					session['totalgst'] = "{:.2f}".format(rec.get("GST Part"))
				if not isinstance(rec.get("dgshare"),str):
					session['dgshare'] = myround(rec.get("DGShare"))
					#session['dgshare'] = "{:.2f}".format(rec.get("DGShare"))
				session['remarks'] = rec.get("Remarks")
				changeremarks = rec.get("Remarks")
				bank1 = rec.get("OWNER BANK ACCOUNT L1")
				bank2 = rec.get("OWNER BANK ACCOUNT L2")
				bank3 = rec.get("OWNER BANK ACCOUNT L3")
				bank4 = rec.get("OWNER BANK ACCOUNT L4")
				bank5 = rec.get("OWNER BANK ACCOUNT L5")
				bank6 = rec.get("OWNER BANK ACCOUNT L6")
				bank7 = rec.get("OWNER BANK ACCOUNT L7")
				session['bank'] = bank1 +" " +\
						bank2 + " " +\
						bank3 + " " +\
						bank4 + " " +\
						bank5 + " " + \
						bank6 + " " + \
						bank7
				state =  session['state']
				owner = session['owner']
				inrbt = session['rbt']
				insgst = session['sgst']
				incgst = session['cgst']
				intotalrent = session['totalrent']
				intotalgst = session['totalgst']
				wsdgshare = session['dgshare']
				netamt = float(intotalrent) + float(wsdgshare)
				session['tdspercent'] = str(rec.get("TDSPER"))
				session['tdsamt'] = str(rec.get("TDS"))
				session['rentaftertds'] = str(rec.get("RAT"))
				if int(tdspercent) > 0:
					tdsneeded = True
				else:
					tdsneeded = False
		if request.form['submit_button'] == "Reprint & Mail Invoice":
			reprint = True
			tdspercent = session.get('tdspercent')
			tdsamt = session.get('tdsamt')
			if int(tdspercent) > 0:
				tdsneeded = True
			else:
				tdsneeded = False
			pdfcreate()
			return redirect(url_for('showpdf'))
		if request.form['submit_button'] == 'Exit':
			for key in list(session.keys()):
				if key != 'username' \
				and key != 'User_type' \
				and key != 'justmailed' \
				and key != 'dummyinvoice' :
					session.pop(key)
			reprint = False
			return redirect(url_for('InvoiceMenu'))
	return render_template('reprintinv.html')


@RentInvoice.route('/ledgerview', methods = ['POST', 'GET'])
def ledgerview():
	global Invoice_dbclient, Invoice_db, Invoice_dbCollection, Invoice_Receipt, Rent_Ledger
	global Invoice_Users_Collection, Owners
	#
	session['ledgerarray'] = ""
	allentries = Rent_Ledger.find({})
	allentries = list(allentries)
	earliestentry = list(Rent_Ledger.find({}).sort([('TransTimeStamp', 1)]).limit(1))
	for entry in earliestentry:
			wstransdate = str(entry.get("TransTimeStamp"))
			session['dispdate'] = wstransdate[0:10]
	accheadlist=[]
	for rec in allentries:
		if rec.get("DebitAccountHead") != "RENTS RECEIVABLE":
			accheadlist.append(rec.get("DebitAccountHead"))
		if rec.get("CreditAccountHead") != "RENTS RECEIVABLE":
			accheadlist.append(rec.get("CreditAccountHead"))
	accheadlist = sorted(set(accheadlist))
	session['acclist'] = accheadlist			
	if request.method == 'POST':
		if request.form['submit_button'] == 'Show Ledger entries':
			ledgerchoice = request.form['ledgerchoice']
			if ledgerchoice == "allaccs":
				session['ledgerarray'] =""
				ledgerarray = []
				#fill the array
				for acchead in accheadlist:
					dbentries = Rent_Ledger.find({"DebitAccountHead" : acchead})
					dbentries = list(dbentries)
					for eachentry in dbentries:
						line = []
						line.append(eachentry.get("DebitAccountHead"))
						narr = eachentry.get("Narration")
						if narr == None:
							narr  = ""
						narr1 = eachentry.get("Narration1")
						if narr1 == None:
							narr1  = ""
						narr2 = eachentry.get("Narration2")
						if narr2 == None:
							narr2  = ""
						line.append(narr+"  "+narr1 +"  "+ narr2)
						transdate = str(eachentry.get("TransTimeStamp"))
						tyyyy = transdate[0:4]
						tmm = transdate[5]+transdate[6]
						tdd = transdate[8]+transdate[9]
						line.append(tdd+"-"+tmm+"-"+tyyyy)
						line.append("DB")
						line.append(myround(float(eachentry.get("Amount"))))
						line.append("CR")
						line.append("")
						if not(line[4] == 0 and line[6] == ""):
							ledgerarray.append(line)
					crentries = Rent_Ledger.find({"CreditAccountHead" : acchead})
					crentries = list(crentries)
					for eachentry in crentries:
						line = []
						line.append(eachentry.get("CreditAccountHead"))
						narr = eachentry.get("Narration")
						if narr == None:
							narr  = ""
						narr1 = eachentry.get("Narration1")
						if narr1 == None:
							narr1  = ""
						narr2 = eachentry.get("Narration2")
						if narr2 == None:
							narr2  = ""
						line.append(narr+"  "+narr1 +"  "+ narr2)
						transdate = str(eachentry.get("TransTimeStamp"))
						tyyyy = transdate[0:4]
						tmm = transdate[5]+transdate[6]
						tdd = transdate[8]+transdate[9]
						line.append(tdd+"-"+tmm+"-"+tyyyy)
						line.append("DB")
						line.append("")
						line.append("CR")
						line.append(myround(float(eachentry.get("Amount"))))
						if not(line[4] == "" and line[6] == 0):
							ledgerarray.append(line)
				#session['rows'] = rows
				ledgerarray.sort(key=lambda row: (row[0]))
				headrec = []
				headrec.append("Account Head")
				headrec.append("Narration")
				headrec.append("Trans Date")
				headrec.append("DB")
				headrec.append("DB Amount")
				headrec.append("CR")
				headrec.append("CR Amount")
				prevacc =""
				for r1 in ledgerarray:
					index = ledgerarray.index(r1)
					if r1[0] != prevacc:
						ledgerarray.insert(index, headrec)
						prevacc = r1[0]
				session['ledgerarray'] = ledgerarray
				return render_template('ledgerview.html')
			if ledgerchoice == "someaccs":
				session['ledgerarray'] =""
				ledgerarray = []
				accheadlist = request.form.getlist('selacc[]')
				daterange = request.form['fromtrandate']
				for acchead in accheadlist:
					dbentries = Rent_Ledger.find({'DebitAccountHead' : acchead})
					dbentries = list(dbentries)
					for eachentry in dbentries:
						transdate = str(eachentry.get("TransTimeStamp"))
						if transdate >= daterange:
							line = []
							line.append(eachentry.get("DebitAccountHead"))
							narr = eachentry.get("Narration")
							if narr == None:
								narr  = ""
							narr1 = eachentry.get("Narration1")
							if narr1 == None:
								narr1  = ""
							narr2 = eachentry.get("Narration2")
							if narr2 == None:
								narr2  = ""
							line.append(narr+"  "+narr1 +"  "+ narr2)
							#transdate = str(eachentry.get("TransTimeStamp"))
							tyyyy = transdate[0:4]
							tmm = transdate[5]+transdate[6]
							tdd = transdate[8]+transdate[9]
							line.append(tdd+"-"+tmm+"-"+tyyyy)
							line.append("DB")
							line.append(myround(float(eachentry.get("Amount"))))
							line.append("CR")
							line.append("")
							if not(line[4] == 0 and line[6] == ""):
								ledgerarray.append(line)
					crentries = Rent_Ledger.find({'CreditAccountHead' : acchead})
					crentries = list(crentries)
					for eachentry in crentries:
						transdate = str(eachentry.get("TransTimeStamp"))
						if transdate >= daterange:
							line = []
							line.append(eachentry.get("CreditAccountHead"))
							narr = eachentry.get("Narration")
							if narr == None:
								narr  = ""
							narr1 = eachentry.get("Narration1")
							if narr1 == None:
								narr1  = ""
							narr2 = eachentry.get("Narration2")
							if narr2 == None:
								narr2  = ""
							line.append(narr+"  "+narr1 +"  "+ narr2)
							#transdate = str(eachentry.get("TransTimeStamp"))
							tyyyy = transdate[0:4]
							tmm = transdate[5]+transdate[6]
							tdd = transdate[8]+transdate[9]
							line.append(tdd+"-"+tmm+"-"+tyyyy)
							line.append("DB")
							line.append("")
							line.append("CR")
							line.append(myround(float(eachentry.get("Amount"))))
							if not(line[4] == "" and line[6] == 0):
								ledgerarray.append(line)
				#session['rows'] = rows
				ledgerarray.sort(key=lambda row: (row[0]))
				headrec = []
				headrec.append("Account Head")
				headrec.append("Narration")
				headrec.append("Trans Date")
				headrec.append("DB")
				headrec.append("DB Amount")
				headrec.append("CR")
				headrec.append("CR Amount")
				prevacc =""
				for r1 in ledgerarray:
					index = ledgerarray.index(r1)
					if r1[0] != prevacc:
						ledgerarray.insert(index, headrec)
						prevacc = r1[0]
				session['ledgerarray'] = ledgerarray
				return render_template('ledgerview.html')
		if request.form['submit_button'] == 'Exit':
			for key in list(session.keys()):
				if key != 'username' \
				and key != 'User_type' \
				and key != 'justmailed' \
				and key != 'dummyinvoice' :
					session.pop(key)
			return redirect(url_for('InvoiceMenu'))
	return render_template('ledgerview.html')

	
	
@RentInvoice.route('/penal', methods = ['POST', 'GET'])
def penal():
	if request.method == 'POST':
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('penal.html')

@RentInvoice.route('/tenants', methods = ['POST', 'GET'])
def tenants():
	if request.method == 'POST':
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('tenants.html')

@RentInvoice.route('/owners', methods = ['POST', 'GET'])
def owners():
	if request.method == 'POST':
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('owners.html')

@RentInvoice.route('/property', methods = ['POST', 'GET'])
def property():
	global wsstate, wsowner, wspremise, wsownergstadd, wsownergstno, wsbank1, wsbank2, wsbank3, wsbank4, wsbank5, wsbank6, wsbank7
	global existpropertyno, newpropertyno
	global newtenant, newtenantgst, newtenantemail, newtenantphone
	session['dummyinvoice'] = ""
	session['toeditproperty'] = False
	session['selectedpropertynumber'] = 0
	session['premise'] = ""
	session['owner'] = ""
	session['ownerstate'] = ""
	allprop = list(Invoice_dbCollection.find({}))
	proplist =[]
	for rec in allprop:
		proplist.append(rec.get("Property No"))
	proplist = sorted(set(proplist))
	session['proplist'] = proplist
	newpropnumber = max(proplist) + 2 
	wsproperty = newpropnumber
	newpropertyno = newpropnumber
	session['newpropertynumber'] = newpropnumber
	allowners = list(Invoice_dbCollection.find({}))
	ownerlist = []
	for rec in allowners:
		ownerlist.append(rec.get("OWNER OF THE PREMISE")+"~"+rec.get("State"))
	ownerlist = sorted(set(ownerlist))
	session['ownerlist'] = ownerlist
	if request.method == 'POST':
		if request.form['submit_button'] == 'Get Property Details':
					session['toeditproperty'] = True
					selproperty = int(request.form['selproperty'])
					wsproperty = selproperty
					existpropertyno = selproperty
					session['selectedpropertynumber'] = selproperty
					lastproperty = list(Invoice_dbCollection.find({"Property No": selproperty}).sort([('TimeStamp', -1)]).limit(1))
					for proprec in lastproperty:
						session['premise'] = proprec.get("Premise Address")
						wspremise = session['premise']
						session['owner'] = proprec.get("OWNER OF THE PREMISE")
						session['ownerstate'] = proprec.get("State")
						wsowner = session['owner']
						wsstate = session['ownerstate']
						wsbank1 = proprec.get("OWNER BANK ACCOUNT L1")
						wsbank2 = proprec.get("OWNER BANK ACCOUNT L2")
						wsbank3 = proprec.get("OWNER BANK ACCOUNT L3")
						wsbank4 = proprec.get("OWNER BANK ACCOUNT L4")
						wsbank5 = proprec.get("OWNER BANK ACCOUNT L5")
						wsbank6 = proprec.get("OWNER BANK ACCOUNT L6")
						wsbank7 = proprec.get("OWNER BANK ACCOUNT L7")
						wsownergstadd = proprec.get("OWNER GST ADDRESS")
						wsownergstno = proprec.get("OWNER GST NO")
						#02-Feb-2023
						session['wstenant'] = proprec.get("Tenant Name")
						session['wstenantgst'] = proprec.get("Tenant GST No")
						session['wstenantemail'] = proprec.get("Tenant Email ID")
						session['wstenantphone'] = proprec.get("Tenant Contact No")
						session['wsrbt'] = proprec.get("RBT")
						#02-Feb-2023
		if request.form['submit_button'] == 'Add/Update Property':
			choice = request.form['neworedit']
			if choice == "newproperty":
				session['toeditproperty'] = False
				newpremise = request.form['newpremise']
				wspremise = newpremise
				newtenant = request.form['newtenant']
				newtenantgst = request.form['newtenantgst']
				newtenantemail = request.form['newtenantemail']
				newtenantphone = request.form['newtenantphone']
				selowner = request.form['selowner']
				newrbt = float(request.form['newrentbeforetax'])
				incgst = newrbt * 9/100
				insgst = newrbt * 9/100
				intotalgst = incgst + insgst
				intotalrent = newrbt + intotalgst
				ownerpart = selowner.split('~')[0]
				statepart = selowner.split('~')[1]
				wsowner = ownerpart
				wsstate = statepart
				lastowner = list(Invoice_dbCollection.find({"OWNER OF THE PREMISE" : ownerpart, "State": statepart}).sort([('TimeStamp', -1)]).limit(1))
				for lastowner_rec in lastowner:
					wsbank1 = lastowner_rec.get("OWNER BANK ACCOUNT L1")
					wsbank2 = lastowner_rec.get("OWNER BANK ACCOUNT L2")
					wsbank3 = lastowner_rec.get("OWNER BANK ACCOUNT L3")
					wsbank4 = lastowner_rec.get("OWNER BANK ACCOUNT L4")
					wsbank5 = lastowner_rec.get("OWNER BANK ACCOUNT L5")
					wsbank6 = lastowner_rec.get("OWNER BANK ACCOUNT L6")
					wsbank7 = lastowner_rec.get("OWNER BANK ACCOUNT L7")
					wsownergstadd = lastowner_rec.get("OWNER GST ADDRESS")
					wsownergstno = lastowner_rec.get("OWNER GST NO")
			elif choice == "editproperty":
				wspremise = request.form['edtnewpremise']
				session['toeditproperty'] = True
				newtenant = request.form['edtnewtenant']
				newtenantgst = request.form['edtnewtenantgst']
				newtenantemail = request.form['edtnewtenantemail']
				newtenantphone = request.form['edtnewtenantphone']
				selowner = request.form['selowner']
				newrbt = float(request.form['existnewrentbeforetax'])
				incgst = newrbt * 9/100
				insgst = newrbt * 9/100
				intotalgst = incgst + insgst
				intotalrent = newrbt + intotalgst
			#Make a dummy invoice
			now = datetime.now()
			owninv  = list(Owners.find({ "OwnerName" : wsowner }))
			if len(owninv) == 0:
				session['shortnameerr'] = True
				inv01="EE"
			else:
				session['shortnameerr'] = False
				for r in owninv:
					inv01 = r.get("ShortName")
			inv34 = statecode_lookup[wsstate.strip()]
			if choice == "editproperty":
				wsproperty = existpropertyno
			else:
				wsproperty = newpropertyno
			invtengstkey = str(wsproperty)+"~"+inv01+"/"+inv34+"-00-00-00-"+str(wsproperty)+"~"+newtenantgst
			duminvno = inv01+"/"+inv34+"-00-00-00-"+str(wsproperty)
			session['dummyinvoice'] = invtengstkey
			NewInvoiceDict = { 
						"TimeStamp": now, 
						"InvoiceTenantGSTKey" : invtengstkey,
						"Record Version" : "1",
						"Property No": wsproperty,
						"Invoice Date": now,
						"Invoice No": duminvno,
						"Tenant GST No": newtenantgst,
						"Premise Address": wspremise,
						"Tenant Email ID": newtenantemail,
						"Tenant Contact No": newtenantphone,
						"State": wsstate,
						"Rental Type": "Commercial",
						"OWNER OF THE PREMISE": wsowner,
						#continue 
						"OWNER GST ADDRESS": wsownergstadd,
						"OWNER GST NO": wsownergstno,
						"OWNER BANK ACCOUNT L1": wsbank1,
						"OWNER BANK ACCOUNT L2": wsbank2,
						"OWNER BANK ACCOUNT L3": wsbank3,
						"OWNER BANK ACCOUNT L4": wsbank4,
						"OWNER BANK ACCOUNT L5": wsbank5,
						"OWNER BANK ACCOUNT L6": wsbank6,
						"OWNER BANK ACCOUNT L7": wsbank7,
						"Tenant Name": newtenant,
						"RBT": newrbt,
						"SGST": insgst,
						"CGST": incgst,
						"Total Rent": intotalrent,
						"TDS": float(tdsamt),
						"TDSPER" : int(tdspercent),
						"RAT": intotalrent,
						"Remarks": "",
						"GST Part": intotalgst,
						"Commencement Date": "",
						"Expiry Date": "",
						"RENT": 0,
						"Received" : 0,
						"Dispute in Credit" : 0,
						"Received Month" :"",
						"Receipt Narration" : "",
						"Security Deposit":"",
						"DGShare" : 0,
						"NETAMT" : 0,
						"UpdatedBy" : session['username']
					}
			newdoc  = Invoice_dbCollection.insert_one(NewInvoiceDict)

			return redirect(url_for('InvoiceMenu'))
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('property.html')

@RentInvoice.route('/proplink', methods = ['POST', 'GET'])
def proplink():
	if request.method == 'POST':
		if request.form['submit_button'] == 'Exit':
			return redirect(url_for('InvoiceMenu'))
	return render_template('proplink.html')

@RentInvoice.route('/sounderr', methods = ['POST', 'GET'])
def sounderr():
	global todayDate, wsaccounthead, opdbbalamt, opcrbalamt, asondate
	global samesound
	global updateopflag
	if request.method == 'POST':
		if request.form['submit_button'] == 'Do Not Update Opening Balance':
			return redirect(url_for('openingbal'))
		if request.form['submit_button'] == 'Update Anyway':
			now = datetime.now()
			opbaldict = {
						"TimeStamp" : now,
						"EnteredOn"  : todayDate,
						"AccountHead" : wsaccounthead,
						"DebitAmount" : opdbbalamt,
						"CrediAmount" : opcrbalamt,
						"AsOnDate" : asondate,
						"UpdatedBy" : session['username']
			}
			newdoc  = opbalance.insert_one(opbaldict)
			return redirect(url_for('openingbal'))

	return render_template('sounderr.html', sounderr = samesound)

@RentInvoice.route('/openingbal', methods = ['POST', 'GET'])
def openingbal():
	global todayDate, wsaccounthead, opdbbalamt, opcrbalamt, asondate, accheadlist
	global opbalance
	global samesound
	todayDay = datetime.now().day
	todayMonth = datetime.now().month
	todayYear = datetime.now().year
	todayDate = str(todayYear) +"-"+ str(todayMonth) +"-"+str(todayDay)
	accheadlist = []
	allinv  = Invoice_dbCollection.find({})
	allinv = list(allinv)
	for doc in allinv:
		accheadlist.append(doc.get("Tenant Name"))
	allheads  = Rent_Ledger.find({})
	allheads = list(allheads)
	for doc in allheads:
		accheadlist.append(doc.get("DebitAccountHead"))
		accheadlist.append(doc.get("CreditAccountHead"))
	accheadlist = sorted(set(accheadlist))
	origlist = accheadlist
	session['accheadlist'] = accheadlist
	if request.method == 'POST':
		selected = False
		session['selected'] = selected
		#if request.form['submit_button'] == 'Select':
		#	selected = True
		#	session['selacchead'] = request.form['acchead']
		#	accheadlist = []
		#	accheadlist.append(session['selacchead'])
		#	session['accheadlist'] = accheadlist
		#	session['selected'] = selected
		if request.form['submit_button'] == 'Update Opening Balance':
			dbcrflag = request.form['dbcrflag']
			opdbbalamt = 0.0
			opcrbalamt = 0.0
			if dbcrflag == "debit":
				opdbbalamt = float(request.form['opdbbal'])
			if dbcrflag == "credit":
				opcrbalamt = float(request.form['opcrbal'])
			asondate = request.form['asondate']
			now = datetime.now()
			
			existornew = request.form['existornew']
			samesound = "0"
			if existornew == "newaccbut":
				wsaccounthead = request.form['newaccvalue']
				for eachhead in accheadlist:
					if soundex(eachhead) == soundex(wsaccounthead):
						samesound = "Warning: "+wsaccounthead+" sounds like, already existing: "+eachhead
						return redirect(url_for('sounderr'))
					else:
						samesound = "0"
			else:
				wsaccounthead = request.form['acchead']
			
			opbaldict = {
						"TimeStamp" : now,
						"EnteredOn"  : todayDate,
						"AccountHead" : wsaccounthead,
						"DebitAmount" : opdbbalamt,
						"CrediAmount" : opcrbalamt,
						"AsOnDate" : asondate,
						"UpdatedBy" : session['username']
			}
			newdoc  = opbalance.insert_one(opbaldict)
			session['accheadlist'] = accheadlist
			session['selected'] = False
		if request.form['submit_button'] == 'Exit':
			session['selected'] = False
			return redirect(url_for('InvoiceMenu'))
	return render_template('openingbal.html')

def insert_newlines(string, every):
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)

def insert_pipes(string, every):
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '|'.join(lines)

def work_invoice_pdfcreate():
	global selected_party, party_state, party_gst_no, party_gst_add, work_invoice_number, work_invoice_date
	global descline_array, work_desc, total_work_amount, work_sgst, work_cgst, work_gst, grand_total_work_amount
	work_invoicer_name = "KAPPSOFT SYSTEMS PVT LIMITED "
	work_invoicer_gstadd = "935 GKS Towers, 5th floor, Poonamallee High Road, Kilpauk, Chennai, Tamil Nadu 600084"
	work_invoicer_gstno = "33AAJCK1523C1Z4"
	work_invoicer_state = "TAMIL NADU"
	
	# Add a page
	pdf = FPDF('P', 'mm', 'A4')
	pdf.set_margins(left= 15, top= 10, right = -1)
	pdf.add_page()
	#inv number
	pdf.set_font("Arial", "B", 9)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	topx = xpos
	topy = ypos
	pdf.multi_cell(w=50, h = 8, txt ="Invoice No:", align = 'L')
	pdf.set_font("Arial", "", 9)
	pdf.set_xy(xpos+20,ypos)
	#work_invoice_number is for invoice number
	pdf.multi_cell(w=30, h = 8, txt =work_invoice_number)
	#invoice date
	pdf.set_xy(xpos+140,ypos)
	pdf.set_font("Arial", "B", 9)
	pdf.multi_cell(w=50, h = 8, txt ="Dated:", align = 'L')
	pdf.set_xy(xpos+120,ypos)
	pdf.set_font("Arial", "", 9)
	pdf.multi_cell(w=50, h = 8, txt = work_invoice_date, align = 'R')
	pdf.set_font("Arial", "", 5)
	#propdesc = "Property No."+inproperty
	pdf.set_xy(topx, topy+8)
	#pdf.multi_cell(w=30, h = 6, txt = propdesc, align = 'L')
	pdf.set_xy(topx, topy+20)
	pdf.set_font("Arial", "B", 10)
	pdf.multi_cell(w=160, h = 5, txt =work_invoicer_name, align = 'C')
	pdf.set_font("Arial", "", 8)
	pdf.multi_cell(w=160, h = 5, txt =work_invoicer_gstadd, align = 'C')
	pdf.multi_cell(w=160, h = 5, txt ="GSTIN/UIN:"+work_invoicer_gstno, align = 'C')
	#state and code
	pdf.multi_cell(w=160, h = 5, txt ="State:"+work_invoicer_state+" Code:"+statecode_lookup[work_invoicer_state.strip()], align = 'C')
	pdf.set_font("Arial", "B", 12)
	pdf.multi_cell(w=160, h = 5, txt ="")
	pdf.multi_cell(w=160, h = 5, txt ="Works Invoice", align = 'C')
	pdf.multi_cell(w=160, h = 5, txt ="")
	pdf.set_font("Arial", "", 8)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=50, h = 8, txt ="Party:", align = 'L')
	pdf.set_xy(xpos+10,ypos)
	pdf.set_font("Arial", "", 8)
	pdf.multi_cell(w=160, h = 5, txt =selected_party)
	pdf.set_font("Arial", "", 8)
	pdf.set_xy(xpos+10,ypos+5)
	pdf.multi_cell(w=100, h = 5, txt =party_gst_add, align = 'L')
	pdf.set_font("Arial", "", 7)
	pdf.multi_cell(w=50, h = 5, txt ="GSTIN/UIN:"+party_gst_no, align = 'L')

	#tabular
	pdf.set_font("Arial", "B", 6)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	#(90,15)
	pdf.multi_cell(w=100, h = 8, txt = "Particulars", border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+100, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=12, h = 8, txt = "HSN/SAC", border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+12, ypos)

	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = "Amount", border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = "SGST", border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = "CGST", border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=20, h = 8, txt = "Tot Amount", border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+20, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	#detail line
	const_hsn = "998313"
	pdf.set_font("Arial", "", 6)
	
	#detail_1
	pdf.set_xy(15, ypos+8)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=100, h = 8, txt = descline_array[0], border = "LTR", align = 'L', fill = False)
	pdf.set_xy(xpos+100, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=12, h = 8, txt = const_hsn, border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+12, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	work_totalformat = str("{}".format(currency_in_indian_format(total_work_amount)))
	pdf.multi_cell(w=15, h = 8, txt = str(work_totalformat), border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = str(work_sgst), border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = str(work_cgst), border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)

	work_totalformat = str("{}".format(currency_in_indian_format(grand_total_work_amount)))
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=20, h = 8, txt = work_totalformat, border = "LTBR", align = 'C', fill = False)
	pdf.set_xy(xpos+20, ypos)
	#etail_1_end

	#second line details if any
	skipno = 1
	if len(descline_array) > 1:
		skipno = len(descline_array)
		for i in range(1,len(descline_array)):
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			pdf.set_xy(15, ypos+8)
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			pdf.set_xy(xpos, ypos)
			print_desc = descline_array[i].replace("\n","")
			pdf.multi_cell(w=100, h = 8, txt = print_desc, border = "LR", align = 'L', fill = False)
			pdf.set_xy(xpos+100, ypos)
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			pdf.multi_cell(w=12, h = 8, txt = "", border = "L", align = 'C', fill = False)
			pdf.set_xy(xpos+12, ypos)
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			
			pdf.multi_cell(w=15, h = 8, txt ="", border = "", align = 'C', fill = False)
			pdf.set_xy(xpos+15, ypos)
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			pdf.multi_cell(w=15, h = 8, txt = "", border = "", align = 'C', fill = False)
			pdf.set_xy(xpos+15, ypos)
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			pdf.multi_cell(w=15, h = 8, txt = "", border = "", align = 'C', fill = False)
			pdf.set_xy(xpos+15, ypos)
			ypos = pdf.get_y()
			xpos = pdf.get_x()
			pdf.multi_cell(w=20, h = 8, txt = "", border = "R", align = 'C', fill = False)
			pdf.set_xy(xpos+20, ypos)
			#pdf.set_xy(15, ypos+8)
		#endfor
	pdf.set_xy(15, ypos+8)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	
	pdf.multi_cell(w=100, h = 8, txt = "", border = "LRB", align = 'C', fill = False)
	pdf.set_xy(xpos+100, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=12, h = 8, txt = "", border = "LB", align = 'C', fill = False)
	pdf.set_xy(xpos+12, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	
	pdf.multi_cell(w=15, h = 8, txt ="", border = "B", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = "", border = "B", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=15, h = 8, txt = "", border = "B", align = 'C', fill = False)
	pdf.set_xy(xpos+15, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=20, h = 8, txt = "", border = "RB", align = 'C', fill = False)
	pdf.set_xy(xpos+20, ypos)
	#endif array len > 1

	strip_work_newtotal = work_totalformat.replace(',','')
	work_totalwords = word(strip_work_newtotal)
	pdf.set_font("Arial", "", 7)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.set_xy(15, ypos+8)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=50, h = 5, txt = "Amount Chargeable (in words)",  align = 'L', fill = False)
	pdf.set_xy(xpos+40,ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.set_font("Arial", "B", 7)
	pdf.multi_cell(w=100, h = 8, txt = "INR "+work_totalwords+" only",  align = 'L', fill = False)
	pdf.set_xy(xpos+90,ypos)
	pdf.set_font("Arial", "", 7)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=50, h = 5, txt = "E. & O.E",  align = 'R', fill = False)
	pdf.set_font("Arial", "B", 7)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.set_font("Arial", "", 7)
	work_gst_format = str("{}".format(currency_in_indian_format(float(work_gst))))
	pdf.multi_cell(w=160, h = 8, txt = "Tax Amount: "+work_gst_format+"  Tax Amount (in words) :", border = "", align = 'L', fill = False)
	pdf.set_xy(xpos+60, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.set_font("Arial", "", 7)
	
	strip_work_gst = work_gst_format.replace(',','')
	work_gstwords = word(strip_work_gst)
	pdf.multi_cell(w=140, h = 8, txt = "INR "+ work_gstwords +" only", border = "", fill = False)
	pdf.set_font("Arial", "I", 8)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=30, h = 5, txt = "", border = "", align = "L", fill = False)
	pdf.set_xy(xpos+90, ypos)
	pdf.set_font("Arial", "", 7)
	pdf.multi_cell(w=50, h = 5, txt = "Company's Bank Details:", border = "", fill = False)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=80, h = 5, txt = "", border = "", fill = False)
	pdf.set_xy(xpos+90, ypos)
	pdf.set_font("Arial", "", 6)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=80, h = 5, txt = "Account Name: Kappsoft Systems Pvt. Ltd.", border = "", fill = False)
	pdf.set_xy(xpos, ypos+3)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=80, h = 5, txt = "Account Number: 14570200012868", border = "", fill = False)
	pdf.set_xy(xpos, ypos+3)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=80, h = 5, txt = "IFSC code: FDRL0001457", border = "", fill = False)
	pdf.set_xy(xpos, ypos+3)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=80, h = 5, txt = "Branch: Purasawalkam", border = "", fill = False)
	pdf.set_xy(xpos, ypos+3)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	work_bank6 = ""
	work_bank7 = ""
	pdf.multi_cell(w=80, h = 5, txt = "", border = "", fill = False)
	pdf.set_xy(xpos, ypos+3)
	if work_bank6 != "nil" :
		ypos = pdf.get_y()
		xpos = pdf.get_x()
		pdf.multi_cell(w=80, h = 5, txt = "", border = "", fill = False)
		pdf.set_xy(xpos, ypos+3)
	if work_bank7 != "nil":
		ypos = pdf.get_y()
		xpos = pdf.get_x()
		pdf.multi_cell(w=80, h = 5, txt = "", border = "", fill = False)
	pdf.set_font("Arial", "", 7)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	pdf.multi_cell(w=80, h = 5, txt = "", border = "", align = "L",fill = False)
	pdf.set_font("Arial", "B", 8)
	pdf.set_xy(xpos, ypos)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	namelen = len(work_invoicer_name)
	pos = 160 - namelen
	pdf.set_xy(pos, ypos)
	#too long invoicer names to fit in
	print_invoicer = work_invoicer_name
	if len(print_invoicer) > 48:
		invoicerpart1 = print_invoicer[:48]+"-"
		invoicerpart2 = print_invoicer[48:]
		pdf.multi_cell(w=160,  h = 5, txt = invoicerpart1, border = "",fill = False)
		ypos = ypos + 5
		pdf.set_xy(pos, ypos)
		pdf.multi_cell(w=160,  h = 5, txt = invoicerpart2, border = "",fill = False)
	else:
		pdf.multi_cell(w=160,  h = 5, txt = print_invoicer, border = "",fill = False)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	#CR#2 Begin
	#dummy lines 1
	pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
	#pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
	#pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
	#pdf.multi_cell(w=100, h = 8, txt = "", border = "", align = "R",fill = False)
	ypos = pdf.get_y()
	xpos = pdf.get_x()
	#CR#2 End
	pdf.set_xy(xpos, ypos)
	pdf.multi_cell(w=160, h = 5, txt = "Authorised Signatory", border = "", align = "R",fill = False)
	pdf.set_font("", "U", 7)
	pdf.multi_cell(w=180, h = 5, txt = "This is a computer generated invoice and does not require signature", border = "", align = "C",fill = False)
	work_invoice_forpdfname = work_invoice_number.replace("/", "_")
	work_invoice_forpdfname = work_invoice_forpdfname+"-"+party_gst_no
	work_invoice_forpdfname = work_invoice_forpdfname.replace(" ","_")
	newworkpdfname = "Invoice_"+ work_invoice_forpdfname+".pdf"
	pathworkpdfname = mydrive + staticpath + newworkpdfname
	pdf.output(pathworkpdfname)
	work_invoice_cancelflag = False
	if work_invoice_cancelflag:
		#merge with the watermark
		mergecommand = "pdftk "+ pathworkpdfname + \
		" background " + mydrive + staticpath + "canwatermark.pdf output " + \
		mydrive + staticpath + "Cancel_"+ work_invoice_forpdfname +".pdf"
		os.system(mergecommand)
		session['work_pdf_file'] = "Cancel_"+ work_invoice_forpdfname +".pdf"
		work_invoice_cancelflag = False
	else:
		session['work_pdf_file'] = newworkpdfname
	work_invoice_cancelflag = False

#deepika write the code from here onwards

def work_dbopen():
	global Invoice_dbclient, work_invoice_db, work_invoice_party, work_last_inv_no, work_invoice_collection, winv_Users_Collection
	Invoice_dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
	work_invoice_db = Invoice_dbclient["WorkInvoice"]
	work_invoice_party = work_invoice_db["WorkInvoiceParty"]
	work_last_inv_no = work_invoice_db["LastInvoiceNumber"]
	work_invoice_collection = work_invoice_db["WorkInvoiceCollection"]
	winv_Users_Collection = work_invoice_db["WorkInvoiceUsers"]


@RentInvoice.route('/work_invoice_generate' , methods = ['POST', 'GET'])
def work_invoice_generate():
	work_dbopen()
	global Invoice_dbclient, work_invoice_db, work_invoice_party, work_last_inv_no, work_invoice_collection, winv_Users_Collection
	global selected_party, party_state, party_gst_no, party_gst_add
	global descline_array, work_desc, total_work_amount
	global work_sgst, work_cgst, work_gst, grand_total_work_amount
	global work_invoice_number, work_invoice_date
	
	allparty = list(work_invoice_party.find({}))
	partylist =[]
	for rec in allparty:
		partylist.append(rec.get("party_name")+"|"+rec.get("party_state")+"|"+rec.get("party_gst_no"))
	partylist = sorted(set(partylist))
	session['partylist'] = partylist
	resources = work_invoice_db["ResourceMaster"]
	allemp = list(resources.find({}))
	employeelist =[]
	empname=[]
	emprate=[]
	empname.append('Employee')
	emprate.append('0')
	for rec in allemp:
		employeelist.append(rec.get("Employee_Name")+"|"+str(rec.get("Rate_per_hour")))
		empname.append(rec.get("Employee_Name"))
		emprate.append(rec.get("Rate_per_hour"))
	employeelist = sorted(set(employeelist))
	session['employeelist'] = employeelist
	session['empname'] = empname
	session['emprate'] = emprate
	currentMonth = datetime.now().month
	currentYear = datetime.now().year
	prevyr = str(currentYear - 1)
	nextyr = str(currentYear + 1)
	thisyr = str(currentYear)
	if currentMonth < 4:
		finyearnow = prevyr[-2:]+"-"+thisyr[-2:]
	else:
		finyearnow = thisyr[-2:]+"-"+nextyr[-2:]
	worklastinvno  = list(work_last_inv_no.find({"fin_year" : finyearnow}))
	if len(worklastinvno) == 0:
		invoice_serial = 1
		new_last_inv_dict = {
						"fin_year": finyearnow, 
						"LastInvoiceNumber" :0
					}
		new_last_inv_insert = work_last_inv_no.insert_one(new_last_inv_dict)
	else:
		for rec in worklastinvno:
			ws_work_last_inv_no = rec.get("LastInvoiceNumber")
			db_finyear = rec.get("fin_year")
		if finyearnow == db_finyear:
			invoice_serial = ws_work_last_inv_no + 1
		else:
			invoice_serial = 1
	if request.method == 'POST':
		if request.form['wrkinv_submit_botton'] == 'Create Invoice':
			selected_party_string = request.form['sel_party']
			selected_party_string_array = selected_party_string.split("|")
			selected_party = selected_party_string_array[0]
			party_state = selected_party_string_array[1]
			party_gst_no = selected_party_string_array[2]
			work_invoice_number = request.form['invoice_number']
			work_invoice_date = request.form['work_invoice_date']
			work_desc = request.form['work_desc']
			datelist = request.form.getlist('line_date[]')
			emplist = request.form.getlist('selempname[]')
			hrslist = request.form.getlist('hours[]')
			mtslist = request.form.getlist('mts[]')
			ratelist = request.form.getlist('line_rate[]')
			amtlist = request.form.getlist('line_amount[]')
			list_len = len(datelist)
			#take the list in the range 1,2,3 not 0,1,2
			#store the entered invoice in a csv file
			invoice_number_for_file = work_invoice_number.replace('/','-')
			csv_file_name = staticpath+"Calc_Sheet_"+invoice_number_for_file+".csv"
			header_array = []
			header_array.append("Invoice Number:")
			header_array.append(work_invoice_number)
			header_array.append(work_invoice_date)
			party_array = []
			party_array.append(selected_party)
			party_array.append(party_state)
			party_array.append(party_gst_no)
			work_desc = " ".join(work_desc.split())
			work_desc_array=[]
			descline_pipes=[]
			if len(work_desc) > 80:
				work_desc = insert_newlines(work_desc, every=80)
				descline_pipes =  insert_pipes(work_desc, every=80)
				descline_array =descline_pipes.split("|")
			else:
				descline_array=[]
				descline_array.append(work_desc)
			#print(descline_array)
			#print("len of descline_array in main ", len(descline_array))
			work_desc_array.append(work_desc)
			total_work_amount = 0
			with open(csv_file_name, 'w', newline='') as csvfile:
			     writer = csv.writer(csvfile)
			     writer.writerow(header_array)
			     writer.writerow(party_array)
			     writer.writerow(work_desc_array)
			     writer.writerow(["SNo", "Date", "Employee", "Rate","Hours", "Mts", "Amount"])
			     invoice_detail_array =[]
			     detail_dict ={}
			     for lineno in range(1, list_len):
			     	line_array =[]
			     	line_array.append(lineno)
			     	lstr = "_"+str(lineno)
			     	field1 = "lineno"+lstr
			     	detail_dict[field1] = lineno
			     	line_array.append(datelist[lineno])
			     	field2 = "line_date"+lstr
			     	detail_dict[field2] = datelist[lineno]
			     	line_array.append(emplist[lineno])
			     	field3 = "line_emp"+lstr
			     	detail_dict[field3] = emplist[lineno]
			     	line_array.append(ratelist[lineno])
			     	field4 = "line_rate"+lstr
			     	detail_dict[field4] = int(ratelist[lineno])
			     	line_array.append(hrslist[lineno])
			     	field5 = "line_hrs"+lstr
			     	detail_dict[field5] = int(hrslist[lineno])
			     	line_array.append(mtslist[lineno])
			     	field6 = "line_mts"+lstr
			     	detail_dict[field6] = int(mtslist[lineno])
			     	line_array.append(amtlist[lineno])
			     	field7 = "line_amt"+lstr
			     	detail_dict[field7] = int(float(amtlist[lineno]))
			     	total_work_amount = total_work_amount + int(amtlist[lineno])
			     	writer.writerow(line_array)
			     	invoice_detail_array.append(line_array)
			     total_line=["", "", "", "","", "Total:"]
			     total_line.append(total_work_amount)
			     writer.writerow(total_line)
			 
			csvfile.close()
			party_by_gst = list(work_invoice_party.find({"party_gst_no" : party_gst_no }))
			for rec in party_by_gst:
				party_gst_add = rec.get("party_gst_address")
			if party_gst_no != "NO GST NO. ":
				work_sgst = 9.0/100.0*total_work_amount
				work_cgst = work_sgst
				work_gst = work_cgst + work_sgst
				grand_total_work_amount = total_work_amount +work_gst
			else:
				work_sgst = 0.0
				work_cgst = 0.0
				work_gst = 0.0
				grand_total_work_amount = total_work_amount
			work_gst =myround(float(work_gst))
			work_sgst =myround(float(work_sgst))
			work_cgst =myround(float(work_cgst))
			#print(work_gst)
			#end of storing in csv file
			#=== print the invoice and show
			work_invoice_pdfcreate()
			#=== end of print invoice and show
			#== store in the invoice in db
			now = datetime.now()
			work_invoice_rec = {
							"Work_invoice_number": work_invoice_number , 
							"Work_invoice_date": work_invoice_date,
							"Work_invoice_party": selected_party,
							"Work_invoice_party_state" : party_state,
							"Work_invoice_party_gst_no" : party_gst_no,
							"Work_invoice_description" : work_desc,
							"work_invoice_details" : detail_dict,
							"work_invoice_total_amount" : total_work_amount,
							"work_invoice_record_timestamp" : now
						}
			work_inv_coll_insert = work_invoice_collection.insert_one(work_invoice_rec)
			
			rquery = {"fin_year" : finyearnow}
			updated_rec = { "$set": 
							{ 
							 "LastInvoiceNumber" : invoice_serial
							}
					}
			work_last_inv_no.update_one(rquery, updated_rec)
			
		if request.form['wrkinv_submit_botton'] == 'Exit':	
			return '%s' 'Thank you for using Work Invoicing system'
	return render_template('work_invoice_generate.html',passemprate = emprate, passinv_serial = invoice_serial)	

@RentInvoice.route('/afterlogin_winv', methods=['GET', 'POST'])
def afterlogin_winv():

		gotname = session.get("work_email")
		gotpassword = session.get("work_password")
		dbopen()
		global environ
		finduser = Invoice_Users_Collection.find({"work_id" : gotname})
		finduserlist = list(finduser)
		if len(finduserlist) != 0:
			for re_cord in finduserlist:
				dbpassword = re_cord.get("work_password")
				mykey = re_cord.get("work_passkey")
				session['work_type'] = re_cord.get("work_type")
				decoded = cryptocode.decrypt(dbpassword,mykey)
				if decoded == gotpassword:
					error = False
					session['error'] = error
					session['work_password'] =""
					print(session['work_username']," logged in at ", datetime.now())
					return redirect(url_for('work_invoice_generate'))
				else:
					error = True
					session['error'] = error
					return  redirect(url_for('winv'))
			#endfor
		else:
			error = True
			session['error'] = error
			return redirect(url_for('winv'))
			return render_template('afterlogin_winv.html')		

@RentInvoice.route('/forgot_winv', methods=['GET', 'POST'])
def forgot_winv():
	work_dbopen()
	global Invoice_dbclient, work_invoice_db, work_invoice_party, work_last_inv_no, work_invoice_collection, winv_Users_Collection
	global fpusername
	session['sentotp_winv'] = False
	session['nouser_winv'] = False
	session['noemail_winv'] = False 
	session['nootp_winv'] = False
	session['nomatch_winv'] = False
	if request.method == 'POST':
		if request.form['submit_button'] == 'Mail me OTP':
			print("posted")
			fpemailid_winv  = request.form['work_email']
			print(fpemailid_winv)
			finduser = winv_Users_Collection.find({"work_email" : fpemailid_winv})
			finduserlist = list(finduser)
			if len(finduserlist) == 0:
				session['nouser_winv'] = True
				render_template('forgot_winv.html')
			else:
				session['nouser_winv'] = False
				wsemail = fpemailid_winv
				print(wsemail)
				myotp, mytime = winv_sendotp(wsemail)
				winv_Users_Collection.update_one(re_cord, {'$set': {'otp': myotp, 'otptime': mytime}})
				session['sentotp_winv'] = True
		if request.form['submit_button'] == 'Verify OTP':
			dig1 = request.form['dig1']
			dig2 = request.form['dig2']
			dig3 = request.form['dig3']
			dig4 = request.form['dig4']
			dig5 = request.form['dig5']
			otpassword = dig1 + dig2 + dig3 + dig4 + dig5
			for re_cord in finduserlist:
				storedotp = re_cord.get('otp')
				storedotptime = re_cord.get('otptime')
				timenow = time.time()
				if (timenow - storedotptime) > 180:
					session['nootp'] = Truereturn 
					redirect(url_for('forgot_winv'))
				else:
					if storedotp != otpassword:
						session['nootp'] = True
						return redirect(url_for('forgot_winv'))
					else:
						session['nootp'] = False
						newpassword1 = request.form['newpassword1']
						newpassword2 = request.form['newpassword2']
						if newpassword1 != newpassword2:
							session['nomatch'] = True
							return redirect(url_for('resetpassword_winv'))
						else:
							fpemailid_winv  = request.form['work_email']
							finduser = winv_Users_Collection.find({"work_email" : fpemailid_winv})
							finduserlist = list(finduser)
							encoded = cryptocode.encrypt(newpassword1,"211219630525")
							for re_cord1 in finduserlist:
								winv_Users_Collection.update_one(re_cord1, {'$set': { 
                                	"work_password" : encoded,
                                	"work_passkey"  : "211219630525"
                                }})
							return redirect(url_for('afterlogin_winv'))
		#if request.form['submit_button'] == 'Exit':
			return redirect(url_for('winv'))
	return render_template('forgot_winv.html')

@RentInvoice.route('/otp_winv', methods=['GET', 'POST'])
def otp_winv():
	
	return render_template('otp_winv.html')		

@RentInvoice.route('/resetpassword_winv', methods=['GET', 'POST'])
def resetpassword_winv():
    # Your code for handling the password reset goes here
    return render_template('resetpassword_winv.html')
 
    

@RentInvoice.route('/winv', methods=['GET', 'POST'])
def winv():
	work_dbopen()
	global Invoice_dbclient, work_invoice_db, work_invoice_party, work_last_inv_no, work_invoice_collection, winv_Users_Collection
	error = None
	if request.method == 'POST':
		if request.form['submit_button'] == 'Login': 
			wsemail = request.form['workemail'] 
			if session.get('workemail') == wsemail:
				error = True
				print(wsemail,' has another session logged in')
			session['workemail'] = wsemail
			session['new-password'] = request.form['new-password']
			
			return redirect(url_for('work_invoice_generate'))
		if request.form['submit_button'] == 'Forgot Password':
			return redirect(url_for('forgot_winv'))
		if request.form['submit_button'] == 'Login':
			return redirect(url_for('afterlogin_winv'))	
	return render_template('winv.html')


def winv_sendotp(emailid):
    receiver = emailid
    digits = "0123456789"
    OTP = ""
    for i in range(5):
        OTP += random.choice(digits)  # Generate a random digit
    otpgentime = time.time()
    print("Generated OTP:", OTP)

    message = MIMEMultipart()
    message['From'] = "ramadas@kappsoft.com"
    message['To'] = receiver
    message['Subject'] = " OTP for Work Invoice Reset Password "
    message.attach(MIMEText(OTP, 'plain'))
    mailsession = smtplib.SMTP('mail.kappmedia.com', 587, timeout=360)
    mailsession.starttls()
    sender = "ramadas@kappsoft.com"
    empassword = "Kandatha68"
    try:
        print("Attempting to log in...")
        mailsession.login(sender, empassword)
        print("Logged in successfully.")
        text = message.as_string()
        print("Sending email...")
        print("From:", sender)
        print("To:", receiver)
        print("Email content:\n", text)
        mailsession.sendmail(sender, receiver, text)
        print("Email sent successfully.")
        mailsession.quit()
        return OTP, otpgentime
    except Exception as e:
        print("Email sending failed:", str(e))
        return None, None

# Test the function
otp, otpgen_time = sendotp("madhana@kappsoft.com")
if otp is not None:
    print("OTP sent:", otp)
    print("OTP generation time:", otpgen_time)
else:
    print("OTP sending failed.")


def is_number(n):
	try:
		float(n)   # Type-casting the string to `float`.
				   # If string is not a valid `float`, 
				   # it'll raise `ValueError` exception
	except ValueError:
		return False
	return True




@RentInvoice.route('/wdet', methods=['GET', 'POST'])
def wdet():
	error = None
	if request.method == 'POST':
		if request.form['submit_button'] == 'Log In':
			wsemail = request.form['wdet_email'] 
			if session.get('wdet_email') == wsemail:
				error = True
				print(wsemail,' has another session logged in')
			session['wdet_email'] = wsemail
			session['wdet_password'] = request.form['wdet_password']
			return redirect(url_for('wdet_afterlogin'))
		if request.form['submit_button'] == 'Forgot Password':
			return redirect(url_for('forgot_wdet'))
	return render_template('wdet.html')


@RentInvoice.route('/logout', methods = ['POST', 'GET'])
def logout():
	if session.get('username') is not None:
		print(session['username']," logged out of RentInvoice at ", datetime.now())
	#Invoice_dbclient.close()
	for key in list(session.keys()):
				if key != 'username' \
				and key != 'User_type' \
				and key != 'justmailed' \
				and key != 'dummyinvoice' :
					session.pop(key)
	retvalue = "GoodBye, Thanks for using Rent Invoice app"
	return  '%s' %retvalue

#RentInvoice = flask.Flask(__name__)

'''
if __name__ == "__main__":
	from waitress import serve
	import logging
	#logging.basicConfig(level=logging.DEBUG)
	print("RentInvoice is running through Waitress WSGI")
	dbopen()
	serve(RentInvoice, host="0.0.0.0", port=5000)
'''
#use the following in dvelopment for debugging
if __name__ == '__main__':
	RentInvoice.run(host='0.0.0.0', port=5000, debug = True)
	#RentInvoice.run(debug=True)

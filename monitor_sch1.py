from flask import Flask, request, url_for, redirect, session, render_template, json, send_file
from flask_session import Session
import pymongo
from subprocess import check_output
import subprocess
import cryptocode
import datetime
from datetime import date
import time
from datetime import datetime, timedelta
import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import atexit
from apscheduler.schedulers.blocking import BlockingScheduler
import gc

global monitor_collection, monitor_db, monitor_dbclient
monitor_dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
monitor_db = monitor_dbclient["MonitorSupport"]
monitor_collection = monitor_db["Idle_time"]


global support_user, messtext, mess_subject, prev_idle_duration, log_file, just_after_logon,get_result
just_after_logon = False


def quser_output():
	#print("inside main function quser_output")
	gc.collect()
	global messtext, mess_subject, support_user, prev_idle_duration, just_after_logon, get_result
	global monitor_collection, monitor_db, monitor_dbclient
	os.system("C:\\Windows\\Sysnative\\quser.exe > quser1.txt")
	'''
	get_result = check_output(r"C:\Windows\Sysnative\quser.exe", shell=True, stderr=False)
	result_str = get_result.decode('utf-8')
	#print(result_str)
	
	orig_stdout = sys.stdout
	sys.stdout=open('quser1.txt','w')
	print(result_str) #never comment out this print statement
	sys.stdout.close()
	sys.stdout=orig_stdout 
	'''
	present_time = str(datetime.now())
	mess_subject = "User status "+present_time
	
	qs = open("C:\\monitor\\Scripts\\quser1.txt", "r")
	
	rec_count=0
	messtext =""
	#print(qs)
	#s=input("  ")
	for line in qs:
		
		#print("read the record:",line)
		#s=input("  ")
		rec_count = rec_count + 1
		#print(rec_count)
		if line.strip() != "":
			username = line[0:22]
			sessioname = line[22:41]
			processid = line[41:44]
			state = line[45:52]
			idletime = line[53:63]
			logontime = line[64:84]
			if  state.strip() == 'Disc':
				#print("needed for mailing:", line)
				last_logon_date = line[65:74].replace('-','')
				last_logon_time = line[75:84].replace('\n','')
				last_logon_time = line[75:84].replace(' ','~')
				logon_hhmm, logon_am_pm = last_logon_time.split('~')
				in_logon_time = datetime.strptime(last_logon_date+" "+logon_hhmm+" "+logon_am_pm.strip(), "%d%b%y %I:%M %p")
				out_logon_time = datetime.strftime(in_logon_time, "%d-%m-%Y %H:%M")
				logon_age = datetime.now() - datetime.strptime(out_logon_time,"%d-%m-%Y %H:%M")
				if logon_age.days < 1 and logon_age.seconds < 82800:
					messtext = messtext + line + '\n'
			else:
				messtext = messtext + line + '\n'
			if not(username.strip() == 'USERNAME' or username.strip() == 'administrator' or username.strip() == '>administrator' or state.strip() == 'Disc' or idletime.strip() == 'none'  or idletime.strip() == '.'):
				
				#print("needed for database:", line)
				idletime = idletime.strip()
				if ':' in idletime:
					idlehrs, idlemts = idletime.split(':')
					hrs_to_mts = int(idlehrs) * 60
					idle_in_mts = hrs_to_mts + int(idlemts)
					for_db_idletime = float(idle_in_mts)
				else:
					for_db_idletime = float(idletime)
				#print('idle time for db:',for_db_idletime)
				#s=input("  ")
				#65:74 date
				#75:84 time
				last_logon_date = line[65:74].replace('-','')
				last_logon_time = line[75:84].replace('\n','')
				last_logon_time = line[75:84].replace(' ','~')
				logon_hhmm, logon_am_pm = last_logon_time.split('~')
				
				in_logon_time = datetime.strptime(last_logon_date+" "+logon_hhmm+" "+logon_am_pm.strip(), "%d%b%y %I:%M %p")
				
				out_logon_time = datetime.strftime(in_logon_time, "%d-%m-%Y %H:%M")
				#print(out_logon_time)
				capture_time = datetime.now()
				idle_record_dict = {
						"CaptureTime": capture_time, 
						"SupportUser": username,
						"IdleDuration":for_db_idletime,
						"LastLogonTime":out_logon_time
					}
				sleep(2)
				messtext = 'This is a test message for debugging before writing to db (Please ignore)'
				send_the_mail()
				idle_record_insert = monitor_collection.insert_one(idle_record_dict)
				sleep(2)
				messtext = 'This is a test message for debugging after writing to db (Please ignore)'
				send_the_mail()
				#print(" quser written to database "+str(datetime.now()))
				#s=input("  ")
	#print(result_str)
	#messtext = result_str
	#print("mailed text:", messtext)
	'''
	if messtext != "":
		messtext = messtext + "[This is from Windows Services monitor_sch]"
		#print(messtext)
		#s=input("  ")
	''' 
	messtext = 'This is a test message for debugging - proc last line (Please ignore)'
	send_the_mail()
	

def send_the_mail():
	global messtext, mess_subject
	receiver = "deepika@kappsoft.com"
	message = MIMEMultipart()
	message['From'] = "idle_trigger@kappsoft.com"
	message['To'] = receiver
	message['Subject'] =  mess_subject
	sender = "idle_trigger@kappsoft.com"
	empassword = "dR7*CPcJ2DZ=<bJX"
	message.attach(MIMEText(messtext, 'plain'))
	smtp_done = False
	starttsl_done = False
	login_done = False
	sendmail_done = False
	try:
		mailsession = smtplib.SMTP('mail.kappmedia.com', 587, timeout=360)
		smtp_done = True
	except:
		smtp_done = False
	if smtp_done:
		try:
			mailsession.starttls()
			starttsl_done = True
		except:
			starttsl_done = False
		
	if starttsl_done:
		try:
			mailsession.login(sender, empassword)
			login_done = True
		except:
			login_done = False

	if login_done:
		text = message.as_string()
		try:
			mailsession.sendmail(sender, receiver, text)
			sendmail_done = True
		except:
			sendmail_done = False
			
	if sendmail_done:
		mailsession.quit()
		#print("mail sent ", str(datetime.now()))


#print("Monitor process Started at ",str(datetime.now()))
quser_output()
scheduler1 = BlockingScheduler()
#scheduler.add_job(func=quser_output, trigger="interval", seconds=900)
#
scheduler1.add_job(quser_output, 'cron', hour=6, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=6, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=6, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=6, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=7, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=7, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=7, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=7, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=8, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=8, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=8, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=8, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=9, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=9, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=9, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=9, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=10, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=10, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=10, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=10, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=11, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=11, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=11, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=11, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=12, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=12, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=12, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=12, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=13, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=13, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=13, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=13, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=14, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=14, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=14, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=14, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=15, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=15, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=15, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=15, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=16, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=16, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=16, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=16, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=17, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=17, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=17, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=17, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=18, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=18, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=18, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=18, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=19, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=19, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=19, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=19, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=20, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=20, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=20, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=20, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=21, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=21, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=21, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=21, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=22, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=22, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=22, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=22, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=23, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=23, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=23, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=23, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=0, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=0, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=0, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=0, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=1, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=1, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=1, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=1, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=2, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=2, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=2, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=2, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=3, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=3, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=3, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=3, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=4, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=4, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=4, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=4, minute=45)
#
scheduler1.add_job(quser_output, 'cron', hour=5, minute=0)
scheduler1.add_job(quser_output, 'cron', hour=5, minute=15)
scheduler1.add_job(quser_output, 'cron', hour=5, minute=30)
scheduler1.add_job(quser_output, 'cron', hour=5, minute=45)
scheduler1.start()

atexit.register(lambda: scheduler1.shutdown())





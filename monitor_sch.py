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
from apscheduler.schedulers.background import BackgroundScheduler

global monitor_collection, monitor_db, monitor_dbclient
monitor_dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
monitor_db = monitor_dbclient["MonitorSupport"]
monitor_collection = monitor_db["Idle_time"]

MonitorUsers = Flask(__name__)
MonitorUsers.config["SESSION_PERMANENT"] = False
MonitorUsers.config["SESSION_TYPE"] = "filesystem"
import hashlib
secret_string = str(datetime.now())
result = hashlib.sha256(secret_string.encode())

result_hex = result.hexdigest()
secret_key = result_hex.encode('ASCII')

MonitorUsers.config['SECRET_KEY'] = secret_key

Session(MonitorUsers)


global support_user, messtext, mess_subject, prev_idle_duration, log_file, just_after_logon,get_result
just_after_logon = False


def quser_output():
	print("inside main function quser_output")
	global messtext, mess_subject, support_user, prev_idle_duration, just_after_logon, get_result
	get_result = check_output(r"C:\Windows\Sysnative\quser.exe", shell=True, stderr=False)
	result_str = get_result.decode('utf-8')
	#print(result_str)
	orig_stdout = sys.stdout
	sys.stdout=open('quser.txt','w')
	print(result_str)
	sys.stdout.close()
	sys.stdout=orig_stdout 
	present_time = str(datetime.now())
	mess_subject = "User status "+present_time
	qs = open("quser.txt", "r")
	rec_count=0
	messtext =""
	for line in qs:
		#print("read the record:",line)
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
				print("needed for database:", line)
				idletime = idletime.strip()
				if ':' in idletime:
					idlehrs, idlemts = idletime.split(':')
					hrs_to_mts = int(idlehrs) * 60
					idle_in_mts = hrs_to_mts + int(idlemts)
					for_db_idletime = float(idle_in_mts)
				else:
					for_db_idletime = float(idletime)
				print('idle time for db:',for_db_idletime)
				#65:74 date
				#75:84 time
				last_logon_date = line[65:74].replace('-','')
				last_logon_time = line[75:84].replace('\n','')
				last_logon_time = line[75:84].replace(' ','~')
				logon_hhmm, logon_am_pm = last_logon_time.split('~')
				
				in_logon_time = datetime.strptime(last_logon_date+" "+logon_hhmm+" "+logon_am_pm.strip(), "%d%b%y %I:%M %p")
				
				out_logon_time = datetime.strftime(in_logon_time, "%d-%m-%Y %H:%M")
				print(out_logon_time)
				capture_time = datetime.now()
				idle_record_dict = {
						"CaptureTime": capture_time, 
						"SupportUser": username,
						"IdleDuration":for_db_idletime,
						"LastLogonTime":out_logon_time
					}
				idle_record_insert = monitor_collection.insert_one(idle_record_dict)
				print(" quser written to database "+str(datetime.now()))
	#print(result_str)
	#messtext = result_str
	print("mailed text:", messtext)
	if messtext != "":
		messtext = messtext + "\n[Note to developer: This is from new scheduler]"
		send_the_mail()
	shift_reporting()

def shift_reporting():
	print('in shift reporting process')
	global messtext, mess_subject, support_user
	global monitor_collection, monitor_db, monitor_dbclient
	#if time is between 10:00 am and 10:15 am
	#if time is between 18:00 pm and 18:15 pm
	#if time is between 02:00 am and 02:15 am
	present_time = str(datetime.now())
	now=datetime.now()
	present_year = int(datetime.now().year)
	present_month = int(datetime.now().month)
	present_day = int(datetime.now().day)
	present_hour = int(datetime.now().hour)
	present_minute = int(datetime.now().minute)
	present_second = int(datetime.now().second)
	print('Present hour ',present_hour, ' Present minute ', present_minute)
	if (present_hour == 10 and present_minute <= 29)  or (present_hour == 18 and present_minute <= 29) or (present_hour == 2 and present_minute <= 29):
		end_time = datetime(present_year, present_month, present_day, present_hour, present_minute, present_second)
		now_minus_8hours = now - timedelta(hours = 8.5)
		start_time = datetime(int(now_minus_8hours.year), int(now_minus_8hours.month), int(now_minus_8hours.day), int(now_minus_8hours.hour), int(now_minus_8hours.minute), int(now_minus_8hours.second))
		#print(start_time)
		
		find_docs = list(monitor_collection.find({'CaptureTime': { '$gte': start_time, '$lte': end_time } }))
		#print(find_docs)
		docs_array = []
		for doc in find_docs:
			docs_line = []
			docs_line.append(doc.get('SupportUser'))
			docs_line.append(doc.get('IdleDuration'))
			docs_line.append(doc.get('LastLogonTime'))
			docs_array.append(docs_line)
		#print(docs_array)
		docs_array.sort(key=lambda row: (row[0],row[2]))
		#print("after sort")
		#print(docs_array)
		prev_user = docs_array[0][0]
		prev_logon_time = docs_array[0][2]
		idle_array=[]
		max_idle_time =0.0
		for_message = ""
		for i in range(0, len(docs_array)):
			#print(docs_array[i][0], docs_array[i][2], docs_array[i][1])
			idle_array.append(docs_array[i][1])
			if docs_array[i][0] != prev_user and docs_array[i][2] != prev_logon_time:
				max_idle_time = max(idle_array)
				#print("grouped data:", prev_user, prev_logon_time, max_idle_time)
				for_message = for_message + '\n' + prev_user.upper() + 'Idle time: '+ str(max_idle_time)+" mts"
				prev_user = docs_array[i][0]
				prev_logon_time = docs_array[i][2]
				idle_array=[]
				idle_array.append(docs_array[i][1])
		max_idle_time = max(idle_array)
		#print("grouped data:", prev_user, prev_logon_time, max_idle_time)
		for_message = for_message + '\n' + prev_user.upper() + 'Idle time: '+ str(max_idle_time)+" mts"
		mess_subject = "Idle time From: "+str(start_time)+" To: "+ str(end_time)
		messtext = mess_subject + '\n'+for_message
		send_the_mail()

def send_the_mail():
	global messtext, mess_subject
	receiver = "monitor_idle@kappsoft.com"
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
		print("mail sent ", str(datetime.now()))


print("Monitor process Started at ",str(datetime.now()))
#quser_output()
scheduler = BackgroundScheduler()
scheduler.add_job(func=quser_output, trigger="interval", seconds=900, misfire_grace_time=None)
scheduler.start()
#atexit.register(lambda: scheduler.shutdown())


'''
if __name__ == "__main__":
	from waitress import serve
	import logging
	#logging.basicConfig(level=logging.DEBUG)
	print("MonitorUsers is running through Waitress WSGI")
	dbopen()
	serve(MonitorUsers, host="0.0.0.0")
'''
#use the following in dvelopment for debugging

if __name__ == '__main__':
	MonitorUsers.run(host='0.0.0.0',  debug = False)

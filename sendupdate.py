#!/usr/bin/python
import urllib2, json, sqlite3, yaml, smtplib, sys
from email.mime.text import MIMEText
try:
    info = yaml.load(open(sys.argv[1],'r'))
except IndexError:
    print 'usage: %s configuration_file' % sys.argv[0]
    sys.exit(1)
except yaml.YAMLError, exc:
    print 'Error in configuration file:', exc
    sys.exit(2)

try:
    filemsg = ' based on the data in ' +  open('fileinfo.txt').readline()[:-1]
except:
    filemsg = ''


def sendmail(info):
    print 'Sending update notice'
    mtext = """The training reports have been updated%s.
See http://d4tm.org/files/training/report.html.  
There is also an Excel version of the report at http://d4tm.org/files/training/report.xlsx.""" % filemsg
    message = MIMEText(mtext)
    message['Subject'] = 'The training reports have been updated.'
    message['From'] = info['from']
    message['To'] = info['to']
    info['s'].sendmail(info['from'], [info['to']], message.as_string())
    if 'bcc' in info:
        info['s'].sendmail(info['from'], [info['bcc']], message.as_string())


print 'connecting to', info['mailserver']
info['s'] =  smtplib.SMTP(info['mailserver'], info.get('mailport', 25))
info['s'].login(info['from'], info['mailpw'])
sendmail(info)

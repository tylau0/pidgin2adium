#!/usr/bin/python

# pidgin2adium.py
# A script to convert Pidgin conversation log to Adium format
# Author: Eddie Lau
# Released under GPL v3 license

# Usage:
# 1) Locate a system that can run python scripts.
# 2) Put BeautifulSoup.py (from BeautifulSoup 3) and this file in the same folder.
# 3) Edit the user input parameters section and the Adium specific parameters section if needed.
# 4) You may choose to use options to override the parameters.
#    python pidgin2adium.py --indir "<indir>" --outdir "<outdir>" --username <pidgin_account_username> --domain <pidgin_account_domain> --service <im_service_protocol>

import os
from os import walk
import re
from datetime import date, datetime, timedelta
from BeautifulSoup import BeautifulSoup, Tag, NavigableString, BeautifulStoneSoup
from optparse import OptionParser

#### user input parameters ####
# location of the jabber logs of a particular account
# you should see a number of folders whose names are the contacts
indir="/Users/LocalAC/Downloads/logs/jabber/username@domain.com"  
# location of the Adium logs
outdir="/Users/LocalAC/Library/Application Support/Adium 2.0/Users/LocalAC/Logs/Jabber.username@domain.com"
# Assume that you use username@domain as the IM account
# your account user name
username="username"  
# domain of your user account
domain="domain.com"   

#### Adium specific parameters ####
XMLNS="http://purl.org/net/ulf/ns/0.4-02"
SERVICE="Jabber"
ADIUMVERSION="1.5.7"
BUILDID="c72b164f75a7"

#### Debug parameters -- 0, 1, 2. Larger number for more debug info ####
VERBOSE = 1

#### Program start ####

# override default paramters if there is any given from command line
parser = OptionParser()
parser.add_option("-i", "--indir", dest="indir", help="Input Pidgin protocol-account folder", metavar="FOLDER")
parser.add_option("-o", "--outdir", dest="outdir", help="Output Adium protocol.account folder", metavar="FOLDER")
parser.add_option("-u", "--username", dest="username", help="Username for this protocol-account", metavar="USERNAME")
parser.add_option("-d", "--domain", dest="domain", help="domain for this protocol-account", metavar="DOMAIN")
parser.add_option("-s", "--service", dest="SERVICE", help="service name", metavar="SERVICENAME")
(options, args) = parser.parse_args()

if options.indir is not None:
    indir = options.indir
if options.outdir is not None:
    outdir = options.outdir
if options.username is not None:
    username = options.username
if options.domain is not None:
    domain = options.domain
if options.SERVICE is not None:
    SERVICE = options.SERVICE

# construct 
account = username + "@" + domain
phidden = re.compile('^\..+')

# Going through the contact folders one by one
for contact in os.listdir(indir):
    subfolder = os.path.join(indir, contact)
    if os.path.isdir(subfolder) and phidden.match(contact) is None:
    	if VERBOSE >= 1:
    	    print "Working on contact:", contact
        # create an output subfolder for the contact
        outcontactdirpath = os.path.join(outdir, contact)
        if not os.path.exists(outcontactdirpath):
            os.makedirs(outcontactdirpath)
            if VERBOSE >= 2:
                print "-- Creating output folder", outcontactdirpath
        # process the text log in the contact folder
        for txtlog in os.listdir(subfolder):
            fulltxtlog = os.path.join(subfolder, txtlog)
            if os.path.isfile(fulltxtlog) and txtlog.find(".txt"): 
                if VERBOSE >= 2:
                    print "---- Working with input pidgin log file", fulltxtlog
                # txtlog format: 2013-03-26.132208-0700PDT.txt
                # to be converted: 2013-03-26T132208-0700
                starttstamp = txtlog[0:10]+"T"+txtlog[11:13]+"."+txtlog[13:15]+"."+txtlog[15:17]+txtlog[17:22]
                chatfolder = contact+" ("+starttstamp+").chatlog"
                chatfile = contact+" ("+starttstamp+").xml"
                timezone = txtlog[17:22]
                # Figure out the chat start time from the folder name
                startyear=txtlog[0:4]
                startmonth=txtlog[5:7]
                startday=txtlog[8:10]
                starthour=txtlog[11:13]
                startmin=txtlog[13:15]
                startsec=txtlog[15:17]
                timezone=txtlog[17:20]+":"+txtlog[20:22]
                # variables to keep track of time the first and last messages
                firsttstamp = '' # this one only updates once
                lasttstamp = ''  # this one keeps updating
                # create an XML soup for the converted log with the header info
                soup = BeautifulStoneSoup('<?xml version="1.0" encoding=""?>')
                # Populate the soup
                chatTag = Tag(soup, "chat")
                chatTag['xmlns'] = XMLNS
                chatTag['account'] = account
                chatTag['service'] = SERVICE
                chatTag['adiumversion'] = ADIUMVERSION
                chatTag['buildid'] = BUILDID
                soup.append(chatTag)
                # Parse a pidgin log file and compose the Adium log file
                # Pidgin log format note:
                # 1) Messages starts from the 2nd line
                # 2) The first line of a message starts with a timestamp embraced by ()
                #    * (5/6/2015 12:13:14 AM) -- for msg date different from what is recorded in the filename)
                #    * (2:05:59 PM) -- for msg date the same as the one recored in the filename 
                # 3) If the current line is a continuation of the message started in some previous line, it will not have the above time header. 
                # 4) After the timestamp, it has optional sender info before the next :. No sender info if the message is a status update.
                #    * (2:05:59 PM) user@somedomain.com
                # Adium log format note:
                # 1) Sample log format
                #    <chat xmlns="http://purl.org/net/ulf/ns/0.4-02" account="user@domain.com" service="Jabber" adiumversion="1.5.7" buildid="c72b164f75a7">
                #    <event type="WindowOpened" sender="user@domain.com" time="2014-12-04T16:14:01+08:00">
                #    </event>
                #    <message sender="user@domain.com" time="2014-12-04T16:14:01+08:00">
                #    <div>
                #    user2@domain.com is now known as Chris Wong.
                #    </div>
                #    </message>
                #    <event type="WindowClosed" sender="user@domain.com" time="2014-12-04T16:14:01+08:00">
                #    </event>
                #    </chat>
                # 2) sender and time as two attributes of the message tag
                # 3) The formatting by the line breaks and spacings inside the message tag are accurately reproduced in the Adium conversation log viewer.
                # 4) The window open time shouldn't be earlier than the one stated in the log file name.
                # 5) The window close time shouldn't be earlier than any message timestamp.
                with open(os.path.join(subfolder, fulltxtlog)) as f:
                    tmplines = f.readlines()                   
                    # Patterns for checking presence of timestamp
                    # (date time)
                    p01 = re.compile('^\([1]?[0-9]\/[1-3]?[0-9]\/[0-9]{4}\s[0-9]?[0-9]:[0-9][0-9]:[0-9][0-9]\s[AP]M\)\s')
                    # (time) 
                    p02 = re.compile('^\([0-9]?[0-9]:[0-9][0-9]:[0-9][0-9]\s[AP]M\)\s')
                    # Patterns for checking presence of sender
                    # (date, time) sender:
                    p11 = re.compile('^\([1]?[0-9]/[1-3]?[0-9]/[0-9]{4}\s[0-9]?[0-9]:[0-9][0-9]:[0-9][0-9]\s[AP]M\)\s[\S]+:\s')
                    # (time) sender:
                    p12 = re.compile('^\([0-9]?[0-9]:[0-9][0-9]:[0-9][0-9]\s[AP]M\)\s[\S]+:\s')
                    
                    YY = int(startyear)
                    MM = int(startmonth)
                    DD = int(startday)
                    hh = ''
                    mm = ''
                    ss = ''
                    apm = ''
                    sender = ''  # sender is '' if the thread is a status update
                    linebuf = []  # buffer storing lines of the same message
                    for line in tmplines[1:]:
                        if VERBOSE >= 3:
                            print "------ ===="
                            print "------ len(linebuf):", len(linebuf)
                            print "------ line to process:", line
                            if p01.match(line) is None and p02.match(line) is None:
                                print "------ timestamp header found"
                            else:
                                print "------ timestamp header not found"
                        # If no timestamp header is found, the line is the continuation of a message.
                        # just need to push the message segment on this line to the buffer
                        if p01.match(line) is None and p02.match(line) is None:
                            linebuf.append(line)
                        else:
                            # timestamp header found, it's the start of a message
                            # If linebuf is not empty, flush its content first
                            if len(linebuf) > 0:
                                # time to process the linebuf
                                #print YY, MM, DD, hh, mm, ss, apm, sender
                                tstamp = datetime(YY, MM, DD, hh, mm, ss)
                                tstampstr = tstamp.strftime('%Y-%m-%dT%H:%M:%S')+timezone
                                # If the sender doesn't include the email server info, assume it is from the account owner
                                if sender.strip() == username:
                                    sender = account
                                if VERBOSE >= 3:
                                    print "------ ****"
                                    print "------ Message to be written:"
                                    print "------ Time:" + tstampstr
                                    print "------ Sender:" + sender
                                    print "------ Message:" 
                                    # formulate the time 
                                    for l in linebuf:
                                        print "------", l
                                    print "------ ****"
                                # construct the XML message
                                messageTag = Tag(soup, "message")
                                if sender.strip() == '':
                                    messageTag['sender'] = account
                                else:
                                    messageTag['sender'] = sender
                                messageTag['time'] = tstampstr
                                if firsttstamp == '':
                                    firsttstamp = tstampstr
                                lasttstamp = tstampstr
                                chatTag.append(messageTag)
                                divTag = Tag(soup, "div")
                                messageTag.append(divTag)
                                for i in range(len(linebuf)):
                                    text = NavigableString(linebuf[i])
                                    divTag.append(text)
                                    if i < len(linebuf)-1:
                                        #divTag.append(Tag(soup, "br"))
                                        divTag.append("\r\n")
                                if VERBOSE >= 3:
                                    print "------ ==="
                                # clear things after use
                                YY = int(startyear)
                                MM = int(startmonth)
                                DD = int(startday)
                                hh = ''
                                mm = ''
                                ss = ''
                                apm = ''
                                sender = ''
                                linebuf[:] = []    
                            # process the current message
                            # try the more restrictive p2 matches which means a conversation
                            if p01.match(line) is not None:
                                # match (date time)
                                startbracket = line.find("(")
                                endbracket = line.find(")")
                                timestr = line[startbracket+1:endbracket]
                                [MMDDYY, hhmmss, apm] = timestr.split(" ")
                                [MM, DD, YY] = MMDDYY.split("/")
                                MM = int(MM)
                                DD = int(DD)
                                YY = int(YY)
                                [hh, mm, ss] = hhmmss.split(":")
                                hh = int(hh)
                                mm = int(mm)
                                ss = int(ss)
                                # massage hh
                                if apm == 'AM' and hh == 12:
                                    hh = 0
                                if apm == 'PM' and hh < 12:
                                    hh = hh + 12
                                if p11.match(line) is not None:
                                    if VERBOSE >= 3:
                                        print "------ Have sender info in the header."
                                    line = line[endbracket+2:]
                                    [sender, line] = line.split(":", 1)
                                else:       
                                    if VERBOSE >= 3:
                                        print "----- Have no sender info in the header"                         
                                    line = line[endbracket+2:]
                            elif p02.match(line) is not None:
                                # match (time)                          
                                startbracket = line.find("(")
                                endbracket = line.find(")")
                                timestr = line[startbracket+1:endbracket]
                                [hhmmss, apm] = timestr.split(" ")
                                [hh, mm, ss] = hhmmss.split(":")
                                hh = int(hh)
                                mm = int(mm)
                                ss = int(ss)
                                # massage hh
                                if apm == 'AM' and hh == 12:
                                    hh = 0
                                if apm == 'PM' and hh < 12:
                                    hh = hh + 12
                                if p12.match(line) is not None:
                                    if VERBOSE >= 3:
                                        print "------ Have sender info in the header."
                                    line = line[endbracket+2:]
                                    [sender, line] = line.split(":", 1)
                                else:  
                                    if VERBOSE >= 3:
                                        print "----- Have no sender info in the header"
                                    line = line[endbracket+2:]
                            # push the remaining part to linebuf    
                            linebuf.append(line)     
                    # remember to work on the final line as well
                    if len(linebuf) > 0:
                        # time to process the libbuf
                        #print YY, MM, DD, hh, mm, ss, apm, sender
                        tstamp = datetime(YY, MM, DD, hh, mm, ss)
                        tstampstr = tstamp.strftime('%Y-%m-%dT%H:%M:%S')+timezone
                        # If the sender doesn't include the email server info, add it back
                        if sender.strip() == username:
                            sender = account
                        if VERBOSE >= 3:
                            print "------ ****"
                            print "------ Message to be written:"
                            print "------ Time:" + tstampstr
                            print "------ Sender:" + sender
                            print "------ Message:" 
                            # formulate the time 
                            for l in linebuf:
                                print "------", l
                        # construct the XML message
                        messageTag = Tag(soup, "message")
                        if sender.strip() == '':
                            messageTag['sender'] = account
                        else:
                            messageTag['sender'] = sender
                        messageTag['time'] = tstampstr
                        if firsttstamp == '':
                            firsttstamp = tstampstr
                        lasttstamp = tstampstr
                        chatTag.append(messageTag)
                        divTag = Tag(soup, "div")
                        messageTag.append(divTag)
                        for i in range(len(linebuf)):
                            text = NavigableString(linebuf[i])
                            divTag.append(text)
                            if i < len(linebuf)-1:
                                #divTag.append(Tag(soup, "br"))
                                divTag.append("\r\n")
                        if VERBOSE >= 3: 
                            print "------ ==="
                        # clear things after use
                        YY = int(startyear)
                        MM = int(startmonth)
                        DD = int(startday)
                        hh = ''
                        mm = ''
                        ss = ''
                        apm = ''
                        sender = ''
                        linebuf[:] = []
               
                # Add WindowOpened and WindowClosed event
                # Use the time from the first and last message
                winopenEventTag = Tag(soup, "event")
                winopenEventTag['type'] = "WindowOpened"
                winopenEventTag['sender'] = account
                # force to be bigger of firsttstamp, starttstamp
                if firsttstamp < starttstamp:
                    winopenEventTag['time'] = starttstamp 
                else: 
                    winopenEventTag['time'] = firsttstamp 
                chatTag.insert(0, winopenEventTag)

                wincloseEventTag = Tag(soup, "event")
                wincloseEventTag['type'] = "WindowClosed"
                wincloseEventTag['sender'] = account
                # force to be bigger of firsttstamp, starttstamp
                if firsttstamp < starttstamp:
                    winopenEventTag['time'] = starttstamp 
                else: 
                    wincloseEventTag['time'] = lasttstamp 
                chatTag.append(wincloseEventTag)

                # write the soup to file
                # create the folder and file
                outdirpath = os.path.join(outdir, contact, chatfolder)
                if not os.path.exists(outdirpath):
                    os.makedirs(outdirpath)
                outfilepath = os.path.join(outdirpath, chatfile)
                # write to the file
                outf = open(outfilepath, "w")
                outf.write(soup.prettify(encoding='utf-8'))
                #outf.write(str(soup))
                outf.close()
                if VERBOSE >= 2:
                    print "---- Wrote output Adium log file", outfilepath
                
                        
                    
            

        

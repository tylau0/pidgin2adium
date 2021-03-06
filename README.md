# pidgin2adium
Convert Pidgin conversation log to Adium format with Python
* Author: Eddie Lau
* Released under GPL v3 license

# Usage
* Obtain a copy of your pidgin conversation log folder (See "Pidgin conversation log location" below on how to locate it on Windows). Also identify the location of the Adium conversation log.
* Put BeautifulSoup.py (from BeautifulSoup 3) and this file in the same folder. 
* Edit the user input parameters section and the Adium specific parameters section if needed. Then run "python pidgin2adium.py".
* You may choose to use options to override the parameters.
   python pidgin2adium.py --indir INDIR --outdir OUTDIR --username IMACCOUNTUSERNAME --domain IMACCOUNTDOMAIN --service IMSERVICEPROTOCOL

# Pidgin conversation log location:
* For Windows 2000/XP/Vista/7, entering %APPDATA% in your Windows Explorer address bar will take you to the right directory.
* Windows XP -- C:\Documents and Settings\USERNAME\Application Data\.
* Windows Vista/7 -- C:\Users\USERNAME\AppData\Roaming.
* Windows 98/ME -- C:\Windows\Profiles\username.
* The default can be overridden. 
* Details: https://developer.pidgin.im/wiki/Using%20Pidgin#Wherearemysettingsanddataincludinglogssaved

# Adium conversation log location
* Default: /Users/USERNAME/Library/Application Support/Adium 2.0/Users/USERNAME/Logs

# Developer info
## Pidgin conversation log directory structure
* Under .purple/logs/IMSERVICEPROTOCOL/IMACCOUNTUSERNAME@IMACCOUNTDOMAIN, there are a folder named THEOTHERUSERNAME@DOMAIN for each other account that the user talks to.
* Under that individual other account folder, there are multiple .txt files, each of which stores the messages of a conversation session.
* The name of the file is something like 2013-03-26.132208-0700PDT.txt.

## Adium conversation log directory structure
* Under Logs, you first see a set of folders named in the form IMSERVICEPROTOCOL.IMACCOUNTUSERNAME@IMACCOUNTDOMAIN.
* Under each of these folders, you should see multiple "THEOTHERUSERNAME@DOMAIN (TIMESTAMP).chatlog/THEOTHERUSERNAME@DOMAIN (TIMESTAMP).xml" files. Each one stores the messages of a conversation session.

## Pidgin log format:
* Messages starts from the 2nd line.
* The first line of a message starts with a timestamp embraced by (): (5/6/2015 12:13:14 AM) -- for msg date different from what is recorded in the filename); (2:05:59 PM) -- for msg date the same as the one recored in the filename 
* If the current line is a continuation of the message started in some previous line, it will not have the above time header. 
* After the timestamp, it has optional sender info before the next :. No sender info if the message is a status update: (2:05:59 PM) user@somedomain.com

## Adium log format:
* See the source code for sample log format.
* Sender and time as two attributes of the message tag.
* The formatting by the line breaks and spacings inside the message tag are accurately reproduced in the Adium conversation log viewer.
* The window open time shouldn't be earlier than the one stated in the log file name.
* The window close time shouldn't be earlier than any message timestamp.


from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import httplib2
from xml.dom import minidom
import pandas as pd
from io import StringIO
from datetime import datetime
import os.path
import git
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("SPLuser", help="Splunk account username")
parser.add_argument("SPLpass", help="Splunk account password")
parser.add_argument("--all", help="Run for all dashboards, no regard for update time. To turn on set to 1.")
args = parser.parse_args()
print(args.all)
if args.all == "1":
        print("All Flag turned on")
        AllFlag = 1
else:
        print("All Flag not turned on")
        AllFlag = 0 

baseurl = 'URL GOES HERE'
userName = args.SPLuser
password = args.SPLpass
#AllFlag = 0
Changed = 0

searchQuery = '| rest /servicesNS/-/-/data/ui/views | where LIKE(\'author\',"%@company.com") | where !LIKE(\'eai:acl.sharing\',"user") | table title,updated,eai:data,author'

# Authenticate with server.
# Disable SSL cert validation. Splunk certs are self-signed.
serverContent = httplib2.Http(disable_ssl_certificate_validation=True).request(baseurl + '/services/auth/login',
    'POST', headers={}, body=urllib.parse.urlencode({'username':userName, 'password':password}))[1]

sessionKey = minidom.parseString(serverContent).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue

# Remove leading and trailing whitespace from the search
searchQuery = searchQuery.strip()

# If the query doesn't already start with the 'search' operator or another
# generating command (e.g. "| inputcsv"), then prepend "search " to it.
if not (searchQuery.startswith('search') or searchQuery.startswith("|")):
    searchQuery = 'search ' + searchQuery
    
print(searchQuery)

# Run the search.
# Again, disable SSL cert validation.
splResults = StringIO(httplib2.Http(disable_ssl_certificate_validation=True).request(baseurl + '/services/search/v2/jobs/export','POST',
    headers={'Authorization': 'Splunk %s' % sessionKey},body=urllib.parse.urlencode({'search': searchQuery, 'output_mode':'csv'}))[1].decode('utf-8'))
#print(splResults)
df = pd.read_csv(splResults, sep=",")
#print(df.head())

for ind in df.index:
        if not AllFlag:
                if str(df['updated'][ind]).startswith(datetime.now().strftime("%Y-%m-%d")):
                        print(df['title'][ind], df['author'][ind])
                        Changed = 1
                        if os.path.exists("splunk-dashboard-backups/" +df['title'][ind]+".xml"):
                               print("Overwriting Existing File...")
                               with open("splunk-dashboard-backups/" +df['title'][ind]+".xml", "w") as text_file:
                                        text_file.write(df['eai:data'][ind])
                        else:
                               print("Making xml file...")
                               with open("splunk-dashboard-backups/" +df['title'][ind]+".xml", "w") as text_file:
                                        text_file.write(df['eai:data'][ind])
        else:
                        print("Making xml file...")
                        with open("splunk-dashboard-backups/" +df['title'][ind]+".xml", "w") as text_file:
                                text_file.write(df['eai:data'][ind])

# Pushing changes
if AllFlag:
        #repo = git.Repo('./splunk-dashboard-backups')
        #git = repo.git
        #git.checkout('master')
        #git.add('.')
        #git.commit('-m', 'Automated commit by SRE Splunk Dashboard back-up')
        #git.push()
        print("AllFlag enabled so pushing all files.")
else:
        if Changed:
                #repo = git.Repo('C:\Dev\web-platform')
                #git = repo.git
                #git.checkout('SRENG-3579-update-rwd-ips-for-prod-in-je')
                #git.add('.')
                #git.commit('-m', 'Automated commit by SRE Splunk Dashboard back-up')
                #git.push()
                print("Pushing changed dashboards to repo.")
        else:
                print("No Changes to commit.")

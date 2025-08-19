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
import requests

baseurl = 'URL GOES HERE'
app='APP NAME GOES HERE'
userName = 'XXXXX'
password = 'XXXXXX'
Alerts=["my_test_alert","my_test_alert2"]


searchQuery = '| rest /servicesNS/-/-/data/ui/views | where LIKE(\'author\',"%@company.com") | where !LIKE(\'eai:acl.sharing\',"user") | table title,updated,eai:data,author'

# Authenticate with server.
# Disable SSL cert validation. Splunk certs are self-signed.
serverContent = httplib2.Http(disable_ssl_certificate_validation=True).request(baseurl + '/services/auth/login',
    'POST', headers={}, body=urllib.parse.urlencode({'username':userName, 'password':password}))[1]

sessionKey = minidom.parseString(serverContent).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue


# Run the search.
# Again, disable SSL cert validation.
headers = {
    'Authorization': 'Splunk %s' % sessionKey,
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'disabled': '1',
}

for alert in Alerts:
    response = requests.post(
        '' + baseurl + '/servicesNS/nobody/' + app + '/saved/searches/' + alert,
        headers=headers,
        data=data,
    )
    #print(splResults)

    print(response)

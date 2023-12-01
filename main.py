import datetime
from email import header
from operator import index
from os import read, sep
from unittest import result, skip
from xml.etree.ElementTree import tostring
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import ConfigParser

env = 'DEVELOPMENT'
# env = 'PRODUCTION'

configur = ConfigParser()
configur.read('config.ini')

## Config ##
SENDER_EMAIL = configur.get(env,'sender_mail')
SENDER_PASSWORD = configur.get(env,'sender_pass')
SERVER = configur.get(env,'server')
RECEIVER_EMAIL = configur.get(env,'recevier_email')

path = 'File/'

url_csv = pd.read_csv(path+'bscscan_urls.csv')
bscscan_urls = pd.DataFrame()
bscscan_urls = url_csv['bscscan_urls']

for urls in bscscan_urls:
    array = []
    url = urls
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(url,headers=headers)

    soap = BeautifulSoup(r.content,'html5lib')
    main_table = soap.find('tbody')
    file_name = url.split('=')[1]  
    for table in main_table.find_all('tr'):
        tabl_data = pd.DataFrame()
        td = table.find_all('td')  
        txn_hash = td[1].find('span').text
        age_timestamp = td[2].find('span').text
        age_relative = td[3].find('span').text
        txn_from = ''
        if(td[4].find('a',attrs={'class':'hash-tag text-truncate'}) != None):
            txn_from = td[4].find('a',attrs={'class':'hash-tag text-truncate'}).text
        else:
            txn_from = td[4].find('span').text
        type_marker = td[5].find('span').text
        txn_to = ''
        if td[6].find('span') != None : 
            txn_to =  td[6].find('span').text
        else:
            if(td[6].find('a',attrs={'class':'hash-tag text-truncate'}) != None):
              txn_to = td[6].find('a',attrs={'class':'hash-tag text-truncate'}).text
        txn_value = td[7].text
        token = ''
        if(td[8].find('a') != None):
            token = td[8].find('a').text
        res = file_name+"|"+txn_hash+"|"+age_timestamp+"|"+age_relative+"|"+txn_from+"|"+type_marker+"|"+txn_to+"|"+txn_value+"|"+token
        array.append(res)
    res = pd.DataFrame(array,columns=['test'])
    split_data = res["test"].str.split("|")
    data = split_data.to_list()
    result = pd.DataFrame(data,columns=['file_name','txn_hash','age_timestamp','age_relative','txn_from','type_marker','txn_to','txn_value','token'])
    result['age_timestamp'] = pd.to_datetime(result['age_timestamp'])
    max_datetime = result['age_timestamp'].max()
    
    if not(os.path.exists(path+file_name+'.txt')):
      fw = open(path+file_name+'.txt','w')
      fw.writelines(str(max_datetime))
      fw.close()

    f = open(path+file_name+'.txt','r')
    read_content = f.readlines()
    f.close()
    file_store = read_content[0]
    last_mail_datetime = pd.to_datetime(file_store)
    result = result[(result['age_timestamp'] > last_mail_datetime)]
    
    result.to_csv('scraped_data.csv',index=False)
    
    fw = open(path+file_name+'.txt','w')
    fw.writelines(str(max_datetime))
    fw.close()

    SUBJECT = 'Tnx for '+file_name
    header_table = ''
    for head in result.head():
        header_table  = header_table +'<th>'+head+'</th>'
    row_data = ''
    for row in result.itertuples():
        row_data = row_data + "<tr>"
        row_data = row_data + "<td>"+getattr(row, "file_name")+"</td>"
        row_data = row_data + "<td>"+getattr(row, "txn_hash")+"</td>"
        row_data = row_data + "<td>"+str(getattr(row, "age_timestamp"))+"</td>"
        row_data = row_data + "<td>"+getattr(row, "age_relative")+"</td>"
        row_data = row_data + "<td>"+getattr(row, "txn_from")+"</td>"
        row_data = row_data + "<td>"+getattr(row, "type_marker")+"</td>"
        row_data = row_data + "<td>"+getattr(row, "txn_to")+"</td>"
        row_data = row_data + "<td>"+getattr(row, "txn_value")+"</td>"
        row_data = row_data + "<td>"+getattr(row, "token")+"</td>"
        row_data = row_data + "</tr>"


    HTML = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style type="text/css">
          table {
            background: white;
            border-radius:3px;
            border-collapse: collapse;
            height: auto;
            max-width: 900px;
            padding:5px;
            width: 100%;
            animation: float 5s infinite;
          }

          th {
            color:#D5DDE5;;
            background:#1b1e24;
            border-bottom: 4px solid #9ea7af;
            font-size:14px;
            font-weight: 300;
            padding:10px;
            text-align:center;
            vertical-align:middle;
          }

          tr {
            border-top: 1px solid #C1C3D1;
            border-bottom: 1px solid #C1C3D1;
            border-left: 1px solid #C1C3D1;
            color:#666B85;
            font-size:16px;
            font-weight:normal;
          }

          tr:hover td {
            background:#4E5066;
            color:#FFFFFF;
            border-top: 1px solid #22262e;
          }

          td {
            background:#FFFFFF;
            padding:10px;
            text-align:left;
            vertical-align:middle;
            font-weight:300;
            font-size:13px;
            border-right: 1px solid #C1C3D1;
          }
        </style>
      </head>
      <body>
        Dear Ronen,<br> <br>

        <table>
          <thead>
            <tr style="border: 1px solid #1b1e24;">
              """+header_table+"""
            </tr>
          </thead>
          <tbody>
            """+row_data+"""
          </tbody>
        </table>

        <br>
        For more assistance please contact our support team:
        <a href='mailto:''>''</a>.<br> <br>
        Thank you!
      </body>
    </html>
    """

    def _generate_message() -> MIMEMultipart:
        message = MIMEMultipart("alternative", None, [MIMEText(HTML, 'html')])
        message['Subject'] = SUBJECT
        message['From'] = SENDER_EMAIL
        message['To'] = ", ".join(RECEIVER_EMAIL)
        # message['Cc'] = CC_EMAIL
        return message


    def send_message():
        message = _generate_message()
        server = smtplib.SMTP(SERVER)
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL,message.as_string())
        server.quit()

    if result.size > 0:
      send_message()
print("Finished")
exit()
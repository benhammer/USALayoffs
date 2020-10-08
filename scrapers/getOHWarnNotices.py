from bs4 import BeautifulSoup
from lxml import html
import requests
import csv
import sys
import json

def getOHWarnNotices():

    #declare URL of notices
    noticeURL = ('https://jfs.ohio.gov/warn/current.stm')
    
    #use BS to format HTML
    page = requests.get(noticeURL, verify=False)
    tree = html.fromstring(page.content)
    soup = BeautifulSoup(page.content, 'html.parser')

    #find <td> tags in second table and insert contents into a csv
    tables = soup.find_all('table')
    noticeTable = tables[1]
    with open('warn-notices/oh.csv','w',newline='') as csvfile:
        noticewriter = csv.writer(csvfile, delimiter=',')
        header = ['company','effective_date','location','number_of_workers']
        noticewriter.writerow(header)
        col = 0
        cleanNotice = []
        for child in noticeTable.find_all('td'):
            noticeData = child.get_text()
            #company
            if col == 1:
                company = noticeData
            #effective_date
            if col == 4:
                date = noticeData
            #location
            if col == 2:
                city = noticeData[:noticeData.find("/")]
            #number_of_workers
            if col == 3:
                affected = noticeData                
            col += 1
            if col == 8:
                cleanNotice.append(company.strip())
                cleanNotice.append(date.strip())
                cleanNotice.append(city.strip() + ", OH")
                cleanNotice.append(affected.strip())
                noticewriter.writerow(cleanNotice)
                cleanNotice = []
                col = 0

getOHWarnNotices()


from bs4 import BeautifulSoup
from lxml import html
import requests
import csv
import sys
import json

def getMIWarnNotices():

    years = ['2020','2019','2018','2017']        
    months = ["December","November","October","September","August","July","June","May","April","March","February","January"]


    #get all text after stuff we don't need and sort it into csv
    with open('warn-notices/mi.csv','w',newline='') as csvfile:
        noticewriter = csv.writer(csvfile)
        header = ['company','effective_date','location','number_of_workers']
        noticewriter.writerow(header)
        for year in years:
            noticeURL = ('https://www.michigan.gov/leo/0,5863,7-336-94422_95539_64178_64179---y_'+year+',00.html')
            count = 0
            notice = []
            notices = []
            #use BS to format HTML
            page = requests.get(noticeURL)
            tree = html.fromstring(page.content)
            soup = BeautifulSoup(page.content, 'html.parser')

            #find start of notices
            for string in soup.stripped_strings:
                count += 1
                if count >= 165:
                    notices.append(string)
            count = 0

            #read notices
            for string in notices:
                if string in months:
                    month = string
                elif len(string) == 2:
                    date = month + ' ' + string + ', ' + year
                    company = notices[count+1]
                    notice.append(company)
                    
                elif "Layoff" in string or "Closure" in string:
                    incident_type = string[:string.find(' ')]
                    city = string[string.find(':')+2:string.find('Count')]
                    number_affected = string[string.find('d:')+3:]
                    notice.append(date)
                    notice.append(city + "MI")
                    notice.append(number_affected)
                    noticewriter.writerow(notice)
                    notice = []         
                count += 1

getMIWarnNotices()

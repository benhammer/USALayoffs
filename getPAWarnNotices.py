from bs4 import BeautifulSoup
from lxml import html
import requests
import csv
import sys
import json

def getPAWarnNotices():
    years = ["2020","2019","2018","2017"]
    months = ["December","November","October","September","August","July","June","May","April","March","February","January"]
    with open('warn-notices/pa.csv','w', newline='') as csvfile:
        noticewriter = csv.writer(csvfile)
        header = ['company','effective_date','location','number_of_workers']
        noticewriter.writerow(header)
        for year in years:
            for month in months:
                #declare URL of notices, for PA requires month and year
                noticeURL = ('https://www.dli.pa.gov/Individuals/Workforce-Development/warn/notices/Pages/'+month+'-'+year+'.aspx')
                
                #use BS to format HTML
                page = requests.get(noticeURL)
                tree = html.fromstring(page.content)
                soup = BeautifulSoup(page.content, 'html.parser')

                #find <td> tags and insert contents into a csv
                noticeTable = soup.table

                if noticeTable != None:

                    for child in noticeTable.find_all('td'):
                        notice = []
                        cleanNotice = []
                        #clean data inside of <td> and append to create each notice
                        for string in child.stripped_strings:
                            #remove *UPDATE*
                            if not "*" in string:
                                notice.append(string)
                        if notice != []:
                            name = notice[0]
                            cleanNotice.append(name)
                            line = 0
                            #clean data
                            for data in notice:
                                if "COUNTY" in data or "County" in data:
                                    cut = data.find(":")
                                    location = data[cut+1:]
                                    if location.strip() == "":
                                        location = notice[line + 1] 
                                if "AFFECTED" in data or "Affected" in data:
                                    cut = data.find(":")
                                    affected = data[cut+1:]
                                    if affected.strip() == "":
                                        affected = notice[line + 1]
                                if "DATE" in data or "date" in data or "Date" in data:
                                    cut = data.find(":")
                                    date = data[cut+1:]
                                    if date.strip() == "":
                                        date = notice[line +1]
                                line += 1
                            cleanNotice.append(date.strip())
                            cleanNotice.append(location.strip() + ", PA")
                            cleanNotice.append(affected.strip())       
                            noticewriter.writerow(cleanNotice)

getPAWarnNotices()

from bs4 import BeautifulSoup
from lxml import html
import requests
import csv
import sys
import json

def getWIWarnNotices():

    years = ["2020","2019","2018","2017"]    
    
    #create csv
    with open('warn-notices/wi.csv','w',newline='') as csvfile:
        noticewriter = csv.writer(csvfile, delimiter=',')
        for year in years:
            if year == "2020":
                noticeURL = ('https://sheets.googleapis.com/v4/spreadsheets/1cyZiHZcepBI7ShB3dMcRprUFRG24lbwEnEDRBMhAqsA/values/Originals?key=AIzaSyDP0OltIjcmRQ6-9TTmEVDZPIX6BSFcunw&callback=handler')                
                page = requests.get(noticeURL)
                tree = html.fromstring(page.content)
                soup = BeautifulSoup(page.content,'html.parser')

                #reassemble string into array the hard way
                for string in soup.stripped_strings:
                    arrayStart = string.find("[")
                    notices = string[arrayStart+1:len(string)-6]
                    noticesCSV = []
                    
                    #separate notices
                    while "[" in notices:
                        notice = notices[notices.find("[")+3:notices.find("]")]
                        notices = notices[notices.find("]")+3:]
                        arrayNotice = notice.split("\n")
                        #clean and sort
                        cleanArrayNotice = []
                        cleanNotice = []
                        e = 3
                        while e <= 11:
                            clean = arrayNotice[e]
                            clean = clean.strip()
                            clean = clean.strip(',')
                            clean = clean.strip('\"')
                            #format date
                            if e == 6 and clean != "NoticeRcvd":
                                clean = clean[4:6] + "/" + clean[6:8] + "/" + clean[:4]
                            cleanArrayNotice.append(clean)
                            e += 1

                        #fill csv
                        company = cleanArrayNotice[0]
                        effective_date = cleanArrayNotice[5]
                        location = cleanArrayNotice[1] + ', WI'
                        number_of_workers = cleanArrayNotice[2]

                        if company == 'Company':
                            company = 'company'
                        if effective_date == 'LayoffBeginDate':
                            effective_date = 'effective_date'
                        if location == 'City, WI':
                            location = 'location'
                        if number_of_workers == 'AffectedWorkers':
                            number_of_workers = 'number_of_workers'

                        cleanNotice.append(company)
                        cleanNotice.append(effective_date)
                        cleanNotice.append(location)
                        cleanNotice.append(number_of_workers)
                        cleanNotice.append(year)
                        noticewriter.writerow(cleanNotice)
            else:
                noticeURL = ('https://dwd.wisconsin.gov/dislocatedworker/warn/'+year+'/default.htm')
                page = requests.get(noticeURL)
                tree = html.fromstring(page.content)
                soup = BeautifulSoup(page.content,'html.parser')
                line = 0
                cleanNotice = []
                for table in soup.find_all('table'):
                    if not "ReasonForUpdate" in table.prettify():
                        for string in table.stripped_strings:
                            if "\n" in string:
                                string = string.replace('\n','')
                            #company
                            if line == 0 and not string == "Company":
                                cleanNotice.append(string)
                            #date
                            if line == 5 and not string == "Layoff Begin Date":
                                cleanNotice.append(string)
                            #location
                            if line == 1 and not string == "City":
                                cleanNotice.append(string)
                            #affected
                            if line == 2 and not string == "Affected Workers":
                                cleanNotice.append(string)
                            line += 1
                            if line == 9:
                                noticewriter.writerow(cleanNotice)
                                line = 0
                                cleanNotice = []
                    
                                

                            
                        

                
                       
                
getWIWarnNotices()
        

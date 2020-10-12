from bs4 import BeautifulSoup
from lxml import html
import requests
import csv
import sys
import json

def getOHWarnNotices():

    i = 1
    with open('warn-notices/az.csv','w', newline='') as csvfile:
        noticewriter = csv.writer(csvfile)
        header = ['company','effective_date','location','number_of_workers']
        noticewriter.writerow(header)
        #sift through list of notices
        while i < 276:

            notice_list_url = "https://www.azjobconnection.gov/ada/mn_warn_dsp.cfm?securitysys=on&start_row="+str(i)+"&max_rows=25&orderby=noticeDateSort%20DESC&choice=1"

            page = requests.get(notice_list_url)
            tree = html.fromstring(page.content)
            soup = BeautifulSoup(page.content, 'html.parser')


            notice_urls = soup.table
            c = 0
            for line in soup.find_all('tr'):
                if c > 3 and c< 29:
                    
                    clean_notice = []
                    for string in line.stripped_strings:
                        if '2017' in string or '2018' in string or '2019' in string or '2020' in string:
                            date = string
                    for url in line.find_all('a'):
                        notice_url = url.get('href')
                        if "id=" in notice_url:
                                
                            page = requests.get("https://www.azjobconnection.gov/ada/" + notice_url)
                            tree = html.fromstring(page.content)
                            soup = BeautifulSoup(page.content, 'html.parser')

                            notice = []
                            
                            for child in soup.find_all('td'):
                                for string in child.stripped_strings:
                                    if not "WARN Information" in string and not "WARN Listing Properties" in string:
                                        if not string in notice:
                                            notice.append(string)

                            company = notice[1]
                            location = notice[3]+' '+notice[5]+', '+notice[7]+' '+notice[9]
                            number_of_workers = notice[11]

                            clean_notice.append(company)
                            clean_notice.append(date)
                            clean_notice.append(location)
                            clean_notice.append(number_of_workers)
                            noticewriter.writerow(clean_notice)
                c += 1                             

            i += 25

getOHWarnNotices()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import re
import urllib.parse
import os
import sys
import datetime
import locale
locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

known_contests_filename = os.path.join(os.environ['HOME'], 'var/atcoder_notify/known_contests.txt')

def read_known_contests():
    if known_contests_filename and os.path.exists(known_contests_filename):
        with open(known_contests_filename) as f:
            return set(map(lambda x: x.strip(), f.readlines()))
    else:
        return set()

def write_known_contests(urls):
    if known_contests_filename:
        with open(known_contests_filename, 'w') as f:
            for url in urls:
                print(url, file=f)

r=requests.get("https://atcoder.jp/contests/")
soup=bs(r.text,"lxml")
#print(soup.body)

content = soup.body.find('div',id='main-div').find('div',id='main-container').find('div',class_='row')
content = content.find('div',class_='col-lg-9 col-md-8')
url_root  = "https://atcoder.jp"

upcoming_contests = content.find('div',id="contest-table-upcoming")
if upcoming_contests == None:#予定されたコンテストが無ければ、終了
    # print("予定されたコンテストはありません。")
    sys.exit()
upcoming_contests = upcoming_contests.find("div",class_ ="panel panel-default").find("tbody")
upcoming_contests = upcoming_contests.find_all("tr")
url_root  = "https://atcoder.jp"
import urllib.parse

def get_contest_info(upcoming_contests):#soupの一部を渡すと、(date,duration,name,link,grade,rated)のlistを返す。
    infos =[]
    for i in upcoming_contests:
        date = i.find("td",class_ = "text-center").find("a").text
        #print(date)
        duration = i.find_all("td")[2].text
        #print(duration)
        contest_color = str(i.find_all("td")[1].find("span")).split('"')[1]
        if 'red' in contest_color:
            grade = 'AGC-grade'
        elif 'orange' in contest_color:
            grade = 'ARC-grade'
        elif 'blue' in contest_color:
            grade = 'ABC-grade'
        else:
            grade = 'unrated'
        #print(grade)
        name = i.find_all("td")[1].find("a").text
        #print(name)
        link = i.find_all("td")[1].find("a").get("href")
        link = urllib.parse.urljoin(url_root,link)
        #print(link)
        rated = i.find_all("td")[3].text
        #print(rated)
        infos.append((date,duration,name,link,grade,rated))
    return infos

def info2post(info):
    date, duration, name, link, grade, rated = info
    start_datetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S%z')
    start_str = start_datetime.strftime('%Y-%m-%d(%a) %H:%M')
    duration_hours, duration_minutes = map(int,duration.split(':'))
    end_datetime = (start_datetime + datetime.timedelta(hours=duration_hours, minutes=duration_minutes))
    if start_datetime.date() == end_datetime.date():
        end_str = end_datetime.strftime('%H:%M')
    else:
        end_str = end_datetime.strftime('%Y-%m-%d(%a) %H:%M')
    date_line = '{}-{}'.format(start_str, end_str)
    rated_line = 'rated: {}'.format(rated.strip())

    # if re.match(r'^AtCoder (Beginner|Regular|Grand) Contest', name):
    #     display_name = name
    # else:
    #     display_name = '{} [{}]'.format(name, grade)

    post_message = '\n'.join([name, date_line, link, rated_line])
    return post_message

contest_info = get_contest_info(upcoming_contests)
known_contests = read_known_contests()
new_contest_info = list(filter(lambda info: not info[3] in known_contests, contest_info))
message = '\n######\n'.join([info2post(info) for info in new_contest_info])
write_known_contests([info[3] for info in contest_info])
print(message)

import re
import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbsparta

from apscheduler.schedulers.blocking import BlockingScheduler

def get_MelonChart():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.melon.com/chart/index.htm', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    MelonMusic = soup.select('#lst50')
    
    for music in MelonMusic:
        title = music.select_one('td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a')
        if title is not None:
            title = title.text
            rank = music.select_one('td:nth-child(2) > div > span.rank').text
            artist = music.select_one('td:nth-child(6) > div > div > div.ellipsis.rank02 > a').text
            img_url = music.select_one('#lst50 > td:nth-child(4) > div > a > img')['src']
            doc = {
                'title' : title,
                'rank' : rank,
                'artist' : artist,
                'img_url' : img_url
            }
            db.Melon_Chart.insert_one(doc)

def get_GenieChart():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.genie.co.kr/chart/top200?ditc=D&ymd=20200403&hh=23&rtm=N&pg=1', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    GenieChart = soup.select('#body-content > div.newest-list > div > table > tbody > tr')
    for music in GenieChart:
        title = music.select_one('td.info > a.title.ellipsis')
        REAL_TITLE = title.text
        if REAL_TITLE is not None:
            artist = music.select_one('td.info > a.artist.ellipsis').text
            rank = music.select_one('td.number').text
            img_url = music.select_one('td > a > img')['src']
            REAL_RANK = re.findall('\d+', rank.strip())[0]

            doc = {
                'title': REAL_TITLE,
                'artist': artist,
                'rank': REAL_RANK,
                'img_url': img_url
            }

        db.GenieChart.insert_one(doc)

def get_BillBoardChart():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.billboard.com/charts/hot-100', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
                                    
    BillBoardChart = soup.select('#charts > div > div.chart-list.container > ol > li')
    for music in BillBoardChart:
        title = music.select_one('button > span.chart-element__information > span.chart-element__information__song.text--truncate.color--primary').text
        if title is not None:
            rank = music.select_one('button > span.chart-element__rank.flex--column.flex--xy-center.flex--no-shrink > span.chart-element__rank__number').text
            artist = music.select_one('button > span.chart-element__information > span.chart-element__information__artist.text--truncate.color--secondary').text
            url = music.select_one('button > span.chart-element__image.flex--no-shrink')['style']
            
            doc = {
                'title' : title,
                'artist' : artist,
                'rank' : rank,
                
            }
        db.BillBoardChart.insert_one(doc)

def get_BugsChart():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://music.bugs.co.kr/chart/track/realtime/total?wl_ref=M_contents_03_01', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    BugsChart = soup.select('#CHARTrealtime > table > tbody > tr')
    
    for music in BugsChart:
        title = music.select_one('th > p > a')
        if title is not None:
            Realtitle = title.text
            rank = music.select_one('td > div > strong').text
            artist = music.select_one('td > p > a').text
            img_url = music.select_one('td > a > img')['src']
            doc = {
                'title' : Realtitle,
                'artist' : artist,
                'rank' : rank,
                'img_url': img_url
            }
            db.BugsChart.insert_one(doc)

scheduler = BlockingScheduler()
scheduler.add_job(get_MelonChart, 'interval', minutes=1)
scheduler.add_job(get_GenieChart, 'interval', minutes=1)
scheduler.add_job(get_BillBoardChart, 'interval', minutes=1)
scheduler.add_job(get_BugsChart, 'interval', minutes=1)

scheduler.start()

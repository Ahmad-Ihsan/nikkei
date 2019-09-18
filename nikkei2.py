# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 16:16:39 2019

@author: lenovo
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 12:45:56 2019

@author: lenovo
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import sqlite3
import MeCab
from selenium.webdriver.firefox.options import Options
import time
import logging

from sql.connect import DBConnection

import sys
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(message)s:%(asctime)s')
file_handler = logging.FileHandler('nikkei2.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

main_logger = logging.getLogger('main')
main_logger.setLevel(logging.INFO)
main_logger_format = logging.Formatter('%(message)s:%(asctime)s')
main_logger_handler = logging.FileHandler('MainLog.log')
main_logger_handler.setFormatter(main_logger_format)
main_logger.addHandler(main_logger_handler)

geckodriver = "/usr/local/bin/"
options = Options()
options.headless = True
driver = webdriver.Firefox(geckodriver, options=options)
db = DBConnection()
conn = db.connection()
c = conn.cursor()
mecab = MeCab.Tagger()

#News
art_id = []
art_ver = []
art_titles = []
art_subtitles = []
art_content = []
art_day = []
art_year = []
art_month = []
art_date = []
art_date_full = []
art_raw = []
art_category_id = []

#Media
art_media = []
art_media_type = []

#Categories
morning_categories = []
morning_categories_id = []
evening_categories = []
evening_categories_id = []
new_category = []
cat_ver = []

#Days
day_id = [1,2,3,4,5,6,7]
day_kanji = ['日','月','火','水','木','金','土']

#Dictionary
artikel = []
title_cleaned = []
subtitle_cleaned = []
content_cleaned = []

#Parser
word = []
furigana = []
word_type = []
row=dict()

baseURL = 'https://www.nikkei.com/paper/'

paper_version = {'M': 'morning', 'E': 'evening'}

def get_link(url):
    
    driver.get(url)
    time.sleep(15)
    try:
        username = driver.find_element_by_name("LA7010Form01:LA7010Email")
    except:
        logger.exception('FAILED Connection Too Slow')
    username.clear()
    username.send_keys("hmatsuhisa@aol.com")
    
    password = driver.find_element_by_name("LA7010Form01:LA7010Password")
    password.clear()
    password.send_keys("matsuhisa1380")
    
    
    login_attempt = driver.find_element_by_xpath("//*[@type='submit']")
    login_attempt.click()
    
    time.sleep(2)    
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    logger.info('Login Success')
    print('Login Success ')
    data = soup.find_all('div', attrs={'class': 'cmn-tree_set'})
    links = []
    
    for i in data:
        try:
            link = i.find('h4', {"class": "cmn-article_title"}).span.a['href']
        except Exception:
            link = None
        if link:
            links.append(link)
        try:
            link2 = i.find('h5', {"class": "cmn-article_title"}).span.a['href']
        except Exception:
            link2 = None
        if link2:        
            links.append(link2)
            
    v = soup.find('div', {'class':'kn-panel cmn-clearfix'})
    try:
        b = v.findAll('li')
    except:
        logger.exception('Failed Connection Too Slow')
    for i in range(len(b)):
        category = b[i].a.text
        new_category.append(category)
        
    if soup.find('li', {'class': re.compile('knc-here')})['class'][0].split('-')[1] == 'morning':
        ver = 'M'
        cat_ver.append(ver)
    elif soup.find('li', {'class': re.compile('knc-here')})['class'][0].split('-')[1] == 'evening':
        ver = 'E'
        cat_ver.append(ver)
    
    for i in range(len(new_category)):
        c.execute('insert or ignore into categories (category_name, version) values (?, ?)', (new_category[i], cat_ver[0]))
        conn.commit()
        
    catM = c.execute('select * from categories where version = "M"')
    for row in catM:
        morning_categories.append(row[1])
        morning_categories_id.append(row[0])
        
    catE = c.execute('select * from categories where version = "E"')
    for row in catE:
        evening_categories.append(row[1])
        evening_categories_id.append(row[0])
    
    print(f' {len(links)} links captured')
    logger.info(f' {len(links)} links captured')
    return(links)



def cleaner(container, string):
    words = []
    lines = mecab.parse(string).split('\n')
    for line in lines:
        items = re.split('[\t,]',line)
        words.append(items[0])
    a = ' '.join(words)    
    container.append(a[:-5])
    
    
    
def get_data(links):    
    for i in range(len(links)):
        if links[i] != 'javascript:void(0)':
            driver.get(f'https://www.nikkei.com{links[i]}')
            html = driver.page_source
            time.sleep(1)
            sp = BeautifulSoup(html, 'lxml')
            data = sp.find('div', class_=re.compile("cmn-section cmn-indent"))
            
            
            
#Article TITLE & SUBTITLE
            x = data.find('h1', {"class": "cmn-article_title cmn-clearfix"})
            y = x.find_all('span')
            try:
                title = y[0].text
                print(title)
                cleaner(title_cleaned, title)
            except Exception:
                title = None
            try:
                if y[1].text:
                    subtitle = y[1].text
                    cleaner(subtitle_cleaned, subtitle)
                else:
                    subtitle = None
                    cleaner(subtitle_cleaned, str(subtitle))
            except Exception:
                subtitle = 'None'
                cleaner(subtitle_cleaned, subtitle)
                
            
#Article TEXT CONTENT
            content = data.find_all('div', attrs={'class': 'cmn-article_text JSID_key_fonttxt m-streamer_medium'})
            p_temp = []
            cleaned_temp = []                                 
            for j in content:
                if j.find('p'):
                    p = j.find('p').text
                    cleaner(cleaned_temp, p)
                else:
                    p='None'
                    cleaner(cleaned_temp, p)
                if p:
                    p_temp.append(p)
                    
            content_cleaned.append(cleaned_temp)

            
#Article VERSION
            if sp.find('li', {'class': re.compile('knc-here')})['class'][0].split('-')[1] == 'morning':
                version = 'M'
            elif sp.find('li', {'class': re.compile('knc-here')})['class'][0].split('-')[1] == 'evening':
                version = 'E'
            
#Article DATE
            year = sp.find('li', {'class' : 'knc-morning'}).a['href'].split('=')[1][:4]
            month = sp.find('li', {'class' : 'knc-morning'}).a['href'].split('=')[1][4:6]
            date = sp.find('li', {'class' : 'knc-morning'}).a['href'].split('=')[1][6:8]
            date_full = f'{year}-{month}-{date}'
            day = sp.find('span', {'class': 'm-miM23_currentText'}).text.split('（')[1][0]
            for a in range(len(day_id)):
                if day == day_kanji[a]:
                    art_day_id = day_id[a] 
            
#Article ID
            ids = f'{year}{month}{date}{version}{i+1:0>4}'
            
            
#Artcle RAW
            raw = html
            
#Article CATEGORY
            category = sp.find('h3', {'class':'cmnc-title'}).text
            if version == 'M':
                for i in range(len(morning_categories)):
                    if category == morning_categories[i]:
                        category_id = morning_categories_id[i]
            elif version == 'E':
                for i in range(len(evening_categories)):
                    if category == evening_categories[i]:
                        category_id = evening_categories_id[i]                
                        
#Article MEDIA
            location = []
            img1 = data.find_all('div', {'style': 'cmnc-figure'})
            img2 = data.find_all('div', {'class': 'cmnc-figure'})
            if img1:
                for i in img1:
                    if i.a:
                        image = i.a.img['src']
                        tipe = 'Picture'
                        location.append(image)
                    else:
                        image = i.img['src']
                        tipe = 'Picture'
                        location.append(image)
            elif img2:
                for i in img2:
                    if i.a:
                        image = i.a.img['src']
                        tipe = 'Picture'
                        location.append(image)
                    else:
                        image = i.img['src']
                        tipe = 'Picture'
                        location.append(image)
            else:
                location = None
                tipe = None
            if location:
                location = str(location)
            else:
                location = None
                

##############################################################################################################    
            
            if ids:
                art_id.append(ids)
            if version:
                art_ver.append(version)
            if title:    
                art_titles.append(title)
            if p_temp:
                art_content.append(''.join(p_temp))            
            art_subtitles.append(subtitle)
            if year:
                art_year.append(year)
            if month:
                art_month.append(month)
            if date:
                art_date.append(date)
            if date_full:
                art_date_full.append(date_full)
            if day:
                art_day.append(art_day_id)
            if raw:
                art_raw.append(raw)
            if category_id:
                art_category_id.append(category_id)
            art_media.append(location)
            art_media_type.append(tipe)

            logger.info(f'Article fetched: date = {date_full}, version = {version}, id = {ids}')
        else:
            continue

###########################################################################################################

    for i in range(len(content_cleaned)):
        artikel.append([title_cleaned[i], subtitle_cleaned[i], ''.join(content_cleaned[i])])    
    
    for i in range(len(artikel)):
        artikel[i] = ' '.join(artikel[i])
        
    
###########################################################################################################    
    for i in range(len(artikel)):
        node = mecab.parse(artikel[i])
        node = node.split("\n")
        for i in node:
            feature = re.split('[\t,]',i)
            if len(feature) >= 2 and feature[1] in ('助詞', '記号'):
                continue
            if len(feature) >= 2 and feature[2] in ('数'):
                continue
            if len(feature) <= 8:
                continue
            if feature[0] == "EOS":
                break
            word.append(feature[0])
            furigana.append(feature[8])
            word_type.append(feature[1])
    
######################################################################################################    
    x=[]
    for i in range(len(artikel)):
        one = mecab.parse(artikel[i])
        x.append(one)
    temp = []
    for i in x:
        a=i.split('\n')
        temp.append(a)
    temp2=[]
    for i in temp:
        f=[]
        for j in i:
            if len(j)>1:
                b= re.split('[\t,]',j)
                if len(b) >= 2 and b[1] in ('助詞', '記号'):
                    continue
                if len(b) >= 2 and b[2] in ('数'):
                    continue
                if len(b) <= 8:
                    continue
                if b[0] == 'EOS':
                    break
                f.append(b[0])
        temp2.append(f)
        
    def word_count(str):
        counts = dict()    
        for word in str:
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        return counts

    temp3=[]
    for i in temp2:
        o = word_count(i)
        temp3.append(o)
        

    for i in range(len(art_id)):
        row[art_id[i]] = temp3[i]
        
    
    
    
######################################################################################################        
    
def main(argv):
    today = int(datetime.datetime.now().strftime("%Y%m%d"))
    urls = []
    #default
    if len(argv) == 0:
        yesterday = today - 1
        for code, ver in paper_version.items():
            urls.append(baseURL + ver + '/?b=' + str(yesterday) + '&d=0')
    #select date
    elif len(argv) == 1:
        if int(argv[0]) >= today:
            print('Cannot take data other than past 29 days')
        else:
            for code, ver in paper_version.items():
                urls.append(baseURL + ver + '/?b=' + argv[0] + '&d=0')
    #select date range
    elif len(argv) == 2:
        if int(argv[0]) >= today or int(argv[0]) < today-30 or int(argv[1]) >= today or int(argv[1]) < today-30:
            print('Cannot take data other than past 29 days')
        elif int(argv[0]) > int(argv[1]):
            print('Start date bigger than End date')
        else:
            for news_date in range(int(argv[0]), int(argv[1])):
                for code, ver in paper_version.items():
                    urls.append(baseURL + ver + '/?b=' + str(news_date) + '&d=0')
    else:
        print('Format is not correct')
    for url in urls:
        links = get_link(url)
    #    print(links)
        get_data(links)
        

        print('Insertnig to News, Media ....')
        logger.info('Insertnig to News, Media ....')
        for i in range(len(art_titles)):
            c.execute("insert or ignore into news (News_ID, Date_Full, Year, Month, Date, Day, Version, Title, Subtitle, Text_Content, Raw, Category) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (art_id[i], art_date_full[i], int(art_year[i]), int(art_month[i]), int(art_date[i]), int(art_day[i]), art_ver[i], art_titles[i], art_subtitles[i], str(art_content[i]), art_raw[i], art_category_id[i]))
            c.execute("insert or ignore into media (News_ID, location, type) values (?,?,?)", (art_id[i], art_media[i], art_media_type[i]))
            conn.commit()
        logger.info('Finished Insertnig to News, Media ....')
        print('Finished Insertnig to News, Media')


        print('Insertnig to Dictionary ....')
        logger.info('Insertnig to Dictionary ....')
        for i in range(len(word)):
            c.execute("insert or ignore into dictionary (japanese, furigana, word_type) values (?,?,?)", (word[i], furigana[i], word_type[i]))

            conn.commit()
        logger.info('Finished Insertnig to Dictionary')
        print('Finished Insertnig to Dictionary')

        a = c.execute('select word_id, japanese from dictionary')    

        name = []
        ids = []
        for i in a:
            ids.append(i[0])   
            name.append(i[1])

        print('Insertnig to Word_count ....')
        logger.info('Insertnig to Word_count')
        for key, value in row.items():
            a = key
            b = value
            for key, value in b.items():
                for i in range(len(name)):
                    if key == name[i]:
                        key = ids[i]
                c.execute('insert into word_count(word_id, news_id, count) values (?,?,?)', (key, a, value))
                conn.commit()
        print('Finished Insertnig to Word_count')
        logger.info('Finished Insertnig to Word_count')


        b = c.execute('select word_id, sum(count) from word_count group by word_id')
        ids = []
        count = []
        for i in b:
            ids.append(i[0])
            count.append(i[1])
            
        print('Updating Count Total ....')
        logger.info('Updating Count Total')
        for i in range(len(ids)):
            c.execute('UPDATE dictionary SET count_total = %d where word_id = %s' %(count[i], ids[i]))
            conn.commit()
        conn.close()
        print('Finished Updating Count Total')
        logger.info('Finished Updating Count Total')
        main_logger.warning(f'Articles from {art_date_full[0]} version {art_ver[0]} has been added to database @ ')


if __name__ == '__main__':    
    main('https://www.nikkei.com/paper/evening/?b=20190831&d=0')




































if __name__ == '__main__':
    main(sys.argv[1:])
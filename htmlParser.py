# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 03:06:50 2019

@author: lenovo
"""


from bs4 import BeautifulSoup
import re
import sqlite3
import MeCab
import codecs
import os
import logging

logger = logging.getLogger('html')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(message)s:%(asctime)s')
file_handler = logging.FileHandler('htmlParser.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

main_logger = logging.getLogger('main')
main_logger.setLevel(logging.INFO)
main_logger_format = logging.Formatter('%(message)s:%(asctime)s')
main_logger_handler = logging.FileHandler('MainLog.log')
main_logger_handler.setFormatter(main_logger_format)
main_logger.addHandler(main_logger_handler)

rootdir = '/home/ihsan/Nikkei/news/20190613朝刊'

conn = sqlite3.connect('/home/ihsan/nikkei/testdb2.db')
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
dic=dict()

            

def get_dirs(rootdir):
    directory = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if file == 'index.html':
                directory.append(os.path.join(subdir, file))
    
    return directory    

def cleaner(container, string):
    words = []
    lines = mecab.parse(string).split('\n')
    for line in lines:
        items = re.split('[\t,]',line)
        words.append(items[0])
    a = ' '.join(words)    
    container.append(a[:-5])
    
def get_data(dirs):    
    for i in range(len(dirs)):
        f=codecs.open(dirs[i], 'r')
        html = f.read()
        sp = BeautifulSoup(html, 'lxml')
        data = sp.find('div', class_=re.compile("cmn-section cmn-indent"))
        
        try:
            if sp.find('h3', {'class':'cmnc-title'}).text:
                cats = sp.find('h3', {'class':'cmnc-title'}).text
            else:
                continue
        except:
            continue
        
        if sp.find('li', {'class': re.compile('knc-here')})['class'][0].split('-')[1] == 'morning':
            cat_ver = 'M'
        elif sp.find('li', {'class': re.compile('knc-here')})['class'][0].split('-')[1] == 'evening':
            cat_ver = 'E'
        
        c.execute('insert or ignore into categories (category_name, version) values (?, ?)', (cats, cat_ver))
        conn.commit()
        
        catM = c.execute('select * from categories where version = "M"')
        for row in catM:
            morning_categories.append(row[1])
            morning_categories_id.append(row[0])
            
        catE = c.execute('select * from categories where version = "E"')
        for row in catE:
            evening_categories.append(row[1])
            evening_categories_id.append(row[0])
        
    #Article TITLE & SUBTITLE
        x = data.find('h1', {"class": "cmn-article_title cmn-clearfix"})
        y = x.find_all('span')
        try:
            title = y[0].text
            print(title)
            cleaner(title_cleaned, title)
        except Exception:
            title = None
            cleaner(title_cleaned, str(title))
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
            art_content.append(' '.join(p_temp))            
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

###########################################################################################################

    for i in range(len(content_cleaned)):
        artikel.append([title_cleaned[i], subtitle_cleaned[i], ' '.join(content_cleaned[i])])    
    
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
        dic[art_id[i]] = temp3[i]
        
def main(rootdir):
#    print(links)
    
    dirs = get_dirs(rootdir)
    get_data(dirs)
    
    print('Insertnig to News, Media ....')
    logger.info('Insertnig to News, Media ....')
    for i in range(len(art_titles)):
        c.execute("insert or ignore into news (News_ID, Date_Full, Year, Month, Date, Day, Version, Title, Subtitle, Text_Content, Raw, Category) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (art_id[i], art_date_full[i], int(art_year[i]), int(art_month[i]), int(art_date[i]), int(art_day[i]), art_ver[i], art_titles[i], art_subtitles[i], str(art_content[i]), art_raw[i], art_category_id[i]))
        c.execute("insert or ignore into media (News_ID, location, type) values (?,?,?)", (art_id[i], art_media[i], art_media_type[i]))
        conn.commit()
    logger.info('Finished inserting news, media')
    print('Finished inserting news, media')

    print('Insertnig to Dictionary ....')
    logger.info('Insertnig to Dictionary ....')
    for i in range(len(word)):
        c.execute("insert or ignore into dictionary (japanese, furigana, word_type) values (?,?,?)", (word[i], furigana[i], word_type[i]))
        conn.commit()
    logger.info('Finished inserting dictionary')
    print('Finished inserting dictionary')
    
    a = c.execute('select word_id, japanese from dictionary')    

    name = []
    ids = []
    for i in a:
        ids.append(i[0])   
        name.append(i[1])
    
    print('Insertnig to word_count ....')
    logger.info('Insertnig to word_count ....')
    for key, value in dic.items():
        a = key
        b = value
        for key, value in b.items():
            for i in range(len(name)):
                if key == name[i]:
                    key = ids[i]
            c.execute('insert or ignore into word_count(word_id, news_id, count) values (?,?,?)', (key, a, value))
            conn.commit()
    print('Finished Insertnig to word_count')
    logger.info('Finished Insertnig to word_count')

    b = c.execute('select word_id, sum(count) from word_count group by word_id')
    ids = []
    count = []
    for i in b:
        ids.append(i[0])
        count.append(i[1])

    print('Updating Count Total ....')
    logger.info('Updating Count Total ....')    
    for i in range(len(ids)):
        c.execute('UPDATE dictionary SET count_total = %d where word_id = %s' %(count[i], ids[i]))
        conn.commit()
        
    conn.close()
    logger.info(f'Finished Insertnig Artikel {art_date_full[0]}, version {art_ver[0]}')
    main_logger.warning(f'Articles from {art_date_full[0]} version {art_ver[0]} has been added to database @ ')



if __name__ == '__main__':    
    main(rootdir)

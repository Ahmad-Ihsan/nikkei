# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:05:40 2019

@author: lenovo
"""

from sql.connect import DBConnection

day_id = [1,2,3,4,5,6,7]
day_kanji = ['日','月','火','水','木','金','土']
day_english = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

db = DBConnection()
conn = db.connection()
c = conn.cursor()

#for i in range(len(morning_cat_id)):
#    c.execute("insert into categories (category_id, category_name, version) values(?, ?, ?)", (morning_cat_id[i], morning_categories[i], 'M'))
#    conn.commit()
#conn.close()

for i in range(len(day_id)):
    c.execute("insert into days (day_id, day_kanji, day_english) values(?, ?, ?)", (day_id[i], day_kanji[i], day_english[i]))
    conn.commit()
conn.close()
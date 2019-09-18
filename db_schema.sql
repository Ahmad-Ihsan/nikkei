CREATE TABLE days (day_id integer primary key, day_kanji text, day_english text);
CREATE TABLE categories (category_id integer primary key, category_name text, version text, unique(category_name, version));
CREATE TABLE news (News_ID text primary key unique, Date_Full text, Year integer, Month integer, Date integer, Day text, Version text, Title text, Subtitle text, Text_Content text, Raw text, Category integer, CONSTRAINT fk_categories FOREIGN KEY (Category) REFERENCES categories(category_id), CONSTRAINT fk_days FOREIGN Key (Day) REFERENCES days(day_id));
CREATE TABLE media(News_ID text, location text, type text, constraint fk_news foreign key (News_ID) references news(News_ID));
CREATE TABLE dictionary(word_id integer primary key, japanese text, furigana text, word_type text, count_total integer, unique(japanese));
CREATE TABLE word_count(word_id integer, news_id text, count integer, unique(word_id, news_id));

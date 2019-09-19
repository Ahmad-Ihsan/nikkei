/*delete from word_count;
delete from media;
delete from dictionary;
delete from news;*/

select count(*) from news;
select count(*) from dictionary;
select count(*) from word_count;

select news.News_ID, news.Date_Full, news.Version, news.Title from news 
where news.Date_Full like '201909%'
order by news.News_ID desc;

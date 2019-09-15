import subprocess
import glob
import os

root = "/home/ihsan/Nikkei/news/"
data_path = root + '/20130408朝刊/'

os.chdir(data_path)

for doc in glob.iglob("*.doc"):

    print(doc)
    subprocess.call(['soffice', '--headless', '--convert-to', 'docx', doc], shell = False) 

rootdir = '/home/ihsan/Nikkei/news/20190613朝刊'

conn = sqlite3.connect('/home/ihsan/nikkei/testdb2.db')

baseDir = '/home/ihsan/Nikkei/news/20130408朝刊' 



import logging
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


logger = setup_logger('htmlLog', 'htmlParser.log')

main_logger = setup_logger('main_logger', 'MainLog.log')
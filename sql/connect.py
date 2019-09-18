import sqlite3
import os

class DBConnection():
    def __init__(self):
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.conn = sqlite3.connect(my_path + '/../nikkei.sqlite3')

    def connection(self):
        return self.conn
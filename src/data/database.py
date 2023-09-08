import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import sqlite3
from os import path
import project_config as pc
from data import utils as du
from typing import Dict, List, Tuple

class Database:
    """ A basic class to represent airbnb database """
    def __init__(self, db_name: str=None) -> None:
        """ initializes a database object

        Args:
            db_name (str): name of the database
        """
        self.db_name = pc.DATABASE_PATH if not db_name else db_name
        self.connection = None
        self.cursor = None
    
    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def connect(self) -> None:
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = Database.dict_factory
        self.cursor = self.connection.cursor()
    
    def close(self) -> None:
        self.connection.close()
    
    def __execute(
        self, 
        query: str, 
        params: Dict=None
    ) -> None:
        if not self.connection:
            self.connect()

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return

    def executemany(
        self, 
        query: str, 
        params: List
    ) -> None:
        if not self.connection:
            self.connect()
        self.cursor.executemany(query, params)
        self.connection.commit()
        return
    
    def execute(
        self, 
        query: str, 
        params: Dict=None
    ) -> None:
        self.__execute(query, params)
        self.connection.commit()
        return
        
    def fetch_all(
        self, 
        query: str, 
        params: Dict=None
    ) -> List:
        self.__execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_many(
        self, 
        query: str, 
        params: Dict=None,
        size: int=1
    ) -> List:
        self.__execute(query, params)
        return self.cursor.fetchmany(size)

    def fetch_one(
        self, 
        query: str, 
        params: Dict=None
    ) -> Tuple:
        self.__execute(query, params)
        return self.cursor.fetchone()
    

def db_setup():
    """ sets up the initial database """
    if os.path.exists(pc.DATABASE_PATH):
        return

    if not path.exists(path.dirname(pc.DATABASE_PATH)):
        os.makedirs(path.dirname(pc.DATABASE_PATH))
    
    print('Setting up database for the first time...')

    db = Database()
    db.execute(f'CREATE TABLE IF NOT EXISTS listing ({du.LISTING_TABLE_SCHEMA})')
    db.close()


if __name__ == '__main__':
    db_setup()
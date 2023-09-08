import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import sqlite3
from os import path
import project_config as pc
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
    
    def connect(self) -> None:
        self.connection = sqlite3.connect(self.db_name)
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

    def execute(
        self, 
        query: str, 
        params: Dict=None
    ) -> None:
        self.__execute(query, params)
        self.connection.commit()
        
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
    db.execute('''
        CREATE TABLE IF NOT EXISTS listing (
            id INTEGER PRIMARY KEY,
            listing_url TEXT NOT NULL,
            room_type TEXT NOT NULL,
            neighbourhood_group_cleansed TEXT NOT NULL,
            neighbourhood_cleansed TEXT NOT NULL,
            bedrooms INTEGER NOT NULL,
            beds INTEGER,
            bathrooms_text TEXT,
            accommodates INTEGER,
            price REAL NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            property_type TEXT,
            description TEXT,
            neighborhood_overview TEXT,
            host_about TEXT
        )
    ''')
    db.close()


if __name__ == '__main__':
    db_setup()
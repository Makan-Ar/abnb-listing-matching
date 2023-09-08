import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from os import path
import pandas as pd
import urllib.request
import project_config as pc
from pydantic import BaseModel, AnyUrl
from typing import Union


NYC_LISTINGS_URL = 'http://data.insideairbnb.com/united-states/ny/new-york-city/2023-06-05/data/listings.csv.gz'
NYC_LISTING_LOCAL_PATH = path.join(pc.BASE_RAW_DATA_DIR, 'nyc_listings.csv.gz')

COLS_TO_KEEP = [
    'id',
    'listing_url',
    'room_type',
    'neighbourhood_group_cleansed',
    'neighbourhood_cleansed',
    'bedrooms',
    'beds',
    'bathrooms_text',
    'accommodates',
    'price',
    'latitude',
    'longitude',
    'property_type',
    'description',
    'neighborhood_overview',
    'host_about'
]

LISTING_TABLE_SCHEMA = ('''
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
    host_about TEXT,
    embedding BLOB,
    similar_listings BLOB
''')
                        
class ListingItem(BaseModel):
    id: int
    listing_url: AnyUrl
    room_type: str
    neighbourhood_group_cleansed: str
    neighbourhood_cleansed: str
    bedrooms: int
    beds: Union[int, None] = None
    bathrooms_text: Union[str, None] = None
    accommodates: Union[int, None] = None
    price: float
    latitude: float
    longitude: float
    property_type: Union[str, None] = None
    description: Union[str, None] = None
    neighborhood_overview: Union[str, None] = None
    host_about: Union[str, None] = None

def load_listings(listing_url: str) -> pd.DataFrame:
    """ loads listings from a url and returns a dataframe with the relevant columns
        performs basic cleaning on the data including removing $ and , from price.

    Args:
        listing_url (str): url to listings csv

    Returns:
        pd.DataFrame: dataframe with relevant columns
    """
    data_df = pd.read_csv(listing_url)
    data_df = data_df[COLS_TO_KEEP]

    data_df.price = data_df.price.str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

    # no room number means either a studio or a shared room
    data_df.bedrooms.fillna(0, inplace=True)
    data_df.bedrooms = data_df.bedrooms.astype('Int64')

    data_df.beds = data_df.beds.astype('Int64')
    data_df.accommodates = data_df.accommodates.astype('Int64')

    return data_df

def load_nyc_listings() -> pd.DataFrame:
    """ loads NYC listings from local copy or a url and returns a dataframe with the relevant columns """
    if not path.exists(pc.BASE_RAW_DATA_DIR):
        os.makedirs(pc.BASE_RAW_DATA_DIR)

    if not path.exists(NYC_LISTING_LOCAL_PATH):
        print('NYC listings not found locally. Downloading from the web...')
        urllib.request.urlretrieve(NYC_LISTINGS_URL, NYC_LISTING_LOCAL_PATH)
    return load_listings(NYC_LISTING_LOCAL_PATH)


if __name__ == '__main__':
    df = load_nyc_listings()

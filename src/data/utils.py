import os
import sys
from os import path
sys.path.append(os.path.abspath(path.join(os.getcwd(), os.pardir)))

import pandas as pd
import urllib.request
import project_config as pc

NYC_LISTINGS_URL = 'http://data.insideairbnb.com/united-states/ny/new-york-city/2023-06-05/data/listings.csv.gz'
NYC_LISTING_LOCAL_PATH = path.join(pc.BASE_RAW_DATA_DIR, 'nyc_listings.csv.gz')

COLS_TO_KEEP = [
    'id',
    'listing_url',
    'room_type',
    'neighbourhood_group_cleansed',
    'neighbourhood_cleansed',
    'bathrooms_text',
    'bedrooms',
    'beds',
    'accommodates',
    'price',
    'latitude',
    'longitude',
    'property_type',
    'description',
    'amenities',
    'neighborhood_overview',
    'host_about'
]

def load_listings(listing_url: str) -> pd.DataFrame:
    """ loads listings from a url and returns a dataframe with the relevant columns
        performs basic cleaning on the data including removing $ and , from price and splitting amenities into a list

    Args:
        listing_url (str): url to listings csv

    Returns:
        pd.DataFrame: dataframe with relevant columns
    """
    data_df = pd.read_csv(listing_url)
    data_df = data_df[COLS_TO_KEEP]

    data_df.price = data_df.price.str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
    data_df.amenities = data_df.amenities.str.replace('\[|\]', '', regex=True).str.replace('"', '', regex=False).str.split(',')
    data_df.amenities = data_df.amenities.apply(lambda x: [amenity.strip() for amenity in x])
    return data_df

def load_nyc_listings() -> pd.DataFrame:
    """ loads NYC listings from local copy or a url and returns a dataframe with the relevant columns """
    if not path.exists(NYC_LISTING_LOCAL_PATH):
        print('NYC listings not found locally. Downloading from the web...')
        urllib.request.urlretrieve(NYC_LISTINGS_URL, NYC_LISTING_LOCAL_PATH)
    return load_listings(NYC_LISTING_LOCAL_PATH)


if __name__ == '__main__':
    df = load_nyc_listings()
    # print(df.head())
    # print(df.info())

    from models.listing import Listing
    listing_dict = df.iloc[0].to_dict()
    for key in listing_dict:
        if not isinstance(listing_dict[key], list) and pd.isna(listing_dict[key]):
            listing_dict[key] = None

    print(listing_dict)
    listing = Listing(listing_dict.pop('id'), listing_dict)
    print(listing.get_info_summary())
    print(listing.get_full_host_description())
    listing.store()

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import pickle
import numpy as np
import pandas as pd
from os import path
from tqdm import tqdm
from data import utils as du
from database.db import Database, db_setup
from models.matching import ListingSimilarity
from models.listing_embedding import ListingEmbedder

def filter_by_price(df: pd.DataFrame) -> np.ndarray:
    """ filter by price abs(log10(price) - log10(reference_price)) <= self.MAX_LOG_PRICE_DIFF

    Args:
        df (pd.DataFrame): all data

    Returns:
        np.ndarray: boolean array of shape (n, n) where n is the number of listings
    """
    prices = df.price.to_numpy()
    prices[prices == 0] = 1
    log_prices = np.log10(prices)
    return np.abs(log_prices[:, None] - log_prices) <= ListingSimilarity.MAX_LOG_PRICE_DIFF


def filter_by_neighborhood(df: pd.DataFrame) -> np.ndarray:
    """ filter by neighborhood

    Args:
        df (pd.DataFrame): all data

    Returns:
        np.ndarray: boolean array of shape (n, n) where n is the number of listings
    """
    neighbourhoods = df.neighbourhood_cleansed.to_numpy()
    return neighbourhoods[:, None] != neighbourhoods


def apply_heuristic_filters(
    scores: np.ndarray, 
    df: pd.DataFrame
) -> np.ndarray:
    """ apply heuristic filters to the scores

    Args:
        scores (np.ndarray): cosine similarity scores of shape (n, n) where n is the number of listings
        df (pd.DataFrame): all data

    Returns:
        np.ndarray: filtered scores
    """
    scores *= filter_by_price(df)
    scores *= filter_by_neighborhood(df)
    scores[scores <= ListingSimilarity.MIN_COS_SIMILARITY] = 0
    return scores


def precompute_and_populate(
    device: str, 
    batch_size: int
) -> None:
    """ precomputes embeddings for all listings and populates the database from a dataframe

    Args:
        device (str): device for computing embeddings (cuda / cpu)
        batch_size (int): batch size for computing embeddings and populating the database
    """
    # load data
    df = du.load_nyc_listings()
    df = df.iloc[:1000]

    print('Compute all listings embeddings...')
    listing_embedder = ListingEmbedder(device=device)
    embeddings = listing_embedder.from_dataframe(df, batch_size)

    print('Find similar listings and apply heuristic filters...')
    cos_similarities = embeddings @ embeddings.T
    cos_similarities = apply_heuristic_filters(cos_similarities, df)
    top_n_similar = np.argsort(cos_similarities, axis=1)[:, -ListingSimilarity.TOP_N:]
    top_n_similar = top_n_similar[:, ::-1]

    # add embeddings to dataframe
    df['embedding'] = df.apply(lambda row: pickle.dumps(embeddings[row.name].tolist()), axis=1)
    df['similar_listings'] = df.apply(lambda row: pickle.dumps(df.iloc[top_n_similar[row.name]].id.tolist()), axis=1)
    
    # populate database
    db_setup()
    print('Populating database with listings and precomputed embeddings...')
    db = Database()
    for i in tqdm(range(0, df.shape[0], batch_size)):
        populate_db(df.iloc[i:i+batch_size], db)
    db.close()


def populate_db(
    df: pd.DataFrame, 
    db: Database
) -> None:
    """ populates the database with listings from the dataframe """
    listings = list(df.T.to_dict().values())
    for listing in listings:
        for key, val in listing.items():
            if pd.isna(val):
                listing[key] = None

    cols = list(listings[0].keys())
    db.executemany(f'INSERT INTO listing ({", ".join(cols)}) VALUES (:{", :".join(cols)});', listings)
    return

if __name__ == '__main__':
    precompute_and_populate(device='cuda:0', batch_size=250)
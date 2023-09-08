
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from models.listing import Listing
from typing import List

class ListingSimilarity:
    """ A class to represent a listing similarity model

        Note: this class is not implemented yet, since everything is precomputed for the toy project.

        Given a new listing this model will:
            1. retrieves all filtered listings from the database
            2. compute / retrieve the embedding of all listing
            3. computes the cosine similarity between the new listing and all filtered listings
            4. updates database with the new listing's similar listings
            5. returns the top N similar listings
    """
    MAX_LOG_PRICE_DIFF = 0.3
    MIN_COS_SIMILARITY = 0.9
    TOP_N = 10
    MIN_DISTANCE = 1.0  # in miles
    
    def _retrieve_filtered_listings(self, reference_listing: Listing) -> List[Listing]:
        # TODO: SQL query to retrieve filtered listings based on heuristic filters
        raise NotImplementedError

    def find_similar_listings(self, id: int) -> List[Listing]:
        # TODO: if similar_listings is not in the database 
        #   retrieve filtered listings, compute embeddings, compute cosine similarity, return top N
        raise NotImplementedError

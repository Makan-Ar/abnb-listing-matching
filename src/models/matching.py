
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import numpy as np
from os import path
from models.listing import Listing
import project_config as pc
from typing import List

class ListingSimilarity:
    MAX_LOG_PRICE_DIFF = 0.3
    MIN_COS_SIMILARITY = 0.9

    def __init__(
        self,
        cache: bool = False
    ) -> None:
        self.cache = cache
        self.listing_cache = {}
    
    def _get_listing_by_id(self, id: int) -> Listing:
        """ retrieves a listing by id

        Args:
            id (int): listing id

        Returns:
            Listing: listing object
        """
        if self.cache and id in self.listing_cache:
            return self.listing_cache[id]

        listing = Listing.retrieve(id)
        if self.cache:
            self.listing_cache[id] = listing
        return listing    

    def _retrieve_filtered_listings(self, reference_listing: Listing) -> List[Listing]:
        
        reference_log_cost = np.log10(reference_listing.properties['price'])

        def filter_by_cost(listing: Listing) -> bool:
            """ filter by cost abs(log10(price) - log10(reference_price)) <= self.MAX_LOG_PRICE_DIFF """
            cur_log_price = np.log10(listing.properties['price'])
            return np.abs(cur_log_price - reference_log_cost) <= self.MAX_LOG_PRICE_DIFF

        filters = [filter_by_cost]
        listing_ids = Listing.retrieve_all_ids()
        filtered_listing = []
        for id in listing_ids:
            listing = self._get_listing_by_id(id)
            is_match = True
            while is_match and filters:
                is_match = filters.pop()(listing)
            
            if is_match:
                filtered_listing.append(listing)
        
        return filtered_listing
            


    def find_similar_listings(self, listing: Listing) -> List[Listing]:
        pass

    



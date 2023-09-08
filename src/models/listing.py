import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import pickle
import project_config as pc
from data.database import Database
from data.utils import ListingItem
from typing import Dict, Any, Hashable, List

class Listing:
    """ A class to represent a listing on Airbnb
    """
    def __init__(
        self, 
        id: int,
        properties: Dict
    ) -> None:
        """ 
        initializes a listing object.
        `properties` must include the following keys:
            - `listing_url` (str)
            - `price` (float)
            - `latitude` (float)
            - `longitude` (float)
            - `room_type` (str)
            - `neighbourhood_group_cleansed` (str)
            - `neighbourhood_cleansed` (str)
            
        Args:
            id (int): listing id
            properties (Dict): dictionary of properties
        """
        assert properties.get('listing_url', None), '`listing_url` must be specified'
        assert properties.get('price', None), '`price` must be specified as a float'
        assert properties.get('latitude', None), '`latitude` must be specified'
        assert properties.get('longitude', None), '`longitude` must be specified'
        assert properties.get('room_type', None), '`room_type` must be specified'
        assert properties.get('neighbourhood_group_cleansed', None), '`neighbourhood_group_cleansed` must be specified'
        assert properties.get('neighbourhood_cleansed', None), '`neighbourhood_cleansed` must be specified'
    
        self.id = id
        self.properties = properties
    
    @staticmethod
    def __from_db_dict(db_dict: Dict) -> 'Listing':
        """ creates a listing object from a dict returned by the database

        Args:
            db_dict (Dict): dictionary returned by the database

        Returns:
            Listing: listing object
        """
        listing_id = db_dict.pop('id')
        db_dict['embedding'] = pickle.loads(db_dict['embedding'])
        db_dict['similar_listings'] = pickle.loads(db_dict['similar_listings'])
        return Listing(listing_id, db_dict)

    @staticmethod
    def retrieve_by_id(id: int, db: Database=None) -> 'Listing':
        """ retrieves a listing by id

        Args:
            id (int): listing id
            db (Database, optional): database object. If None, a new 
                connection will be opened. Defaults to None.

        Returns:
            Listing: listing object
        """
        if not db:
            db = Database()
        row = db.fetch_one('SELECT * FROM listing WHERE id = :id', {'id': id})
        if not db:
            db.close()
        
        if not row:
            return None
        
        return Listing.__from_db_dict(row)

    @staticmethod
    def retrieve_by_ids(ids: List[int], db: Database=None) -> List['Listing']:
        """ retrieves listings by ids

        Args:
            ids (List[int]): list of listing ids
            db (Database, optional): database object. If None, a new 
                connection will be opened. Defaults to None.

        Returns:
            List[Listing]: list of listing objects
        """
        if not db:
            db = Database()
        rows = db.fetch_all(f'SELECT * FROM listing WHERE id IN ({", ".join([str(id) for id in ids])})')
        if not db:
            db.close()
        
        if not rows:
            return []
        
        return [Listing.__from_db_dict(row) for row in rows]

    @staticmethod
    def retrieve_all(
        skip: int=0, 
        limit: int=10, 
        db: Database=None
    ) -> List['Listing']:
        """ retrieves all listings

        Args:
            skip (int, optional): number of listings to skip. Defaults to 0.
            limit (int, optional): number of listings to return. Defaults to 10.
            db (Database, optional): database object. If None, a new 
                connection will be opened. Defaults to None.

        Returns:
            List[Listing]: list of listing objects
        """
        if not db:
            db = Database()
        rows = db.fetch_all(f'SELECT * FROM listing LIMIT {limit} OFFSET {skip}')
        if not db:
            db.close()
        
        if not rows:
            return []
        
        return [Listing.__from_db_dict(row) for row in rows]

    def to_listing_item(self) -> ListingItem:
        """ converts the listing to a ListingItem

        Returns:
            ListingItem: ListingItem object
        """
        props = {}
        props.update(self.properties)
        props.pop('embedding')
        props.pop('similar_listings')
        return ListingItem(id=self.id, **props)

    def store(self, db: Database=None) -> None:
        """ stores in the db as a new record.

        Args:
            db (Database, optional): database object. If None, a new 
                connection will be opened. Defaults to None.
        """
        cols = ['id']
        vals = [str(self.id)]
        for prop in self.properties:
            cols.append(prop)
            vals.append(f':{prop}')

        if not db:
            db = Database()
        db.execute(f'INSERT INTO listing ({", ".join(cols)}) VALUES ({", ".join(vals)})', self.properties)

        if not db:
            db.close()
        return

if __name__ == '__main__':
    db = Database()
    listing = Listing.retrieve_by_id(5121, db)
    print(listing)
    print(listing.properties['similar_listings'])
    print(Listing.retrieve_by_ids(listing.properties['similar_listings'], db))
    db.close()
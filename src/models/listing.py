import os
import sys
from os import path
sys.path.append(os.path.abspath(path.join(os.getcwd(), os.pardir)))

import re
import json
import project_config as pc
from typing import Dict, Any, Hashable

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
            - `amenities` (list[str], optional)
            
        Args:
            id (int): listing id
            properties (Dict): dictionary of properties
        """
        assert 'listing_url' in properties, '`listing_url` must be specified'
        assert 'price' in properties and isinstance(properties['price'], float), '`price` must be specified as a float'
        assert 'latitude' in properties, '`latitude` must be specified'
        assert 'longitude' in properties, '`longitude` must be specified'
        assert 'room_type' in properties, '`room_type` must be specified'
        assert 'neighbourhood_group_cleansed' in properties, '`neighbourhood_group_cleansed` must be specified'
        assert 'neighbourhood_cleansed' in properties, '`neighbourhood_cleansed` must be specified'
        assert 'amenities' not in properties or isinstance(properties['amenities'], list), '`amenities` must be a list'
    
        self.id = id
        self.properties = properties
    
    def add_property(self, key: Hashable, value: Any) -> None:
        """ adds a property to the listing

        Args:
            key (Hashable): property key
            value (Any): property value
        """
        self.properties[key] = value
        return

    def get_info_summary(self) -> str:
        """ returns a summary of the listing in natural language.
            Information includes (if available) the type of listing, location, number of bedrooms, number of beds, 
                number of bathrooms, and price per night.

        Returns:
            str: summary of the listing
        """
        if 'info_summary' in self.properties:
            return self.properties['info_summary']

        summary = []
        if self.properties.get('room_type', None) and self.properties.get('neighbourhood_group_cleansed', None):
            type_and_loc = f'{self.properties["room_type"]} in {self.properties["neighbourhood_group_cleansed"]}'
        summary.append(type_and_loc)
        
        # bed and bath info
        bed_bath = ''
        if self.properties.get('bedrooms', None):
            n_bedrooms = int(self.properties['bedrooms'])
            bed_bath = f'{n_bedrooms} bedroom' + 's' if n_bedrooms > 1 else ''
        if self.properties.get('beds', None):
            n_beds = int(self.properties['beds'])
            bed_bath += ' with ' if bed_bath != '' else ''
            bed_bath += f'{n_beds} bed' + 's' if n_beds > 1 else ''
        if self.properties.get('bathrooms_text', None):
            bed_bath += ' and ' if bed_bath != '' else ''
            bed_bath += self.properties['bathrooms_text']
        summary.append(bed_bath)
        
        max_occupancy = ''
        if self.properties.get('accommodates', 0) > 0:
            max_occupancy = 'Accommodates 1 person'
            if self.properties["accommodates"] > 1:
                max_occupancy = f'Accommodates up to {self.properties["accommodates"]} people'            
        summary.append(max_occupancy)
        
        cost = f'Costs ${self.properties["price"]:.2f} per night'
        summary.append(cost)
        
        summary = [s for s in summary if s]
        summary = '. '.join(summary)

        self.add_property('info_summary', summary)
        return summary
    
    def get_full_host_description(self) -> str:
        """ returns a full description by the host in natural language.
            information includes (if available) host property type, hot description, 
                amenities, and neighborhood overview and host information.
        
        Returns:
            str: full description by the host
        """
        if 'full_host_description' in self.properties:
            return self.properties['full_host_description']
        
        summary = []

        def clean_html(txt):
            return re.sub('<.*?>', '', txt)
        
        if self.properties.get('property_type', None):
            property_type = f'This is a'
            property_type += 'n' if self.properties['property_type'][0].lower() in 'aeiou' else ''
            property_type += ' ' + self.properties['property_type'].lower()
            summary.append(property_type)

        if self.properties.get('description', None):
            summary.append(clean_html(self.properties['description']))
        
        if self.properties.get('amenities', None):
            amenities = 'Amenities include: ' + ', '.join(self.properties['amenities']).lower()
            summary.append(amenities)
        
        if self.properties.get('neighborhood_overview', None):
            neigh_overview = 'A little about the neighborhood. '
            neigh_overview += clean_html(self.properties['neighborhood_overview'])
            summary.append(neigh_overview)
        
        if self.properties.get('host_about', None):
            host_info = 'Host information: ' + clean_html(self.properties['host_about'])
            summary.append(host_info)
        
        summary = [s for s in summary if s]
        summary = '. '.join(summary)
        
        # remove extra spaces
        summary = summary.strip()
        summary = re.sub('\s+', ' ', summary)
        
        self.add_property('full_host_description', summary)
        return summary

    def store(self):
        """stores the listing as a json file in the database directory.
           excludes `full_host_description` and `info_summary` from the json file if they exist.
        """
        properties_to_exclue = ['full_host_description', 'info_summary']
        store_exclue = {pte: self.properties.pop(pte) for pte in properties_to_exclue if pte in self.properties}

        with open(path.join(pc.DATABASE_DIR, f'{self.id}.json'), 'w') as f:
            json.dump(self.properties, f)

        self.properties.update(store_exclue)
        return
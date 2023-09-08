import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import re
import numpy as np
import pandas as pd
from tqdm import tqdm
import project_config as pc
from typing import List

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel


class ListingEmbedder:
    """ A class to embed listings using BGE-large-en model from HuggingFace 
        (https://huggingface.co/BAAI/bge-large-en)

        Constructs 2 natural language summaries for each listing:
            1. info summary: a summary of the listing's information (e.g. room type, price, etc.)
            2. full host description: a full description by the host (e.g. property type, description, etc.)
        
        The embeddings are the weighted average of the embeddings of the two summaries.
    """

    INFO_SUM_COEF = 3
    FULL_HOST_DESC_COEF = 2
    def __init__(
        self, 
        device: str='cpu'
    ) -> None:
        self.device = device

        self.tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-large-en', cache_dir=pc.HUGGING_FACE_CACHE_DIR)
        self.model = AutoModel.from_pretrained('BAAI/bge-large-en', cache_dir=pc.HUGGING_FACE_CACHE_DIR).to(self.device)
        self.model.eval()

    def __embed(self, text: str) -> torch.Tensor:
        encoded_input = self.tokenizer(text, padding=True, truncation=True, return_tensors='pt').to(self.device)
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            # Perform cls pooling
            sentence_embeddings = model_output[0][:, 0]
        return sentence_embeddings

    @staticmethod
    def __weigted_average(
        embed_a: torch.Tensor,
        embed_b: torch.Tensor, 
        weight_a: torch.Tensor,
        weight_b: torch.Tensor
    ) -> torch.Tensor:
        """ returns a weighted average of two embeddings """
        return (embed_a * weight_a + embed_b * weight_b) / (weight_a + weight_b)

    def embed_listings(
        self, 
        info_summaries: List[str], 
        full_host_descriptions: List[str],
        batch_size: int=32,
        verbose: bool=True
    ) -> np.ndarray:
        """ returns a numpy array of embeddings for each listing

        Args:
            info_summaries (List[str]): list of info summaries for each listing
            full_host_descriptions (List[str]): list of full host descriptions for each listing
            batch_size (int, optional): batch size for inference. Defaults to 32.
            verbose (bool, optional): whether to show progress bar. Defaults to True.

        Returns:
            np.ndarray: numpy array of embeddings for each listing
        """
        embeddings = []
        for i in tqdm(range(0, len(info_summaries), batch_size), disable=not verbose):
            batch_info_sum = info_summaries[i:i+batch_size]
            batch_info_sum_embed = self.__embed(batch_info_sum)
            info_sum_weights = torch.ones((len(batch_info_sum), 1), device=self.device) * self.INFO_SUM_COEF

            # full host description can be empty. If so, set the weight to 0
            batch_host_desc = full_host_descriptions[i:i+batch_size]
            batch_host_desc_weigted_embed = self.__embed(full_host_descriptions[i:i+batch_size])
            host_desc_mask = torch.tensor([1 if desc != '' else 0 for desc in batch_host_desc], device=self.device)
            host_desc_weights = host_desc_mask[:, None] * self.FULL_HOST_DESC_COEF

            avg_embed = self.__weigted_average(
                batch_info_sum_embed, 
                batch_host_desc_weigted_embed, 
                info_sum_weights, 
                host_desc_weights
            )

            avg_embed = F.normalize(avg_embed, p=2, dim=1)
            embeddings.append(avg_embed.detach().cpu().numpy())
        embeddings = np.concatenate(embeddings)
        return embeddings

    @staticmethod
    def construct_info_summary(
        room_type: str,
        neighbourhood_group_cleansed: str,
        price: float,
        bedrooms: int,
        beds: int=None,
        bathrooms_text: str=None,
        accommodates: int=None,
    ) -> str:
        """ returns a summary of the listing in natural language.

        Args:
            room_type (str): listing room type
            neighbourhood_group_cleansed (str): listing neighbourhood group
            price (float): listing price
            bedrooms (int): listing's number of bedrooms. Defaults to None.
            beds (int, optional): listing's number of beds. Defaults to None.
            bathrooms_text (str, optional): listing's number of bathrooms. Defaults to None.
            accommodates (int, optional): number of people the listing can accomodate. Defaults to None.

        Returns:
            str: summary of the listing in natural language
        """
        summary = []
        type_and_loc = f'{room_type} in {neighbourhood_group_cleansed}'
        summary.append(type_and_loc)
        
        # bed and bath info
        bed_bath = ''
        if bedrooms == 0 and room_type == 'Entire home/apt':
            bed_bath = 'A studio'
        elif bedrooms > 0:
            bed_bath = f'{bedrooms} bedroom{"s" if bedrooms > 1 else ""}'
        if beds is not None and beds > 0:
            bed_bath += ' with ' if bed_bath != '' else ''
            bed_bath += f'{beds} bed{"s" if beds > 1 else ""}'
        if bathrooms_text:
            bed_bath += ' and ' if bed_bath != '' else ''
            bed_bath += bathrooms_text
        summary.append(bed_bath)
        
        max_occupancy = ''
        if accommodates > 0:
            max_occupancy = 'Accommodates 1 person'
            if accommodates > 1:
                max_occupancy = f'Accommodates up to {accommodates} people'            
        summary.append(max_occupancy)
        
        cost = f'Costs ${price:.2f} per night'
        summary.append(cost)
        
        summary = [s for s in summary if s]
        summary = '. '.join(summary)
        return summary
    
    @staticmethod
    def construct_full_host_description(
        property_type: str=None,
        description: str=None,
        neighborhood_overview: str=None,
        host_about: str=None
    ) -> str:
        """ returns a full description by the host in natural language.
            information includes (if available) host property type, hot description, 
                and neighborhood overview and host information.
        
        Returns:
            str: full description by the host
        """
        summary = []

        def clean_html(txt):
            return re.sub('<.*?>', '', txt)
        
        if property_type:
            property_type = f'This is a{"n" if property_type[0].lower() in "aeiou" else ""}'
            property_type += ' ' + property_type.lower()
            summary.append(property_type)

        if description:
            summary.append(clean_html(description))
        
        if neighborhood_overview:
            neigh_overview = 'A little about the neighborhood. '
            neigh_overview += clean_html(neighborhood_overview)
            summary.append(neigh_overview)
        
        if host_about:
            host_info = 'Host information: ' + clean_html(host_about)
            summary.append(host_info)
        
        summary = [s for s in summary if s]
        summary = '. '.join(summary)
        
        # remove extra spaces
        summary = summary.strip()
        summary = re.sub('\s+', ' ', summary)
        return summary

    def from_dataframe(
        self, 
        df: pd.DataFrame, 
        batch_size: int=32
    ) -> np.ndarray:
        """ returns a numpy array of embeddings for each listing in the dataframe

        Args:
            df (pd.DataFrame): dataframe of listings
            batch_size (int, optional): batch size for inference. Defaults to 32.

        Returns:
            np.ndarray: numpy array of embeddings for each listing in the dataframe
        """
        embeddings = []
        full_summary, host_desc = [], []
        for _, row in df.iterrows():
            full_summary.append(self.construct_info_summary(
                room_type=row.room_type,
                neighbourhood_group_cleansed=row.neighbourhood_group_cleansed,
                price=row.price,
                bedrooms=None if pd.isna(row.bedrooms) else row.bedrooms,
                beds=None if pd.isna(row.beds) else row.beds,
                bathrooms_text=None if pd.isna(row.bathrooms_text) else row.bathrooms_text,
                accommodates=None if pd.isna(row.accommodates) else row.accommodates,
            ))
            
            host_desc.append(self.construct_full_host_description(
                property_type=None if pd.isna(row.property_type) else row.property_type,
                description=None if pd.isna(row.description) else row.description,
                neighborhood_overview=None if pd.isna(row.neighborhood_overview) else row.neighborhood_overview,
                host_about=None if pd.isna(row.host_about) else row.host_about,
            ))

        embeddings = self.embed_listings(
            full_summary, 
            host_desc, 
            batch_size=batch_size,
            verbose=True
        )
        return embeddings
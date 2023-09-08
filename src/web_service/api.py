import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import project_config as pc
from pydantic import BaseModel
from data.database import Database
from models.listing import Listing
from data.utils import ListingItem
from typing_extensions import Annotated
from typing import Dict, Any, Union, List
from fastapi import FastAPI, HTTPException, status, Path, Query


app = FastAPI()
db = Database()

@app.get("/listings", status_code=status.HTTP_200_OK)
async def get_listings(
    skip: Annotated[int, Query(title="Number of listings to skip", ge=0)] = 0, 
    limit: Annotated[int, Query(title="Number of listings to fetch", ge=1)] = 10
) -> List[ListingItem]:
    """ retrieves all listings

    Args:
        skip (int, optional): number of listings to skip. Defaults to 0.
        limit (int, optional): number of listings to return. Defaults to 10.

    Raises:
        HTTPException: 400 limit must be less than or equal to 100

    Returns:
        List[ListingItem]: list of listings
    """
    if limit > 100:
        raise HTTPException(status_code=400, detail="limit must be less than or equal to 100")

    listings = Listing.retrieve_all(skip, limit, db)
    return [listing.to_listing_item() for listing in listings]


@app.get("/listings/{listing_id}", status_code=status.HTTP_200_OK)
async def get_listing(
    listing_id: Annotated[int, Path(title="The ID of the item to get", ge=0)]
) -> ListingItem:
    """ retrieves a listing by ID

    Args:
        listing_id (int): ID of the listing to retrieve

    Raises:
        HTTPException: 404 if listing not found

    Returns:
        ListingItem: listing item
    """
    listing = Listing.retrieve_by_id(listing_id, db)

    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    return listing.to_listing_item()


@app.get("/listings/{listing_id}/similar", status_code=status.HTTP_200_OK)
async def get_similar_listings(
    listing_id: Annotated[int, Path(title="The ID of the item to get", ge=0)]
) -> List[ListingItem]:
    """ retrieves similar listings by ID

    Args:
        listing_id (int): ID of the listing to retrieve similar listings for

    Raises:
        HTTPException: 404 if listing not found

    Returns:
        List[ListingItem]: List of similar listings
    """
    listing = Listing.retrieve_by_id(listing_id, db)

    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    similar_listings = Listing.retrieve_by_ids(listing.properties['similar_listings'], db)
    
    return [listing.to_listing_item() for listing in similar_listings]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=pc.ENV_VARS['API_PORT'])
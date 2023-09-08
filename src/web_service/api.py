import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import project_config as pc
from pydantic import BaseModel
from database.db import Database
from models.listing import Listing
from data.utils import ListingItem
from typing_extensions import Annotated
from typing import Dict, Any, Union, List
from fastapi import FastAPI, HTTPException, status, Path


app = FastAPI()
db = Database()


@app.get("/listings/{listing_id}", status_code=status.HTTP_200_OK)
async def get_listing(
    listing_id: Annotated[int, Path(title="The ID of the item to get", ge=1)]
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
    listing_id: Annotated[int, Path(title="The ID of the item to get", ge=1)]
) -> List[ListingItem]:
    listing = Listing.retrieve_by_id(listing_id, db)

    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    similar_listings = Listing.retrieve_by_ids(listing.properties['similar_listings'], db)
    return [listing.to_listing_item() for listing in similar_listings]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=pc.ENV_VARS['API_PORT'])
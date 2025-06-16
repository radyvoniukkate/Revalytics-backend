from fastapi import APIRouter
from database import listings_collection

router = APIRouter()

@router.get("/listings")
def get_listings():
    listings = list(listings_collection.find({}, {"_id": 0}))
    return listings

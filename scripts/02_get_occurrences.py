import requests
import pandas as pd
import time

def fetch_all(scientific_name="Leopardus tigrinus", page_size=300):
    """Pages through the GBIF API until every georeferenced record is collected."""
    records = []
    offset = 0
    while True:
        params = {
            "scientificName": scientific_name,
            "hasCoordinate": "true",
            "limit": page_size,
            "offset": offset,
        }
        r = requests.get("https://api.gbif.org/v1/occurrence/search", params=params, timeout=30)
        r.raise_for_status()   # stops with a clear error if the request failed
        payload = r.json()
        batch = payload["results"]
        records.extend(batch)
        print(f"  fetched {len(records)} of {payload['count']} records so far...")
        if payload["endOfRecords"] or len(batch) == 0:
            break
        offset += page_size
        time.sleep(0.5)   # be polite to the free public API
    return records

print("Downloading Leopardus tigrinus occurrence records from GBIF...")
raw_records = fetch_all()

df = pd.DataFrame([{
    "gbif_id": rec.get("key"),
    "lat": rec.get("decimalLatitude"),
    "lon": rec.get("decimalLongitude"),
    "country": rec.get("country"),
    "year": rec.get("year"),
    "institution": rec.get("institutionCode"),
    "basis": rec.get("basisOfRecord"),
} for rec in raw_records])

# Drop exact duplicate coordinates -- the same specimen sometimes appears
# more than once in GBIF's aggregated sources
before = len(df)
df = df.drop_duplicates(subset=["lat", "lon"])
print(f"Kept {len(df)} of {before} records after removing exact duplicates")

df.to_csv("data/raw/tigrinus_occurrences.csv", index=False)
print("Saved data/raw/tigrinus_occurrences.csv")
print("This file has exact coordinates and lives in data/raw/, which is gitignored -- it will NEVER be committed.")
print(df["country"].value_counts())
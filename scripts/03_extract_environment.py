import ee, geemap
import pandas as pd
import json

ee.Initialize(project="yungas-cloud-forest-watch")

# 1. Reload the Yungas boundary saved in Step 2
with open("data/yungas_ecoregion.geojson") as f:
    yungas_geojson = json.load(f)
yungas_fc = ee.FeatureCollection(yungas_geojson)
yungas_geom = yungas_fc.geometry()

# 2. Generate 1000 random background points inside the Yungas boundary
background_pts = ee.FeatureCollection.randomPoints(region=yungas_geom, points=1000, seed=42)

# 3. Load occurrence points and convert to Earth Engine collection
occ_df = pd.read_csv("data/raw/tigrinus_occurrences.csv").dropna(subset=["lat", "lon"]).fillna("")
occ_fc = geemap.pandas_to_ee(occ_df, latitude="lat", longitude="lon")

# 4. Create 3-band environmental stack (elevation, temp, precip)
dem = ee.ImageCollection("COPERNICUS/DEM/GLO30_2024_1").select("DEM").mosaic().rename("elevation")
clim = ee.Image("WORLDCLIM/V1/BIO")
temp = clim.select("bio01").divide(10).rename("temp_c")     # stored as degC x 10
precip = clim.select("bio12").rename("precip_mm")
env_stack = dem.addBands(temp).addBands(precip)

# 5. Extract environmental values at all points
occ_env = env_stack.sampleRegions(collection=occ_fc, scale=1000, geometries=True)
bg_env = env_stack.sampleRegions(collection=background_pts, scale=1000, geometries=True)

# 6. Convert features to DataFrames and combine
occ_features = occ_env.getInfo()["features"]
occ_env_df = pd.DataFrame([f["properties"] for f in occ_features])
occ_env_df["group"] = "occurrence"

bg_features = bg_env.getInfo()["features"]
bg_env_df = pd.DataFrame([f["properties"] for f in bg_features])
bg_env_df["group"] = "background"

combined = pd.concat([occ_env_df, bg_env_df], ignore_index=True)
before = len(combined)
combined = combined.dropna(subset=["elevation", "temp_c", "precip_mm"])
print(f"Kept {len(combined)} of {before} rows with complete environmental data")

combined.to_csv("outputs/pca_env.csv", index=False)
print("Saved outputs/pca_env.csv")
print(combined.groupby("group").size())
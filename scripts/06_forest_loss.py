import ee
import json
import pandas as pd

ee.Initialize(project="yungas-cloud-forest-watch")

# 1. Load the belt boundary
with open("data/yungas_ecoregion.geojson") as f:
    yungas_geojson = json.load(f)
belt_fc = ee.FeatureCollection(yungas_geojson)
belt_geom = belt_fc.geometry()
belt_mask_image = ee.Image.constant(1).clip(belt_geom)

# 2. Load Hansen Global Forest Change dataset v1.13 (through 2025)
gfc = ee.Image("UMD/hansen/global_forest_change_2025_v1_13")

loss = gfc.select("loss")                     # 1 = tree cover lost 2001-2025
loss_year = gfc.select("lossyear")              # 1-25 (21 = 2021, 25 = 2025)
treecover_2000 = gfc.select("treecover2000")   # % tree cover in 2000

# Forest baseline: >= 30% tree cover in 2000
forest_2000 = treecover_2000.gte(30)

# Loss occurring specifically between 2021 and 2025 within baseline forest
recent_loss = (
    loss.eq(1)
    .And(loss_year.gte(21))
    .And(loss_year.lte(25))
    .And(forest_2000)
    .rename("recent_loss")
    .toFloat()
)

# Set default projection to prevent reduceResolution projection errors
recent_loss = recent_loss.setDefaultProjection(crs="EPSG:4326", scale=30)

# 3. Coarsen to 1km resolution (fraction of 1km cell cleared)
loss_fraction_1km = (
    recent_loss
    .reduceResolution(reducer=ee.Reducer.mean(), maxPixels=65536)
    .reproject(crs="EPSG:4326", scale=1000)
    .updateMask(belt_mask_image)
    .rename("loss_fraction")
)

# 4. Attach explicit coordinate bands for clean 1km grid merging
coords = ee.Image.pixelLonLat()
loss_fraction_1km = loss_fraction_1km.addBands(coords.select(["longitude", "latitude"], ["lon", "lat"]))

# 5. Sample at 1km grid pixel centers without heavy geometries
grid_sample = loss_fraction_1km.sample(
    region=belt_geom,
    scale=1000,
    geometries=False,
    dropNulls=True,
    tileScale=16
)

# 6. Stream directly into Pandas via GEE URL (bypassing 5,000 element limit)
print("Downloading updated 2021-2025 forest loss grid from Earth Engine...")
download_url = grid_sample.getDownloadURL(filetype="csv")
df = pd.read_csv(download_url)

if "system:index" in df.columns:
    df = df.drop(columns=["system:index"])

df.to_csv("outputs/forest_loss_grid.csv", index=False)
print(df["loss_fraction"].describe())
print("Saved outputs/forest_loss_grid.csv")
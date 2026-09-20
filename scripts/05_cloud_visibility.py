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

# 2. Build clear/not-clear mask for Sentinel-2
def add_clear_band(img):
    scl = img.select("SCL")
    is_clear = scl.eq(4).Or(scl.eq(5))  # 4 = vegetation, 5 = bare soil
    return img.addBands(is_clear.rename("clear").toFloat())

# 3. Load Sentinel-2 surface reflectance, 2021-01-01 to 2025-12-31
s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(belt_geom)
    .filterDate("2021-01-01", "2026-01-01")
    .map(add_clear_band)
)

print("Number of Sentinel-2 images found:", s2.size().getInfo())

# 4. Average clear band and clip to study area
clear_fraction = (
    s2.select("clear")
    .mean()
    .rename("clear_fraction")
    .clip(belt_geom)
)

# 5. Reproject to 1km grid resolution
clear_fraction_1km = clear_fraction.reproject(crs="EPSG:4326", scale=1000)

# 6. Restrict to belt mask and attach explicit coordinate bands
coords = ee.Image.pixelLonLat()
clear_fraction_1km = (
    clear_fraction_1km
    .updateMask(belt_mask_image)
    .addBands(coords.select(["longitude", "latitude"], ["lon", "lat"]))
)

# 7. Sample 1km pixel values without heavy geometries
grid_sample = clear_fraction_1km.sample(
    region=belt_geom,
    scale=1000,
    geometries=False,
    dropNulls=True,
    tileScale=16
)

# 8. Download directly via GEE URL to bypass .getInfo() 5000-element limit
print("Downloading grid data from Earth Engine...")
download_url = grid_sample.getDownloadURL(filetype="csv")
df = pd.read_csv(download_url)

if "system:index" in df.columns:
    df = df.drop(columns=["system:index"])

df.to_csv("outputs/cloud_visibility_grid.csv", index=False)
print(df["clear_fraction"].describe())
print("Saved outputs/cloud_visibility_grid.csv")
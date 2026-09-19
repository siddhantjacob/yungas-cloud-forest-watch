import ee

ee.Initialize(project="yungas-cloud-forest-watch")  # <-- replace with your own

# 1. The ecoregion outline -- this is the region we sample background points from
ecoregions = ee.FeatureCollection("RESOLVE/ECOREGIONS/2017")
yungas = ecoregions.filter(ee.Filter.eq("ECO_NAME", "Bolivian Yungas"))

print("Number of matching ecoregion features:", yungas.size().getInfo())
# This should print 1. If it prints 0, the exact name has changed -- run the
# line below to see nearby names and fix the filter above:
# names = ecoregions.filterBounds(ee.Geometry.Point([-67.6, -16.2])).aggregate_array("ECO_NAME").getInfo()
# print(names)

yungas_geom = yungas.geometry()
area_km2 = yungas_geom.area().divide(1e6).getInfo()
print(f"Yungas ecoregion area: {area_km2:,.0f} km2")
# Sanity check: published figures put the Bolivian Yungas around 30,000-45,000 km2.
# If this number is wildly different (10x off in either direction), something's wrong --
# stop and check before continuing.

# 2. The stricter habitat envelope: elevation 500-3500m AND forest cover >=30% in 2000
dem = ee.Image("COPERNICUS/DEM/GLO30").select("DEM")
elevation_ok = dem.gte(500).And(dem.lte(3500))

gfc = ee.Image("UMD/hansen/global_forest_change_2025_v1_13")
forest_ok = gfc.select("treecover2000").gte(30)

belt_mask = elevation_ok.And(forest_ok)
# belt_mask is a 0/1 image: 1 where elevation and forest conditions are both met.
# Later steps do image.updateMask(belt_mask) to restrict analysis to this envelope.

# Save the ecoregion boundary to a local file so later scripts don't need to
# re-query Earth Engine for it every time
import geemap
geemap.ee_export_vector(yungas, "data/yungas_ecoregion.geojson")
print("Saved data/yungas_ecoregion.geojson")
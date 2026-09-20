# Yungas Cloud Forest Watch

A landscape-scale analysis of environmental space and satellite-monitoring
coverage in Bolivia's Yungas cloud forest, prompted by the 2025 description
of *Leopardus tilcayo* (Bolivian tiger cat) from this region.

## What this project does NOT do

- It does **not** contain any occurrence data for *Leopardus tilcayo*. No
  such public dataset exists yet -- the species was described in 2025 from
  a small number of specimens, and GBIF currently returns **zero** Bolivia
  records under the historical tiger-cat-complex name.
- It does **not** predict where the cat lives, model its habitat, or make
  any claim about the species' ecology, range, or population.
- It does **not** reproduce or reference the type-locality coordinates of
  the holotype specimen, which are public in the taxonomic literature but
  are deliberately omitted here and from every figure, script, and post in
  this repo. Precise-location data for a newly described, presumably rare
  carnivore should not be casually amplified.

## What this project DOES do

Three questions, using only publicly available landscape data:

1. **How unusual is the Yungas, environmentally, compared to the historical range of the broader tiger-cat complex?** (`scripts/03_extract_environment.py`, `scripts/04_pca.py` -> `figures/figure1_pca.png`)
2. **Where in the Yungas can satellites reliably observe the ground at all?** (`scripts/05_cloud_visibility.py`)
3. **Where has real forest loss occurred (2021-2025), and how does that overlap with where satellites can and can't see?** (`scripts/06_forest_loss.py`, `scripts/07_combine_analysis.py` -> `figures/figure3_monitoring_blindspot.png`)

## Key findings

- **Environmental Context (PCA):** PC1 and PC2 together account for **96.9%** of variance (PC1: 64.6%, PC2: 32.3%) across elevation, mean temperature, and annual precipitation. The Yungas background forms a tight environmental subset near the edge of the historical *Leopardus tigrinus* complex envelope ($n=918$).
- **Cloud Visibility:** Across 94,283 1km grid cells evaluated between 2021 and 2025, optical satellites (Sentinel-2) obtained clear ground observations only **32.1%** of the time on average.
- **Monitoring Blind Spots:** Exactly **50.0% of analyzed 1km grid cells** (33,049 of 66,104 cells) fall into the **poor visibility, high loss** quadrant. Spearman rank correlation between clear-observation fraction and forest loss fraction was **$\rho = 0.253$**, reported descriptively because neighbouring grid cells are spatially correlated.

## Data sources

| Dataset | Source | Use |
|---|---|---|
| Tiger-cat-complex occurrences | GBIF (`data/raw/tigrinus_occurrences.csv`, gitignored -- not in this repo) | Environmental-space comparison |
| Ecoregion boundary | RESOLVE Ecoregions 2017 (`RESOLVE/ECOREGIONS/2017`) | Study-area definition |
| Elevation | Copernicus GLO-30 DEM (`COPERNICUS/DEM/GLO30_2024_1`) | Study-area filter + PCA feature |
| Forest cover / loss | Hansen Global Forest Change v1.11 (`UMD/hansen/global_forest_change_2023_v1_11`) | Study-area filter + loss analysis |
| Temperature / precipitation | WorldClim v1 BIO (`WORLDCLIM/V1/BIO`) | PCA features |
| Cloud/clear observations | Sentinel-2 SR Harmonized (`COPERNICUS/S2_SR_HARMONIZED`) | Visibility analysis |

All datasets are public and were accessed via Google Earth Engine and the GBIF API. No paid or restricted-access data was used.

## Reproducing this

Run `scripts/01` through `scripts/07` in order in your Python environment; each script writes its outputs to `data/`, `outputs/`, or `figures/` before the next script requires them.

## Limitations

- The study-area boundary (elevation 500-3500m, $\ge$30% forest cover within the Bolivian Yungas ecoregion) is a reasonable analytical choice, not an official habitat or protected-area boundary.
- The PCA-env-inspired comparison uses historical tiger-cat-complex records, not confirmed *L. tilcayo* records, because none are public. It describes how unusual the Yungas environment is relative to that broader group's historical range -- it is not a niche model for the new species.
- Forest-loss totals here should not be compared to official Global Forest Watch figures for the region, since the study boundary differs from any official administrative or ecoregion polygon GFW reports on.

## License

MIT -- see `LICENSE`.

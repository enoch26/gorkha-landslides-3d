# Gorkha 2015 Landslides — 3D Terrain + Earthquake Ground Motion Viewer

An interactive 3D visualization of the 2015 Gorkha earthquake in Nepal, combining:
- **Terrain**: High-resolution DEM with landslide polygons
- **PGA**: Peak Ground Acceleration ShakeMap
- **MMI**: Modified Mercalli Intensity ShakeMap

## Quick Start

### View the Live Demo
🌐 **[Open the Interactive 3D Viewer](https://enoch26.github.io/gorkha-landslides-3d/)**

### Run Locally
```bash
# Start the development server
python server.py

# Visit http://localhost:5000 in your browser
```

## Features
- **3D Terrain Visualization**: Explore the DEM with interactive camera controls
- **Dual ShakeMaps**: Toggle between PGA and MMI ground motion intensity
- **Region Extraction**: Zoom to predefined regions (Langtang, Rasuwa, etc.)
- **Cross-section Analysis**: View vertical profiles through landslides
- **Real-time Filtering**: Adjust opacity and thresholds dynamically

## Data Sources
- **Landslide inventory**: Valagussa et al. (2021), including mapped landslide polygons for the 2015 Gorkha earthquake. [Inventory and bounding box](https://www.sciencebase.gov/catalog/item/61f040e1d34e8b818adc3251)
- **Terrain**: Copernicus 30 m DEM ([OpenTopography](https://opentopography.org/news/updated-copernicus-30m-DEM-available))
- **Ground motion**: USGS ShakeMap PGA and MMI for the 2015 Gorkha earthquake ([PGA map](https://earthquake.usgs.gov/earthquakes/eventpage/us20002926/shakemap/pga))
- **Channel steepness**: Channel steepness index derived from the DEM using [LSDTopoTools](https://lsdtopotools.github.io/); see [LSDTopoTools data and scripts](https://doi.org/10.5281/zenodo.8076231).

## Research Context

This viewer presents geospatial data associated with modelling earthquake-induced landslide (EQIL) locations and susceptibility in Nepal after the 2015 Gorkha earthquake. The main model discussed in the study, `fit6a`, estimates spatial variation in landslide intensity using earthquake shaking, channel steepness, rainfall, distance to fluvial channels, and a spatial effect:

```text
log(lambda(s)) = beta0 + f1(PGA(s)) + f2(log(ksn(s))) + f3(Rainfall(s))
				+ beta * exp(-Fd2Ch(s)) + u(s)
```

Here, `lambda(s)` is predicted landslide intensity at location `s`; the `f` terms represent flexible effects, `Fd2Ch` is distance to a channel, and `u(s)` captures residual spatial structure. The viewer's susceptibility and uncertainty layers are intended for spatial exploration, not as a substitute for the full-resolution model outputs or statistical analysis.

The web viewer uses aggregated, lower-resolution data to keep interactive rendering responsive. Values and visual patterns may therefore differ from full-resolution results. Refer to the publications and their accompanying analysis code for the complete methods and model outputs.

For the model implementation and analysis code using INLA and inlabru, see the companion [Gorkha model repository](https://github.com/enoch26/Gorkha).

## Interactive Dashboard

The companion [2D susceptibility dashboard](https://enoch26.shinyapps.io/gorkha-earthquake-landslide-dashboard/) provides another way to explore selected model and covariate layers. This repository hosts the [3D viewer](https://enoch26.github.io/gorkha-landslides-3d/).

## Citation

If you use this viewer, its data, or the associated analysis, cite:

Suen, M. H., Naylor, M., Mudd, S. M., & Lindgren, F. (2026). *Influence of river incision on landslides triggered in Nepal by the 2015 Gorkha earthquake: Results from a pixel-based susceptibility model using inlabru*. *Frontiers in Earth Science*, 14, 1876760.

For methods concerning spatially misaligned data, see:

Suen, M. H., Naylor, M., & Lindgren, F. (2026). *Coherent disaggregation and uncertainty quantification for spatially misaligned data*. *Environmetrics*, 37(2), e70078. https://doi.org/10.1002/env.70078

Dataset versions may change; verify current data and metadata with the official providers.

## Technical Stack
- **Frontend**: Three.js (3D WebGL visualization)
- **Backend**: Python Flask (data processing)
- **Deployment**: GitHub Pages
- **3D development**: Created with assistance from Gemini 4.0 Aragon

## License
Project data and code available under the repository license.

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
- **Landslides**: Valagussa et al., 2021 (Shapefile)
- **Terrain**: Copernicus DEM 30m
- **ShakeMaps**: USGS PGA and MMI for 2015 Gorkha M7.8 event

## Technical Stack
- **Frontend**: Three.js (3D WebGL visualization)
- **Backend**: Python Flask (data processing)
- **Deployment**: GitHub Pages

## License
Project data and code available under the repository license.

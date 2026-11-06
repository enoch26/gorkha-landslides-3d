"""
Extract smaller test regions from Valagussa_2021.shp (2015 M7.8 Gorkha Earthquake Landslides),
drape polygon vertices onto real 3D DEM terrain (AWS Terrarium 30m DEM tiles), map
pga_mean.flt, mmi_mean.flt, and fp6a.gpkg (Bayesian space-time landslide susceptibility model)
onto both the 3D terrain mesh and every landslide polygon, and export 3D GeoJSON files plus a
combined 3D terrain bundle.
"""

import io
import json
import math
import os
import shutil
import sqlite3
import struct
import urllib.request
from PIL import Image
import numpy as np

SHP_DIR = r"Z:\home\gorkha\data\Valagussaandoth\Valagussa_2021"
SHP_PATH = os.path.join(SHP_DIR, "Valagussa_2021.shp")
SHX_PATH = os.path.join(SHP_DIR, "Valagussa_2021.shx")
DBF_PATH = os.path.join(SHP_DIR, "Valagussa_2021.dbf")

RASTER_DIR = r"Z:\home\gorkha\data\raster"
PGA_FLT_PATH = os.path.join(RASTER_DIR, "pga_mean.flt")
MMI_FLT_PATH = os.path.join(RASTER_DIR, "mmi_mean.flt")

GPKG_SRC_PATH = r"Z:\home\gorkha\fp6a.gpkg"
KSN_TIF_PATH = r"Z:\home\gorkha\data\lsdtt\lanczos_\cop30dem_channel_tagged_pixels_near.tif"

# GeoTIFF metadata from cop30dem_channel_tagged_pixels_near.tif (EPSG:32645 in km)
KSN_ULX = 224.78955828567322
KSN_ULY = 3184.377253239011
KSN_DX = 0.028428845063911627
KSN_DY = 0.028428845063911596

# GridFloat header metadata from pga_mean.hdr / mmi_mean.hdr
FLT_NROWS = 479
FLT_NCOLS = 558
FLT_ULX = 80.85
FLT_ULY = 31.95
FLT_DIM = 1.0 / 60.0  # 0.016666666666666666 deg

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT_DIR, exist_ok=True)
GPKG_CACHE_PATH = os.path.join(OUT_DIR, "fp6a_cache.gpkg")

REGIONS = {
    "trisuli_rasuwa": {
        "id": "trisuli_rasuwa",
        "name": "Upper Trisuli / Rasuwa Gorge",
        "subtitle": "Mailung–Syafru corridor (249 landslides)",
        "description": "Deep Himalayan river gorge with steep valley-wall rockfalls and translational slides.",
        "bbox": [85.16, 28.05, 85.26, 28.15],
        "grid_size": 64,
        "dem_zoom": 12,
    },
    "bhote_koshi": {
        "id": "bhote_koshi",
        "name": "Bhote Koshi Canyon (Kodari)",
        "subtitle": "Arniko Highway border gorge (dense cluster)",
        "description": "Highest spatial density of coseismic landslides in the 2015 Gorkha inventory.",
        "bbox": [85.875, 27.885, 85.945, 27.955],
        "grid_size": 64,
        "dem_zoom": 12,
    },
    "langtang": {
        "id": "langtang",
        "name": "Langtang Valley & Massif",
        "subtitle": "Includes the 1.97 km² Langtang rock-ice avalanche",
        "description": "High-relief glaciated valley containing the largest single landslide in the dataset.",
        "bbox": [85.38, 28.14, 85.56, 28.25],
        "grid_size": 64,
        "dem_zoom": 12,
    },
    "budi_gandaki": {
        "id": "budi_gandaki",
        "name": "Budi Gandaki Gorge (Gorkha)",
        "subtitle": "Near M 7.8 mainshock epicentral zone (Max PGA/MMI)",
        "description": "Steep incised valley east of Barpak & Laprak in Gorkha District.",
        "bbox": [84.745, 28.165, 84.835, 28.255],
        "grid_size": 64,
        "dem_zoom": 12,
    },
    "rupture_corridor": {
        "id": "rupture_corridor",
        "name": "Gorkha–Kodari Regional Corridor",
        "subtitle": "Wide 3D fault-rupture swath (Major landslides > 25,000 m²)",
        "description": "Full ground-motion gradient from Barpak epicenter across Langtang to Bhote Koshi.",
        "bbox": [84.65, 27.68, 86.05, 28.42],
        "grid_size": 64,
        "dem_zoom": 9,
        "min_area_filter": 25000.0,
    },
}


def load_shakemap_rasters():
    pga_ln = np.fromfile(PGA_FLT_PATH, dtype="<f4").reshape(FLT_NROWS, FLT_NCOLS)
    mmi = np.fromfile(MMI_FLT_PATH, dtype="<f4").reshape(FLT_NROWS, FLT_NCOLS)
    # Replace NODATA (999.0) with NaN if any
    pga_ln = np.where(pga_ln > 100, np.nan, pga_ln)
    mmi = np.where(mmi > 100, np.nan, mmi)
    pga_g = np.exp(pga_ln)
    return pga_ln, pga_g, mmi


def sample_flt_bilinear(grid, lon, lat):
    c = (lon - FLT_ULX) / FLT_DIM
    r = (FLT_ULY - lat) / FLT_DIM
    c = float(np.clip(c, 0.0, FLT_NCOLS - 1.001))
    r = float(np.clip(r, 0.0, FLT_NROWS - 1.001))
    c0, r0 = int(c), int(r)
    du, dv = c - c0, r - r0
    val = (
        grid[r0, c0] * (1 - du) * (1 - dv)
        + grid[r0, c0 + 1] * du * (1 - dv)
        + grid[r0 + 1, c0] * (1 - du) * dv
        + grid[r0 + 1, c0 + 1] * du * dv
    )
    return float(val)


def sample_flt_grid_for_bbox(grid, bbox, grid_size):
    xmin, ymin, xmax, ymax = bbox
    lons = np.linspace(xmin, xmax, grid_size)
    lats = np.linspace(ymin, ymax, grid_size)
    out = np.zeros((grid_size, grid_size), dtype=np.float32)
    for r, lat in enumerate(lats):
        for c, lon in enumerate(lons):
            out[r, c] = sample_flt_bilinear(grid, lon, lat)
    return out


def lonlat_to_utm45n_km(lon_deg, lat_deg):
    """Project WGS84 (lon, lat) in degrees to EPSG:32645 (UTM Zone 45N) in kilometers."""
    a = 6378137.0
    f = 1.0 / 298.257223563
    k0 = 0.9996
    lon0 = math.radians(87.0)
    e2 = f * (2.0 - f)
    ep2 = e2 / (1.0 - e2)

    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    dlon = lon - lon0

    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    tan_lat = math.tan(lat)

    N = a / math.sqrt(1.0 - e2 * sin_lat * sin_lat)
    T = tan_lat * tan_lat
    C = ep2 * cos_lat * cos_lat
    A = cos_lat * dlon

    M = a * (
        (1.0 - e2 / 4.0 - 3.0 * e2**2 / 64.0 - 5.0 * e2**3 / 256.0) * lat
        - (3.0 * e2 / 8.0 + 3.0 * e2**2 / 32.0 + 45.0 * e2**3 / 1024.0) * math.sin(2.0 * lat)
        + (15.0 * e2**2 / 256.0 + 45.0 * e2**3 / 1024.0) * math.sin(4.0 * lat)
        - (35.0 * e2**3 / 3072.0) * math.sin(6.0 * lat)
    )

    easting_m = 500000.0 + k0 * N * (
        A
        + (1.0 - T + C) * A**3 / 6.0
        + (5.0 - 18.0 * T + T**2 + 72.0 * C - 58.0 * ep2) * A**5 / 120.0
    )
    northing_m = k0 * (
        M
        + N
        * tan_lat
        * (
            A**2 / 2.0
            + (5.0 - T + 9.0 * C + 4.0 * C**2) * A**4 / 24.0
            + (61.0 - 58.0 * T + T**2 + 600.0 * C - 330.0 * ep2) * A**6 / 720.0
        )
    )
    return easting_m / 1000.0, northing_m / 1000.0


def fill_nan_nearest(grid, iterations=65):
    """Fill NaN boundary cells via non-wrapping nearest-valid neighbor propagation."""
    filled = grid.copy()
    h, w = filled.shape
    for _ in range(iterations):
        mask = np.isnan(filled)
        if not np.any(mask):
            break
        padded = np.pad(filled, 1, mode="constant", constant_values=np.nan)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            neighbor = padded[1 + dr : 1 + dr + h, 1 + dc : 1 + dc + w]
            replace = mask & ~np.isnan(neighbor)
            filled[replace] = neighbor[replace]
            mask = np.isnan(filled)
    return filled


def load_fp6a_susceptibility():
    """Load Bayesian space-time landslide susceptibility from fp6a.gpkg onto its 315x500 UTM45N grid."""
    if not os.path.exists(GPKG_CACHE_PATH):
        print(f"Caching {GPKG_SRC_PATH} to {GPKG_CACHE_PATH}...")
        shutil.copy2(GPKG_SRC_PATH, GPKG_CACHE_PATH)

    conn = sqlite3.connect(GPKG_CACHE_PATH)
    cur = conn.cursor()
    rows = cur.execute('SELECT geom, mean, sd, "q0.5", "q0.975", count FROM fp6a').fetchall()
    conn.close()

    raw = np.zeros((len(rows), 7), dtype=np.float64)
    for idx, (g, m, s, med, q9, cnt) in enumerate(rows):
        x, y = struct.unpack("<2d", g[-16:])
        raw[idx] = [x, y, m, s, med, q9, cnt if cnt is not None else 0.0]

    ux = np.unique(np.round(raw[:, 0], 4))
    uy = np.unique(np.round(raw[:, 1], 4))
    x0, dx = float(ux[0]), float((ux[-1] - ux[0]) / (len(ux) - 1))
    y0, dy = float(uy[0]), float((uy[-1] - uy[0]) / (len(uy) - 1))
    nx, ny = len(ux), len(uy)

    mean_raw = np.full((ny, nx), np.nan, dtype=np.float32)
    sd_raw = np.full((ny, nx), np.nan, dtype=np.float32)
    q975_raw = np.full((ny, nx), np.nan, dtype=np.float32)

    for row in raw:
        ci = int(round((row[0] - x0) / dx))
        ri = int(round((row[1] - y0) / dy))
        if 0 <= ri < ny and 0 <= ci < nx:
            mean_raw[ri, ci] = row[2]
            sd_raw[ri, ci] = row[3]
            q975_raw[ri, ci] = row[5]

    mean_filled = fill_nan_nearest(mean_raw)
    sd_filled = fill_nan_nearest(sd_raw)
    q975_filled = fill_nan_nearest(q975_raw)

    meta = {"x0": x0, "dx": dx, "y0": y0, "dy": dy, "nx": nx, "ny": ny}
    return meta, mean_raw, mean_filled, sd_filled, q975_filled


def sample_fp6a_bilinear(grid, meta, lon, lat):
    x_km, y_km = lonlat_to_utm45n_km(lon, lat)
    u = float(np.clip((x_km - meta["x0"]) / meta["dx"], 0.0, meta["nx"] - 1.001))
    v = float(np.clip((y_km - meta["y0"]) / meta["dy"], 0.0, meta["ny"] - 1.001))
    c0, r0 = int(u), int(v)
    du, dv = u - c0, v - r0
    val = (
        grid[r0, c0] * (1 - du) * (1 - dv)
        + grid[r0, c0 + 1] * du * (1 - dv)
        + grid[r0 + 1, c0] * (1 - du) * dv
        + grid[r0 + 1, c0 + 1] * du * dv
    )
    return float(val)


def sample_fp6a_grid_for_bbox(grid, meta, bbox, grid_size):
    xmin, ymin, xmax, ymax = bbox
    lons = np.linspace(xmin, xmax, grid_size)
    lats = np.linspace(ymin, ymax, grid_size)
    out = np.zeros((grid_size, grid_size), dtype=np.float32)
    for r, lat in enumerate(lats):
        for c, lon in enumerate(lons):
            out[r, c] = sample_fp6a_bilinear(grid, meta, lon, lat)
    return out


def load_ksn_geotiff():
    """Load channel steepness index (k_sn) GeoTIFF (cop30dem_channel_tagged_pixels_near.tif)."""
    with open(KSN_TIF_PATH, "rb") as f:
        raw_bytes = f.read()
    img = Image.open(io.BytesIO(raw_bytes))
    ksn_raw = np.array(img, dtype=np.float32)
    # Build a 16x downsampled nearest-neighbor filled fallback grid for any NaN boundary pixels
    ksn_coarse = fill_nan_nearest(ksn_raw[::16, ::16], iterations=85)
    return ksn_raw, ksn_coarse


def sample_ksn_at_lonlat(ksn_raw, ksn_coarse, lon, lat, allow_nan=False):
    """Sample k_sn at WGS84 (lon, lat) via UTM Zone 45N (km) GeoTIFF coordinates."""
    x_km, y_km = lonlat_to_utm45n_km(lon, lat)
    h, w = ksn_raw.shape
    c = (x_km - KSN_ULX) / KSN_DX
    r = (KSN_ULY - y_km) / KSN_DY
    ci = int(round(c))
    ri = int(round(r))
    if 0 <= ri < h and 0 <= ci < w:
        v = float(ksn_raw[ri, ci])
        if not math.isnan(v):
            return v
        # Check 3x3 neighborhood in full-res raster
        r0, r1 = max(0, ri - 1), min(h, ri + 2)
        c0, c1 = max(0, ci - 1), min(w, ci + 2)
        patch = ksn_raw[r0:r1, c0:c1]
        valid = patch[~np.isnan(patch)]
        if valid.size > 0:
            return float(valid.mean())
    if allow_nan:
        return float("nan")
    ch, cw = ksn_coarse.shape
    cri = int(np.clip(round(r / 16.0), 0, ch - 1))
    cci = int(np.clip(round(c / 16.0), 0, cw - 1))
    return float(ksn_coarse[cri, cci])


def sample_ksn_grid_for_bbox(ksn_raw, ksn_coarse, bbox, grid_size, allow_nan=False):
    xmin, ymin, xmax, ymax = bbox
    lons = np.linspace(xmin, xmax, grid_size)
    lats = np.linspace(ymin, ymax, grid_size)
    out = np.zeros((grid_size, grid_size), dtype=np.float32)
    for r, lat in enumerate(lats):
        for c, lon in enumerate(lons):
            out[r, c] = sample_ksn_at_lonlat(ksn_raw, ksn_coarse, lon, lat, allow_nan=allow_nan)
    return out


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


TILE_CACHE = {}


def fetch_terrarium_tile(z, x, y):
    key = (z, x, y)
    if key in TILE_CACHE:
        return TILE_CACHE[key]
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
    req = urllib.request.Request(url, headers={"User-Agent": "GorkhaLandslide3DViewer/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        img = Image.open(io.BytesIO(resp.read())).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    elev = (arr[:, :, 0] * 256.0 + arr[:, :, 1] + arr[:, :, 2] / 256.0) - 32768.0
    TILE_CACHE[key] = elev
    return elev


def build_dem_for_bbox(bbox, grid_size=64, zoom=12):
    xmin, ymin, xmax, ymax = bbox
    x0, y0 = deg2num(ymax, xmin, zoom)
    x1, y1 = deg2num(ymin, xmax, zoom)

    nx = x1 - x0 + 1
    ny = y1 - y0 + 1
    mosaic = np.zeros((ny * 256, nx * 256), dtype=np.float32)

    for ty in range(y0, y1 + 1):
        for tx in range(x0, x1 + 1):
            tile_elev = fetch_terrarium_tile(zoom, tx, ty)
            iy = (ty - y0) * 256
            ix = (tx - x0) * 256
            mosaic[iy : iy + 256, ix : ix + 256] = tile_elev

    lons = np.linspace(xmin, xmax, grid_size)
    lats = np.linspace(ymin, ymax, grid_size)
    n = 2.0 ** zoom

    dem_grid = np.zeros((grid_size, grid_size), dtype=np.float32)
    for r, lat in enumerate(lats):
        lat_rad = math.radians(lat)
        yf = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        py = int(np.clip((yf - y0) * 256.0, 0, mosaic.shape[0] - 1))
        for c, lon in enumerate(lons):
            xf = (lon + 180.0) / 360.0 * n
            px = int(np.clip((xf - x0) * 256.0, 0, mosaic.shape[1] - 1))
            dem_grid[r, c] = mosaic[py, px]

    mean_lat = 0.5 * (ymin + ymax)
    dx_m = ((xmax - xmin) / (grid_size - 1)) * 111320.0 * math.cos(math.radians(mean_lat))
    dy_m = ((ymax - ymin) / (grid_size - 1)) * 110540.0
    dz_dy, dz_dx = np.gradient(dem_grid, dy_m, dx_m)
    slope_rad = np.arctan(np.hypot(dz_dx, dz_dy))
    slope_deg = np.degrees(slope_rad)
    aspect_deg = (np.degrees(np.arctan2(-dz_dx, -dz_dy)) + 360.0) % 360.0

    return dem_grid, slope_deg, aspect_deg


def sample_grid(grid, bbox, lon, lat):
    xmin, ymin, xmax, ymax = bbox
    h, w = grid.shape
    u = (lon - xmin) / (xmax - xmin) * (w - 1)
    v = (lat - ymin) / (ymax - ymin) * (h - 1)
    u = float(np.clip(u, 0.0, w - 1.001))
    v = float(np.clip(v, 0.0, h - 1.001))
    c0, r0 = int(u), int(v)
    du, dv = u - c0, v - r0
    val = (
        grid[r0, c0] * (1 - du) * (1 - dv)
        + grid[r0, c0 + 1] * du * (1 - dv)
        + grid[r0 + 1, c0] * (1 - du) * dv
        + grid[r0 + 1, c0 + 1] * du * dv
    )
    return float(val)


def simplify_ring(coords, max_pts=42):
    n = len(coords)
    if n <= max_pts:
        return coords
    step = max(1, (n - 1) // (max_pts - 1))
    simplified = [coords[i] for i in range(0, n - 1, step)]
    if simplified[-1] != coords[-1]:
        simplified.append(coords[-1])
    return simplified


def main():
    print("Loading ShakeMap rasters (pga_mean.flt & mmi_mean.flt)...")
    pga_ln_rast, pga_g_rast, mmi_rast = load_shakemap_rasters()

    print("Loading Bayesian space-time susceptibility model (fp6a.gpkg)...")
    fp6a_meta, fp6a_mean_raw, fp6a_mean_rast, fp6a_sd_rast, fp6a_q975_rast = load_fp6a_susceptibility()

    print("Loading LSDTopoTools channel steepness index GeoTIFF (cop30dem_channel_tagged_pixels_near.tif)...")
    ksn_raw_rast, ksn_coarse_rast = load_ksn_geotiff()

    print("Reading Valagussa_2021 shapefile into memory...")
    with open(SHX_PATH, "rb") as f:
        shx_data = f.read()
    with open(SHP_PATH, "rb") as f:
        shp_data = f.read()
    with open(DBF_PATH, "rb") as f:
        dbf_data = f.read()

    num_rec, hdr_len, rec_len = struct.unpack("<IHH", dbf_data[4:12])
    print(f"Loaded {num_rec} total landslide records.")

    region_dems = {}
    region_shakes = {}
    region_suscs = {}
    region_ksns = {}
    for rkey, rmeta in REGIONS.items():
        z_level = rmeta.get("dem_zoom", 12)
        gs = rmeta["grid_size"]
        print(f"Building 3D DEM + PGA/MMI + fp6a + k_sn grids for {rmeta['name']} (zoom {z_level})...")
        dem, slope, aspect = build_dem_for_bbox(rmeta["bbox"], gs, zoom=z_level)
        pga_g_grid = sample_flt_grid_for_bbox(pga_g_rast, rmeta["bbox"], gs)
        pga_ln_grid = sample_flt_grid_for_bbox(pga_ln_rast, rmeta["bbox"], gs)
        mmi_grid = sample_flt_grid_for_bbox(mmi_rast, rmeta["bbox"], gs)
        susc_mean_grid = sample_fp6a_grid_for_bbox(fp6a_mean_rast, fp6a_meta, rmeta["bbox"], gs)
        susc_sd_grid = sample_fp6a_grid_for_bbox(fp6a_sd_rast, fp6a_meta, rmeta["bbox"], gs)
        ksn_grid = sample_ksn_grid_for_bbox(ksn_raw_rast, ksn_coarse_rast, rmeta["bbox"], gs, allow_nan=False)
        region_dems[rkey] = (dem, slope, aspect)
        region_shakes[rkey] = (pga_g_grid, pga_ln_grid, mmi_grid)
        region_suscs[rkey] = (susc_mean_grid, susc_sd_grid)
        region_ksns[rkey] = ksn_grid
        print(
            f"  -> Elev: {dem.min():.0f}-{dem.max():.0f}m | "
            f"PGA: {pga_g_grid.min():.3f}-{pga_g_grid.max():.3f}g | "
            f"fp6a: {susc_mean_grid.min():.3f}-{susc_mean_grid.max():.2f} | "
            f"k_sn: {ksn_grid.min():.1f}-{ksn_grid.max():.1f}"
        )

    region_features = {k: [] for k in REGIONS}
    region_geojson_features = {k: [] for k in REGIONS}

    for i in range(num_rec):
        off, _ = struct.unpack(">2i", shx_data[100 + i * 8 : 108 + i * 8])
        byte_off = off * 2 + 8
        xmin, ymin, xmax, ymax = struct.unpack("<4d", shp_data[byte_off + 4 : byte_off + 36])
        cx, cy = 0.5 * (xmin + xmax), 0.5 * (ymin + ymax)

        dbf_off = hdr_len + i * rec_len
        area_str = dbf_data[dbf_off + 1 : dbf_off + rec_len].decode("ascii").strip()
        area_m2 = float(area_str) if area_str else 0.0

        matched_regions = []
        for rkey, rmeta in REGIONS.items():
            bx0, by0, bx1, by1 = rmeta["bbox"]
            min_a = rmeta.get("min_area_filter", 0.0)
            if bx0 <= cx <= bx1 and by0 <= cy <= by1 and area_m2 >= min_a:
                matched_regions.append(rkey)

        if not matched_regions:
            continue

        nparts, npts = struct.unpack("<2i", shp_data[byte_off + 36 : byte_off + 44])
        parts = struct.unpack(f"<{nparts}i", shp_data[byte_off + 44 : byte_off + 44 + 4 * nparts])
        pts_off = byte_off + 44 + 4 * nparts
        raw_pts = struct.unpack(f"<{2 * npts}d", shp_data[pts_off : pts_off + 16 * npts])
        end_idx = parts[1] if nparts > 1 else npts
        outer_ring = [(raw_pts[2 * j], raw_pts[2 * j + 1]) for j in range(0, end_idx)]

        # Sample PGA, MMI, Bayesian Susceptibility (fp6a.gpkg), and Channel Steepness (k_sn)
        c_pga_ln = round(sample_flt_bilinear(pga_ln_rast, cx, cy), 3)
        c_pga_g = round(sample_flt_bilinear(pga_g_rast, cx, cy), 3)
        c_mmi = round(sample_flt_bilinear(mmi_rast, cx, cy), 2)
        c_susc_mean = round(sample_fp6a_bilinear(fp6a_mean_rast, fp6a_meta, cx, cy), 4)
        c_susc_log10 = round(math.log10(max(c_susc_mean, 1e-5)), 3)
        c_susc_sd = round(sample_fp6a_bilinear(fp6a_sd_rast, fp6a_meta, cx, cy), 4)
        c_susc_q975 = round(sample_fp6a_bilinear(fp6a_q975_rast, fp6a_meta, cx, cy), 3)
        c_ksn = round(sample_ksn_at_lonlat(ksn_raw_rast, ksn_coarse_rast, cx, cy, allow_nan=False), 1)
        ring_step = max(1, len(outer_ring) // 12)
        ring_ksns = [
            sample_ksn_at_lonlat(ksn_raw_rast, ksn_coarse_rast, pt[0], pt[1], allow_nan=False)
            for pt in outer_ring[::ring_step]
        ]
        c_ksn_max = round(max([c_ksn] + ring_ksns), 1)

        for matched_region in matched_regions:
            dem, slope_grid, aspect_grid = region_dems[matched_region]
            bbox = REGIONS[matched_region]["bbox"]

            ring_elevs = [sample_grid(dem, bbox, pt[0], pt[1]) for pt in outer_ring]
            elev_min = float(min(ring_elevs))
            elev_max = float(max(ring_elevs))
            elev_mean = float(sum(ring_elevs) / len(ring_elevs))
            relief_m = round(elev_max - elev_min, 1)
            c_slope = round(sample_grid(slope_grid, bbox, cx, cy), 1)
            c_aspect = round(sample_grid(aspect_grid, bbox, cx, cy), 0)
            vol_m3 = round(0.05 * (max(area_m2, 1.0) ** 1.45), 1)

            geojson_ring = [
                [round(pt[0], 6), round(pt[1], 6), round(z, 1)]
                for pt, z in zip(outer_ring, ring_elevs)
            ]
            props = {
                "fid": i,
                "area_m2": round(area_m2, 1),
                "elev_mean": round(elev_mean, 1),
                "elev_min": round(elev_min, 1),
                "elev_max": round(elev_max, 1),
                "relief_m": relief_m,
                "slope_deg": c_slope,
                "aspect_deg": c_aspect,
                "pga_g": c_pga_g,
                "pga_ln": c_pga_ln,
                "mmi": c_mmi,
                "susc_mean": c_susc_mean,
                "susc_log10": c_susc_log10,
                "susc_sd": c_susc_sd,
                "susc_q975": c_susc_q975,
                "ksn": c_ksn,
                "ksn_max": c_ksn_max,
                "vol_m3": vol_m3,
                "centroid": [round(cx, 5), round(cy, 5), round(elev_mean, 1)],
            }
            region_geojson_features[matched_region].append(
                {
                    "type": "Feature",
                    "properties": props,
                    "geometry": {"type": "Polygon", "coordinates": [geojson_ring]},
                }
            )

            simp_pts = simplify_ring(outer_ring, max_pts=36)
            simp_ring = [
                [round(pt[0], 5), round(pt[1], 5), round(sample_grid(dem, bbox, pt[0], pt[1]), 1)]
                for pt in simp_pts
            ]
            region_features[matched_region].append(
                {
                    **props,
                    "ring": simp_ring,
                }
            )

    # Also build overview minimap grids for full inventory bbox [84.2427, 27.3837, 86.6961, 28.7362]
    full_bbox = [84.2427, 27.3837, 86.6961, 28.7362]
    overview_pga = sample_flt_grid_for_bbox(pga_g_rast, full_bbox, 44)
    overview_mmi = sample_flt_grid_for_bbox(mmi_rast, full_bbox, 44)
    overview_susc_raw = sample_fp6a_grid_for_bbox(fp6a_mean_raw, fp6a_meta, full_bbox, 44)
    overview_susc_list = [
        [round(float(v), 3) if not np.isnan(v) else -1.0 for v in row]
        for row in overview_susc_raw
    ]
    overview_ksn_raw = sample_ksn_grid_for_bbox(ksn_raw_rast, ksn_coarse_rast, full_bbox, 44, allow_nan=True)
    overview_ksn_list = [
        [round(float(v), 1) if not np.isnan(v) else -1.0 for v in row]
        for row in overview_ksn_raw
    ]

    bundle = {
        "overview": {
            "bbox": full_bbox,
            "grid_size": 44,
            "pga_g": np.round(overview_pga, 3).tolist(),
            "mmi": np.round(overview_mmi, 2).tolist(),
            "susc_mean": overview_susc_list,
            "ksn": overview_ksn_list,
        },
        "regions": {},
    }

    for rkey, rmeta in REGIONS.items():
        dem, slope_grid, _ = region_dems[rkey]
        pga_g_grid, pga_ln_grid, mmi_grid = region_shakes[rkey]
        susc_mean_grid, susc_sd_grid = region_suscs[rkey]
        ksn_grid = region_ksns[rkey]
        susc_log10_grid = np.log10(np.maximum(susc_mean_grid, 1e-5))
        feats = region_features[rkey]
        feats.sort(key=lambda f: f["area_m2"], reverse=True)

        geojson_path = os.path.join(OUT_DIR, f"{rkey}_3d.geojson")
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "type": "FeatureCollection",
                    "name": rmeta["name"],
                    "bbox": rmeta["bbox"],
                    "features": region_geojson_features[rkey],
                },
                f,
            )

        areas = [f["area_m2"] for f in feats]
        total_area_km2 = sum(areas) / 1e6
        bundle["regions"][rkey] = {
            **rmeta,
            "stats": {
                "count": len(feats),
                "total_area_km2": round(total_area_km2, 3),
                "max_area_m2": round(max(areas) if areas else 0, 1),
                "median_area_m2": round(float(np.median(areas)) if areas else 0, 1),
                "elev_min_m": round(float(dem.min()), 0),
                "elev_max_m": round(float(dem.max()), 0),
                "mean_slope_deg": round(float(slope_grid.mean()), 1),
                "pga_min_g": round(float(pga_g_grid.min()), 3),
                "pga_max_g": round(float(pga_g_grid.max()), 3),
                "pga_ln_min": round(float(pga_ln_grid.min()), 2),
                "pga_ln_max": round(float(pga_ln_grid.max()), 2),
                "mmi_min": round(float(mmi_grid.min()), 2),
                "mmi_max": round(float(mmi_grid.max()), 2),
                "susc_min": round(float(susc_mean_grid.min()), 4),
                "susc_median": round(float(np.median(susc_mean_grid)), 3),
                "susc_max": round(float(susc_mean_grid.max()), 2),
                "susc_log10_min": round(float(susc_log10_grid.min()), 2),
                "susc_log10_max": round(float(susc_log10_grid.max()), 2),
                "susc_sd_min": round(float(susc_sd_grid.min()), 4),
                "susc_sd_max": round(float(susc_sd_grid.max()), 2),
                "ksn_min": round(float(ksn_grid.min()), 1),
                "ksn_median": round(float(np.median(ksn_grid)), 1),
                "ksn_p90": round(float(np.percentile(ksn_grid, 90)), 1),
                "ksn_max": round(float(ksn_grid.max()), 1),
            },
            "dem": np.round(dem, 1).tolist(),
            "pga_g": np.round(pga_g_grid, 4).tolist(),
            "pga_ln": np.round(pga_ln_grid, 3).tolist(),
            "mmi": np.round(mmi_grid, 2).tolist(),
            "susc_mean": np.round(susc_mean_grid, 4).tolist(),
            "susc_sd": np.round(susc_sd_grid, 4).tolist(),
            "ksn": np.round(ksn_grid, 1).tolist(),
            "features": feats,
        }
        print(f"Saved {geojson_path} ({len(feats)} features)")

    bundle_path = os.path.join(OUT_DIR, "regions_3d_data.json")
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, separators=(",", ":"))
    print(f"Combined 3D + PGA/MMI + fp6a bundle written ({os.path.getsize(bundle_path)/1024:.1f} KB)")


if __name__ == "__main__":
    main()

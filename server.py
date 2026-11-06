"""
Interactive 3D Landslide Map Server for Valagussa_2021.shp (2015 M7.8 Gorkha Earthquake).
Serves the interactive 3D web application and provides a live `/api/custom_bbox` endpoint
to extract and drape landslide polygons onto 3D DEM terrain for any user-selected bounding box.
"""

import json
import os
import struct
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from extract_region import (
    SHP_PATH,
    SHX_PATH,
    DBF_PATH,
    build_dem_for_bbox,
    sample_grid,
    simplify_ring,
)
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_SHP_CACHE = None


def get_shp_cache():
    global _SHP_CACHE
    if _SHP_CACHE is None:
        print("Caching shapefile index in memory for live queries...")
        with open(SHX_PATH, "rb") as f:
            shx_data = f.read()
        with open(SHP_PATH, "rb") as f:
            shp_data = f.read()
        with open(DBF_PATH, "rb") as f:
            dbf_data = f.read()
        num_rec, hdr_len, rec_len = struct.unpack("<IHH", dbf_data[4:12])
        _SHP_CACHE = (shx_data, shp_data, dbf_data, num_rec, hdr_len, rec_len)
    return _SHP_CACHE


def extract_custom_bbox(bbox, grid_size=48, max_features=350):
    xmin, ymin, xmax, ymax = bbox
    dx = max(1e-5, xmax - xmin)
    dy = max(1e-5, ymax - ymin)
    shx_data, shp_data, dbf_data, num_rec, hdr_len, rec_len = get_shp_cache()
    dem, slope_grid, aspect_grid = build_dem_for_bbox(bbox, grid_size=grid_size, zoom=12)

    feats = []
    for i in range(num_rec):
        off, _ = struct.unpack(">2i", shx_data[100 + i * 8 : 108 + i * 8])
        byte_off = off * 2 + 8
        fx0, fy0, fx1, fy1 = struct.unpack("<4d", shp_data[byte_off + 4 : byte_off + 36])
        cx, cy = 0.5 * (fx0 + fx1), 0.5 * (fy0 + fy1)
        if not (xmin <= cx <= xmax and ymin <= cy <= ymax):
            continue

        nparts, npts = struct.unpack("<2i", shp_data[byte_off + 36 : byte_off + 44])
        parts = struct.unpack(f"<{nparts}i", shp_data[byte_off + 44 : byte_off + 44 + 4 * nparts])
        pts_off = byte_off + 44 + 4 * nparts
        raw_pts = struct.unpack(f"<{2 * npts}d", shp_data[pts_off : pts_off + 16 * npts])

        dbf_off = hdr_len + i * rec_len
        area_str = dbf_data[dbf_off + 1 : dbf_off + rec_len].decode("ascii").strip()
        area_m2 = float(area_str) if area_str else 0.0

        end_idx = parts[1] if nparts > 1 else npts
        outer_ring = [(raw_pts[2 * j], raw_pts[2 * j + 1]) for j in range(0, end_idx)]
        ring_elevs = [sample_grid(dem, bbox, pt[0], pt[1]) for pt in outer_ring]

        elev_min = float(min(ring_elevs))
        elev_max = float(max(ring_elevs))
        elev_mean = float(sum(ring_elevs) / len(ring_elevs))
        relief_m = round(elev_max - elev_min, 1)
        c_slope = round(sample_grid(slope_grid, bbox, cx, cy), 1)
        c_aspect = round(sample_grid(aspect_grid, bbox, cx, cy), 0)
        vol_m3 = round(0.05 * (max(area_m2, 1.0) ** 1.45), 1)

        simp_pts = simplify_ring(outer_ring, max_pts=20)
        q_ring = [
            [
                int(round((pt[0] - xmin) / dx * 10000)),
                int(round((pt[1] - ymin) / dy * 10000)),
                int(round(sample_grid(dem, bbox, pt[0], pt[1]))),
            ]
            for pt in simp_pts
        ]
        q_cent = [
            int(round((cx - xmin) / dx * 10000)),
            int(round((cy - ymin) / dy * 10000)),
            int(round(elev_mean)),
        ]
        feats.append(
            {
                "id": i,
                "a": int(round(area_m2)),
                "z": int(round(elev_mean)),
                "z0": int(round(elev_min)),
                "z1": int(round(elev_max)),
                "dz": int(round(relief_m)),
                "sl": round(c_slope, 1),
                "as": int(c_aspect),
                "v": int(round(vol_m3)),
                "c": q_cent,
                "r": q_ring,
            }
        )

    feats.sort(key=lambda f: f["a"], reverse=True)
    if len(feats) > max_features:
        feats = feats[:max_features]

    areas = [f["a"] for f in feats]
    return {
        "id": "custom",
        "name": f"Custom Box ({xmin:.2f}°E–{xmax:.2f}°E, {ymin:.2f}°N–{ymax:.2f}°N)",
        "subtitle": f"{len(feats)} landslides extracted live from Valagussa_2021.shp",
        "description": "Dynamically extracted test window with 3D DEM draping.",
        "bbox": bbox,
        "grid_size": grid_size,
        "stats": {
            "count": len(feats),
            "total_area_km2": round(sum(areas) / 1e6, 3),
            "max_area_m2": round(max(areas) if areas else 0, 1),
            "median_area_m2": round(float(np.median(areas)) if areas else 0, 1),
            "elev_min_m": int(round(float(dem.min()))),
            "elev_max_m": int(round(float(dem.max()))),
            "mean_slope_deg": round(float(slope_grid.mean()), 1),
        },
        "dem": np.round(dem, 0).astype(int).tolist(),
        "features": feats,
    }


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/custom_bbox":
            qs = urllib.parse.parse_qs(parsed.query)
            try:
                xmin = float(qs["xmin"][0])
                ymin = float(qs["ymin"][0])
                xmax = float(qs["xmax"][0])
                ymax = float(qs["ymax"][0])
                data = extract_custom_bbox([xmin, ymin, xmax, ymax])
                payload = json.dumps(data, separators=(",", ":")).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                err = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(err)
            return
        return super().do_GET()


if __name__ == "__main__":
    port = 8765
    print(f"Starting Gorkha 3D Landslide Map App at http://localhost:{port}")
    server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
    server.serve_forever()

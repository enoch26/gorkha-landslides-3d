"""
Generates the compact 3D dataset (including DEM, PGA, MMI grids and per-polygon attributes).
"""

import json
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "regions_3d_data.json")


def round_2d(arr, decimals=3):
    return [[round(float(v), decimals) for v in row] for row in arr]


def make_compact_bundle(full_bundle, target_grid=48, max_pts=18, max_feats=300):
    ov = full_bundle.get("overview", {})
    compact = {
        "overview": {
            "bbox": ov.get("bbox"),
            "grid_size": ov.get("grid_size", 44),
            "pga_g": round_2d(ov.get("pga_g", []), 3),
            "mmi": round_2d(ov.get("mmi", []), 2),
            "susc_mean": round_2d(ov.get("susc_mean", []), 3),
            "ksn": round_2d(ov.get("ksn", []), 1),
        },
        "regions": {},
    }
    for rkey, rdata in full_bundle["regions"].items():
        dem = np.array(rdata["dem"], dtype=np.float64)
        pga_g = np.array(rdata["pga_g"], dtype=np.float64)
        mmi = np.array(rdata["mmi"], dtype=np.float64)
        susc_mean = np.array(rdata["susc_mean"], dtype=np.float64)
        susc_sd = np.array(rdata["susc_sd"], dtype=np.float64)
        ksn = np.array(rdata["ksn"], dtype=np.float64)
        h, w = dem.shape
        idx_r = np.linspace(0, h - 1, target_grid).astype(int)
        idx_c = np.linspace(0, w - 1, target_grid).astype(int)

        sub_dem = np.round(dem[np.ix_(idx_r, idx_c)], 0).astype(int).tolist()
        sub_pga = round_2d(pga_g[np.ix_(idx_r, idx_c)], 3)
        sub_mmi = round_2d(mmi[np.ix_(idx_r, idx_c)], 2)
        sub_susc_mean = round_2d(susc_mean[np.ix_(idx_r, idx_c)], 3)
        sub_susc_sd = round_2d(susc_sd[np.ix_(idx_r, idx_c)], 3)
        sub_ksn = round_2d(ksn[np.ix_(idx_r, idx_c)], 1)

        xmin, ymin, xmax, ymax = rdata["bbox"]
        dx = xmax - xmin
        dy = ymax - ymin

        compact_feats = []
        for f in rdata["features"][:max_feats]:
            ring = f["ring"]
            n = len(ring)
            if n > max_pts:
                step = max(1, (n - 1) // (max_pts - 1))
                s_ring = [ring[i] for i in range(0, n - 1, step)]
                if s_ring[-1] != ring[-1]:
                    s_ring.append(ring[-1])
            else:
                s_ring = ring

            q_ring = [
                [
                    int(round((p[0] - xmin) / dx * 10000)),
                    int(round((p[1] - ymin) / dy * 10000)),
                    int(round(p[2])),
                ]
                for p in s_ring
            ]
            cx, cy, cz = f["centroid"]
            q_cent = [
                int(round((cx - xmin) / dx * 10000)),
                int(round((cy - ymin) / dy * 10000)),
                int(round(cz)),
            ]
            compact_feats.append(
                {
                    "id": f["fid"],
                    "a": int(round(f["area_m2"])),
                    "z": int(round(f["elev_mean"])),
                    "z0": int(round(f["elev_min"])),
                    "z1": int(round(f["elev_max"])),
                    "dz": int(round(f["relief_m"])),
                    "sl": round(f["slope_deg"], 1),
                    "as": int(f["aspect_deg"]),
                    "pg": round(f["pga_g"], 3),
                    "pl": round(f["pga_ln"], 2),
                    "mm": round(f["mmi"], 2),
                    "sm": round(f["susc_mean"], 3),
                    "slg": round(f["susc_log10"], 2),
                    "ssd": round(f["susc_sd"], 3),
                    "sq9": round(f["susc_q975"], 2),
                    "ks": int(round(f["ksn"])),
                    "ksm": int(round(f["ksn_max"])),
                    "v": int(round(f["vol_m3"])),
                    "c": q_cent,
                    "r": q_ring,
                }
            )

        compact["regions"][rkey] = {
            "id": rdata["id"],
            "name": rdata["name"],
            "subtitle": rdata["subtitle"],
            "description": rdata["description"],
            "bbox": rdata["bbox"],
            "grid_size": target_grid,
            "stats": rdata["stats"],
            "dem": sub_dem,
            "pga_g": sub_pga,
            "mmi": sub_mmi,
            "susc_mean": sub_susc_mean,
            "susc_sd": sub_susc_sd,
            "ksn": sub_ksn,
            "features": compact_feats,
        }
    return compact


if __name__ == "__main__":
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        full_bundle = json.load(f)
    compact = make_compact_bundle(full_bundle, target_grid=36, max_pts=14, max_feats=160)
    out_compact = os.path.join(BASE_DIR, "data", "regions_3d_compact.json")
    with open(out_compact, "w", encoding="utf-8") as f:
        json.dump(compact, f, separators=(",", ":"))
    print(f"Compact bundle size: {os.path.getsize(out_compact)/1024:.1f} KB")

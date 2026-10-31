# AGENTS.md — Gorkha 2015 3D Landslide & Hazard Viewer

## Environment & Build Quirks Learned

1. **Pure-Python Geospatial Parsing (No `gdal` / `rasterio` / `geopandas` / `pyproj` installed)**
   - The local Python environment includes `numpy`, `Pillow` (`PIL`), and `sqlite3`, but does **not** have `geopandas`, `rasterio`, `shapely`, `scipy`, or `pyproj`.
   - **Shapefiles (`.shp` / `.shx` / `.dbf`)**: Parse binary records directly using Python's `struct` module (`PolygonZ` type `15`).
   - **ESRI GridFloat (`.flt` / `.hdr`)**: Read via `np.fromfile(path, dtype="<f4").reshape(nrows, ncols)`. Note that `pga_mean.flt` stores $\ln(\text{PGA in } g)$, so convert via `np.exp(pga_ln)`.
   - **SQLite GeoPackage (`fp6a.gpkg`)**: Copy over the network share (`Z:\`) to local disk (`data/fp6a_cache.gpkg`) before querying with `sqlite3` to avoid SQLite network-locking slowdowns. Parse GeoPackage `GP` binary point blobs by unpacking the trailing 16 bytes (`struct.unpack("<2d", blob[-16:])`).
   - **LZW-Compressed Float32 GeoTIFF (`cop30dem_channel_tagged_pixels_near.tif`)**: Read the entire file into memory first (`io.BytesIO(f.read())`) before passing to `PIL.Image.open()` and `np.array(..., dtype=np.float32)`. Reading directly from `Z:\` via `Image.open(path)` triggers thousands of slow strip seeks over the network mount.

2. **Coordinate Reference System Quirk (`EPSG:32645` in Kilometers)**
   - Both `fp6a.gpkg` and `cop30dem_channel_tagged_pixels_near.tif` use **WGS 84 / UTM Zone 45N (`EPSG:32645`, central meridian `87°E`) with units in kilometers (`km`)**, not meters.
   - Always project `(lon, lat)` via `lonlat_to_utm45n_km(lon, lat)` (dividing standard UTM meters by `1000.0`) before indexing into `fp6a` (`x0=227.3030 km`, `dx=0.48703 km`, `y0=3028.9662 km`, `dy=0.48698 km`) or `cop30dem_channel_tagged_pixels_near.tif` (`ULX=224.789558 km`, `ULY=3184.377253 km`, `dx=dy=0.028428845 km`).

3. **JSON Serialization of `numpy.float32` Arrays**
   - Calling `np.round(float32_arr, 3).tolist()` in Python produces 64-bit floats with binary representation artifacts (`0.16000000834465027`), inflating embedded HTML/JSON bundle sizes.
   - Always round elements as Python `float` (`[[round(float(v), decimals) for v in row] for row in arr]`).

4. **PowerShell Inline Python Quirk with CSS Variables (`--border`)**
   - Do not pass multi-line HTML/CSS strings containing `--` (such as Tailwind `border-[var(--border)]`) inside `python -c "..."` in PowerShell, as PowerShell's parser treats `--` as the unary decrement operator even inside double quotes when nested quotes occur. Write a standalone `.py` script file and execute `python script.py` instead.

5. **Headless Chrome DevTools Recording & Standalone `ffmpeg` on Windows**
   - System `PATH` does not include `ffmpeg`; use `imageio_ffmpeg.get_ffmpeg_exe()` (`pip install imageio-ffmpeg`) to obtain a precompiled Windows `ffmpeg` binary.
   - When launching `chrome.exe --headless=new --remote-debugging-port=<port>` on Windows while a desktop Chrome session is already running, always pass an isolated `--user-data-dir=<temp_dir>`; otherwise Chrome attaches to the existing desktop session instead of opening an isolated headless viewport at the requested `--window-size`.
   - When printing HTML/JS lines containing Unicode math/scientific symbols (such as `μ` `\u03bc`, `²`, or `—`) from Python on Windows PowerShell, call `sys.stdout.reconfigure(encoding='utf-8')` first to avoid `UnicodeEncodeError: 'charmap' codec can't encode character` under `cp1252`.

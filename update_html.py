import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPACT_JSON = os.path.join(BASE_DIR, "data", "regions_3d_compact.json")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
ARTIFACT_HTML = r"C:\Users\mhs4118\.gemini\antigravity\brain\38ec0b63-c099-4411-a09e-791a249c2aa3\gorkha_landslides_3d_viewer.html"

with open(COMPACT_JSON, "r", encoding="utf-8") as f:
    compact_str = f.read().strip()

with open(ARTIFACT_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace EMBEDDED_DATA line
lines = html.splitlines()
for idx, line in enumerate(lines):
    if "const EMBEDDED_DATA =" in line:
        lines[idx] = f"    const EMBEDDED_DATA = {compact_str};"
        break
html = "\n".join(lines)

# 2. Update header & subtitle
html = html.replace(
    "Gorkha 2015 3D Terrain — Landslides + PGA &amp; MMI Ground Motion",
    "Gorkha 2015 3D Terrain — Landslides + fp6a Susceptibility + k_sn Steepness + PGA/MMI",
)
html = html.replace(
    "Valagussa_2021.shp + pga_mean.flt + mmi_mean.flt",
    "Valagussa_2021.shp + fp6a.gpkg + cop30dem_channel_tagged_pixels_near.tif + pga/mmi.flt",
)

# 3. Update KPI cards to show k_sn, fp6a Susceptibility, PGA/MMI, and Elevation
old_kpis = """      <!-- Region KPI Summary Cards -->
      <div class="grid grid-cols-2 gap-2">
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">Region PGA (g)</div>
          <div class="text-xs font-semibold font-mono text-rose-500 mt-0.5" id="stat-pga">0.565–0.680 g</div>
          <div class="text-xs font-mono text-[var(--muted-foreground)]" id="stat-pga-ln">ln: -0.57 to -0.39</div>
        </div>
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">Region MMI</div>
          <div class="text-xs font-semibold font-mono text-amber-500 mt-0.5" id="stat-mmi">MMI 7.82–8.16</div>
          <div class="text-xs font-mono text-[var(--muted-foreground)]" id="stat-count">249 / 249 slides</div>
        </div>
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">3D Elevation</div>
          <div class="text-xs font-semibold font-mono text-[var(--foreground)] mt-0.5" id="stat-elev">816–4,007 m</div>
        </div>
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">Slide Area / Slope</div>
          <div class="text-xs font-semibold font-mono text-[var(--foreground)] mt-0.5" id="stat-area">3.82 km² (31.6°)</div>
        </div>
      </div>"""

new_kpis = """      <!-- Region KPI Summary Cards -->
      <div class="grid grid-cols-2 gap-2">
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">Channel Steepness (k_sn)</div>
          <div class="text-xs font-semibold font-mono text-cyan-400 mt-0.5" id="stat-ksn">240–2,610</div>
          <div class="text-xs font-mono text-[var(--muted-foreground)]" id="stat-ksn-med">Med: 691 · P90: 1,412</div>
        </div>
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">Bayesian Susc. (fp6a)</div>
          <div class="text-xs font-semibold font-mono text-fuchsia-400 mt-0.5" id="stat-susc">0.16–12.39</div>
          <div class="text-xs font-mono text-[var(--muted-foreground)]" id="stat-count">249 / 249 slides</div>
        </div>
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">PGA / MMI (.flt)</div>
          <div class="text-xs font-semibold font-mono text-rose-500 mt-0.5" id="stat-pga">0.565–0.687 g</div>
          <div class="text-xs font-mono text-amber-500" id="stat-mmi">MMI 7.82–8.16</div>
        </div>
        <div class="border border-[var(--border)] rounded-lg p-2 bg-[var(--background)]">
          <div class="text-xs text-[var(--muted-foreground)]">3D Elev / Area</div>
          <div class="text-xs font-semibold font-mono text-[var(--foreground)] mt-0.5" id="stat-elev">828–4,013 m</div>
          <div class="text-xs font-mono text-[var(--muted-foreground)]" id="stat-area">3.82 km² (31.6°)</div>
        </div>
      </div>"""
assert old_kpis in html, "old_kpis not found"
html = html.replace(old_kpis, new_kpis)

# 4. Update terrain-theme options and color-mode options
old_theme_select = """          <select id="terrain-theme" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] px-2.5 py-1.5 font-medium">
            <option value="pga" selected>PGA Ground Motion (pga_mean.flt) + Hillshade</option>
            <option value="mmi">MMI Intensity (mmi_mean.flt) + Hillshade</option>
            <option value="hypso">Hypsometric Elevation + Hillshade</option>
            <option value="slope">Terrain Slope Steepness Heatmap</option>
            <option value="dark">Dark Relief (High-Contrast Base)</option>
            <option value="wire">3D Topographic Wireframe</option>
          </select>"""

new_theme_select = """          <select id="terrain-theme" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] px-2.5 py-1.5 font-medium">
            <option value="ksn" selected>Channel Steepness k_sn (cop30dem_..._near.tif) + Hillshade</option>
            <option value="susc_log">Bayesian Susceptibility (fp6a.gpkg — Log10 μ) + Hillshade</option>
            <option value="susc_lin">Bayesian Susceptibility Hotspots (fp6a.gpkg — Linear μ)</option>
            <option value="susc_sd">Bayesian Posterior Uncertainty (fp6a.gpkg — SD)</option>
            <option value="pga">PGA Ground Motion (pga_mean.flt) + Hillshade</option>
            <option value="mmi">MMI Intensity (mmi_mean.flt) + Hillshade</option>
            <option value="hypso">Hypsometric Elevation + Hillshade</option>
            <option value="slope">Terrain Slope Steepness Heatmap</option>
            <option value="dark">Dark Relief (High-Contrast Base)</option>
            <option value="wire">3D Topographic Wireframe</option>
          </select>"""
assert old_theme_select in html, "old_theme_select not found"
html = html.replace(old_theme_select, new_theme_select)

old_color_select = """          <select id="color-mode" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] px-2.5 py-1.5">
            <option value="area" selected>Landslide Area (m², log scale)</option>
            <option value="pga">Landslide PGA (g, from pga_mean.flt)</option>
            <option value="mmi">Landslide MMI (from mmi_mean.flt)</option>
            <option value="relief">Vertical Drop ΔZ (Crown to Toe, m)</option>
            <option value="elev">Mean Elevation (m a.s.l.)</option>
            <option value="slope">Local Terrain Slope (°)</option>
          </select>"""

new_color_select = """          <select id="color-mode" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] px-2.5 py-1.5">
            <option value="ksn" selected>Channel Steepness Index (k_sn, GeoTIFF)</option>
            <option value="susc">Bayesian Susceptibility (fp6a.gpkg Mean μ)</option>
            <option value="susc_sd">Bayesian Uncertainty (fp6a.gpkg SD)</option>
            <option value="area">Landslide Area (m², log scale)</option>
            <option value="pga">Landslide PGA (g, from pga_mean.flt)</option>
            <option value="mmi">Landslide MMI (from mmi_mean.flt)</option>
            <option value="relief">Vertical Drop ΔZ (Crown to Toe, m)</option>
            <option value="elev">Mean Elevation (m a.s.l.)</option>
            <option value="slope">Local Terrain Slope (°)</option>
          </select>"""
assert old_color_select in html, "old_color_select not found"
html = html.replace(old_color_select, new_color_select)

# 5. Update quick toolbar buttons to include k_sn and fp6a Susceptibility
old_quick_btns = """        <button id="btn-quick-pga" class="px-2.5 py-1 rounded-lg text-xs font-semibold border border-rose-500 bg-rose-500/15 text-[var(--foreground)]">
          3D PGA Surface
        </button>
        <button id="btn-quick-mmi" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
          3D MMI Surface
        </button>
        <button id="btn-quick-hypso" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
          3D Elevation
        </button>"""

new_quick_btns = """        <button id="btn-quick-ksn" class="px-2.5 py-1 rounded-lg text-xs font-semibold border border-cyan-400 bg-cyan-500/15 text-[var(--foreground)]">
          3D k_sn Steepness
        </button>
        <button id="btn-quick-susc" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
          3D fp6a Susc.
        </button>
        <button id="btn-quick-pga" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
          3D PGA Surface
        </button>
        <button id="btn-quick-mmi" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
          3D MMI Surface
        </button>
        <button id="btn-quick-hypso" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
          3D Elevation
        </button>"""
assert old_quick_btns in html, "old_quick_btns not found"
html = html.replace(old_quick_btns, new_quick_btns)

# 6. Add k_sn and fp6a Inspector row in Right Sidebar
old_insp_cards = """          <!-- Ground Motion (PGA & MMI) Highlight Row -->
          <div class="grid grid-cols-2 gap-1.5 text-xs">
            <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-2">
              <span class="text-[var(--muted-foreground)] block">PGA (pga_mean.flt)</span>
              <span class="font-mono font-bold text-rose-500" id="insp-pga">0.642 g</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)] block" id="insp-pga-ln">ln(PGA) = -0.44</span>
            </div>
            <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-2">
              <span class="text-[var(--muted-foreground)] block">MMI (mmi_mean.flt)</span>
              <span class="font-mono font-bold text-amber-500" id="insp-mmi">MMI 8.05</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)] block">Severe–Violent</span>
            </div>
          </div>"""

new_insp_cards = """          <!-- Channel Steepness (k_sn) & Bayesian Susceptibility (fp6a) Row -->
          <div class="grid grid-cols-2 gap-1.5 text-xs">
            <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-2">
              <span class="text-[var(--muted-foreground)] block">Channel Steepness k_sn</span>
              <span class="font-mono font-bold text-cyan-400" id="insp-ksn">685 m^0.9</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)] block" id="insp-ksn-max">Max on ring: 940</span>
            </div>
            <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-2">
              <span class="text-[var(--muted-foreground)] block">Bayesian Susc. (fp6a)</span>
              <span class="font-mono font-bold text-fuchsia-400" id="insp-susc">μ = 3.420</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)] block" id="insp-susc-sd">SD 0.45 · q97.5: 4.81</span>
            </div>
          </div>

          <!-- Ground Motion (PGA & MMI) Highlight Row -->
          <div class="grid grid-cols-2 gap-1.5 text-xs">
            <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-2">
              <span class="text-[var(--muted-foreground)] block">PGA (pga_mean.flt)</span>
              <span class="font-mono font-bold text-rose-500" id="insp-pga">0.642 g</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)] block" id="insp-pga-ln">ln(PGA) = -0.44</span>
            </div>
            <div class="bg-[var(--background)] border border-[var(--border)] rounded-lg p-2">
              <span class="text-[var(--muted-foreground)] block">MMI (mmi_mean.flt)</span>
              <span class="font-mono font-bold text-amber-500" id="insp-mmi">MMI 8.05</span>
              <span class="font-mono text-xs text-[var(--muted-foreground)] block">Severe–Violent</span>
            </div>
          </div>"""
assert old_insp_cards in html, "old_insp_cards not found"
html = html.replace(old_insp_cards, new_insp_cards)

# 7. Update JS state defaults & prepareRegion vertex/feature decoding
html = html.replace(
    """        colorMode: 'area',
        terrainTheme: 'pga',     // Default directly to PGA mapped on 3D terrain!""",
    """        colorMode: 'ksn',
        terrainTheme: 'ksn',     // Default directly to Channel Steepness Index k_sn on 3D terrain!""",
)

html = html.replace(
    """        const pgaGrid = reg.pga_g;
        const mmiGrid = reg.mmi;""",
    """        const pgaGrid = reg.pga_g;
        const mmiGrid = reg.mmi;
        const suscMeanGrid = reg.susc_mean;
        const suscSdGrid = reg.susc_sd;
        const ksnGrid = reg.ksn;""",
)

html = html.replace(
    """              zM: dem[r][c],
              pga: pgaGrid[r][c],
              mmi: mmiGrid[r][c]""",
    """              zM: dem[r][c],
              pga: pgaGrid[r][c],
              mmi: mmiGrid[r][c],
              suscMean: suscMeanGrid[r][c],
              suscSd: suscSdGrid[r][c],
              ksn: ksnGrid[r][c]""",
)

html = html.replace(
    """            pga_g: f.pg,
            pga_ln: f.pl,
            mmi: f.mm,
            vol_m3: f.v,""",
    """            pga_g: f.pg,
            pga_ln: f.pl,
            mmi: f.mm,
            susc_mean: f.sm,
            susc_log10: f.slg,
            susc_sd: f.ssd,
            susc_q975: f.sq9,
            ksn: f.ks,
            ksn_max: f.ksm,
            vol_m3: f.v,""",
)

# 8. Add ksnRGB & suscRGB color ramps and update getFeatureColor + getTerrainQuadColor
old_color_funcs = """      function getFeatureColor(f, regData, alpha) {
        const st = regData.meta.stats;
        let t = 0.5;
        if (state.colorMode === 'area') {
          const logA = Math.log10(Math.max(50, f.area_m2));
          t = (logA - 1.7) / (5.3 - 1.7);
        } else if (state.colorMode === 'pga') {
          const pMin = state.shakeScale === 'local' ? st.pga_min_g : 0.15;
          const pMax = state.shakeScale === 'local' ? st.pga_max_g : 0.80;
          t = (f.pga_g - pMin) / Math.max(0.01, pMax - pMin);
        } else if (state.colorMode === 'mmi') {
          const mMin = state.shakeScale === 'local' ? st.mmi_min : 6.0;
          const mMax = state.shakeScale === 'local' ? st.mmi_max : 8.7;
          t = (f.mmi - mMin) / Math.max(0.05, mMax - mMin);
        } else if (state.colorMode === 'relief') {
          t = f.relief_m / 450;
        } else if (state.colorMode === 'elev') {
          t = (f.elev_mean - regData.zMin) / Math.max(100, regData.zMax - regData.zMin);
        } else if (state.colorMode === 'slope') {
          t = (f.slope_deg - 15) / 35;
        }
        return polyColor(t, alpha);
      }

      function getTerrainQuadColor(zM, pgaG, mmiVal, slopeDeg, shade, regData, isLight) {
        const st = regData.meta.stats;
        const lightFactor = 0.42 + 0.68 * shade;

        if (state.terrainTheme === 'pga') {
          const pMin = state.shakeScale === 'local' ? st.pga_min_g : 0.15;
          const pMax = state.shakeScale === 'local' ? st.pga_max_g : 0.80;
          const t = (pgaG - pMin) / Math.max(0.005, pMax - pMin);
          const [r, g, b] = shakeMapRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }

        if (state.terrainTheme === 'mmi') {
          const mMin = state.shakeScale === 'local' ? st.mmi_min : 6.0;
          const mMax = state.shakeScale === 'local' ? st.mmi_max : 8.7;
          const t = (mmiVal - mMin) / Math.max(0.02, mMax - mMin);
          const [r, g, b] = shakeMapRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }"""

new_color_funcs = """      // Channel Steepness k_sn Turbo/Viridis-inspired ramp: Deep Navy -> Teal -> Emerald -> Amber -> Crimson
      function ksnRGB(t) {
        t = Math.max(0, Math.min(1, t));
        let r, g, b;
        if (t < 0.25) {
          const u = t / 0.25;
          r = 15 + u * (6 - 15);
          g = 35 + u * (182 - 35);
          b = 110 + u * (212 - 110);
        } else if (t < 0.52) {
          const u = (t - 0.25) / 0.27;
          r = 6 + u * (132 - 6);
          g = 182 + u * (204 - 182);
          b = 212 + u * (22 - 212);
        } else if (t < 0.78) {
          const u = (t - 0.52) / 0.26;
          r = 132 + u * (249 - 132);
          g = 204 + u * (115 - 204);
          b = 22 + u * (22 - 22);
        } else {
          const u = (t - 0.78) / 0.22;
          r = 249 + u * (225 - 249);
          g = 115 + u * (29 - 115);
          b = 22 + u * (72 - 22);
        }
        return [r, g, b];
      }

      // Bayesian Susceptibility (fp6a.gpkg) Inferno/Plasma ramp: Deep Indigo -> Purple -> Magenta -> Orange -> Bright Gold
      function suscRGB(t) {
        t = Math.max(0, Math.min(1, t));
        let r, g, b;
        if (t < 0.28) {
          const u = t / 0.28;
          r = 22 + u * (107 - 22);
          g = 16 + u * (33 - 16);
          b = 68 + u * (168 - 68);
        } else if (t < 0.58) {
          const u = (t - 0.28) / 0.30;
          r = 107 + u * (219 - 107);
          g = 33 + u * (39 - 33);
          b = 168 + u * (119 - 168);
        } else if (t < 0.82) {
          const u = (t - 0.58) / 0.24;
          r = 219 + u * (249 - 219);
          g = 39 + u * (115 - 39);
          b = 119 + u * (22 - 119);
        } else {
          const u = (t - 0.82) / 0.18;
          r = 249 + u * (254 - 249);
          g = 115 + u * (240 - 115);
          b = 22 + u * (138 - 22);
        }
        return [r, g, b];
      }

      function getFeatureColor(f, regData, alpha) {
        const st = regData.meta.stats;
        let t = 0.5;
        if (state.colorMode === 'ksn') {
          const kMin = state.shakeScale === 'local' ? st.ksn_min : 50;
          const kMax = state.shakeScale === 'local' ? Math.max(kMin + 50, st.ksn_p90 * 1.25) : 1600;
          t = (f.ksn - kMin) / Math.max(10, kMax - kMin);
        } else if (state.colorMode === 'susc') {
          const sMin = state.shakeScale === 'local' ? st.susc_log10_min : -2.0;
          const sMax = state.shakeScale === 'local' ? st.susc_log10_max : 1.3;
          t = (f.susc_log10 - sMin) / Math.max(0.1, sMax - sMin);
        } else if (state.colorMode === 'susc_sd') {
          t = (f.susc_sd - st.susc_sd_min) / Math.max(0.05, st.susc_sd_max - st.susc_sd_min);
        } else if (state.colorMode === 'area') {
          const logA = Math.log10(Math.max(50, f.area_m2));
          t = (logA - 1.7) / (5.3 - 1.7);
        } else if (state.colorMode === 'pga') {
          const pMin = state.shakeScale === 'local' ? st.pga_min_g : 0.15;
          const pMax = state.shakeScale === 'local' ? st.pga_max_g : 0.80;
          t = (f.pga_g - pMin) / Math.max(0.01, pMax - pMin);
        } else if (state.colorMode === 'mmi') {
          const mMin = state.shakeScale === 'local' ? st.mmi_min : 6.0;
          const mMax = state.shakeScale === 'local' ? st.mmi_max : 8.7;
          t = (f.mmi - mMin) / Math.max(0.05, mMax - mMin);
        } else if (state.colorMode === 'relief') {
          t = f.relief_m / 450;
        } else if (state.colorMode === 'elev') {
          t = (f.elev_mean - regData.zMin) / Math.max(100, regData.zMax - regData.zMin);
        } else if (state.colorMode === 'slope') {
          t = (f.slope_deg - 15) / 35;
        }
        return polyColor(t, alpha);
      }

      function getTerrainQuadColor(zM, pgaG, mmiVal, suscMean, suscSd, ksnVal, slopeDeg, shade, regData, isLight) {
        const st = regData.meta.stats;
        const lightFactor = 0.42 + 0.68 * shade;

        if (state.terrainTheme === 'ksn') {
          const kMin = state.shakeScale === 'local' ? st.ksn_min : 50;
          const kMax = state.shakeScale === 'local' ? Math.max(kMin + 50, st.ksn_p90 * 1.25) : 1600;
          const t = (ksnVal - kMin) / Math.max(10, kMax - kMin);
          const [r, g, b] = ksnRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }

        if (state.terrainTheme === 'susc_log' || state.terrainTheme === 'susc_lin') {
          let t;
          if (state.terrainTheme === 'susc_log') {
            const logVal = Math.log10(Math.max(1e-5, suscMean));
            const sMin = state.shakeScale === 'local' ? st.susc_log10_min : -2.0;
            const sMax = state.shakeScale === 'local' ? st.susc_log10_max : 1.3;
            t = (logVal - sMin) / Math.max(0.1, sMax - sMin);
          } else {
            const sMin = state.shakeScale === 'local' ? st.susc_min : 0.0;
            const sMax = state.shakeScale === 'local' ? Math.max(0.5, st.susc_max * 0.75) : 10.0;
            t = (suscMean - sMin) / Math.max(0.05, sMax - sMin);
          }
          const [r, g, b] = suscRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }

        if (state.terrainTheme === 'susc_sd') {
          const t = (suscSd - st.susc_sd_min) / Math.max(0.02, st.susc_sd_max - st.susc_sd_min);
          const [r, g, b] = suscRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }

        if (state.terrainTheme === 'pga') {
          const pMin = state.shakeScale === 'local' ? st.pga_min_g : 0.15;
          const pMax = state.shakeScale === 'local' ? st.pga_max_g : 0.80;
          const t = (pgaG - pMin) / Math.max(0.005, pMax - pMin);
          const [r, g, b] = shakeMapRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }

        if (state.terrainTheme === 'mmi') {
          const mMin = state.shakeScale === 'local' ? st.mmi_min : 6.0;
          const mMax = state.shakeScale === 'local' ? st.mmi_max : 8.7;
          const t = (mmiVal - mMin) / Math.max(0.02, mMax - mMin);
          const [r, g, b] = shakeMapRGB(t);
          return `rgb(${Math.min(255, Math.round(r * lightFactor))},${Math.min(255, Math.round(g * lightFactor))},${Math.min(255, Math.round(b * lightFactor))})`;
        }"""
assert old_color_funcs in html, "old_color_funcs not found"
html = html.replace(old_color_funcs, new_color_funcs)

# 9. Update drawMinimap to support k_sn, fp6a susceptibility, MMI, and PGA
old_minimap_block = """        // Render overview PGA or MMI heatmap from DATA.overview
        if (DATA.overview && DATA.overview.pga_g) {
          const useMMI = state.terrainTheme === 'mmi' || state.colorMode === 'mmi';
          document.getElementById('minimap-title').textContent =
            useMMI ? 'Nepal Rupture Map (MMI Heatmap)' : 'Nepal Rupture Map (PGA Heatmap)';
          const grid = useMMI ? DATA.overview.mmi : DATA.overview.pga_g;
          const gs = DATA.overview.grid_size;
          const cellW = (w - 16) / gs;
          const cellH = (h - 16) / gs;
          for (let r = 0; r < gs; r++) {
            for (let c = 0; c < gs; c++) {
              const val = grid[r][c];
              const t = useMMI ? (val - 5.5) / (8.7 - 5.5) : (val - 0.10) / (0.80 - 0.10);
              const [cr, cg, cb] = shakeMapRGB(t);
              miniCtx.fillStyle = `rgba(${Math.round(cr)},${Math.round(cg)},${Math.round(cb)},0.55)`;
              const px = 8 + c * cellW;
              const py = 8 + (gs - 1 - r) * cellH;
              miniCtx.fillRect(px, py, Math.ceil(cellW), Math.ceil(cellH));
            }
          }
        }"""

new_minimap_block = """        // Render overview k_sn, fp6a Susceptibility, MMI, or PGA heatmap from DATA.overview
        if (DATA.overview && DATA.overview.pga_g) {
          const useKsn = state.terrainTheme === 'ksn' || state.colorMode === 'ksn';
          const useSusc = state.terrainTheme.startsWith('susc') || state.colorMode.startsWith('susc');
          const useMMI = state.terrainTheme === 'mmi' || state.colorMode === 'mmi';
          const titleEl = document.getElementById('minimap-title');
          if (useKsn) titleEl.textContent = 'Nepal Overview (k_sn Steepness)';
          else if (useSusc) titleEl.textContent = 'Nepal Overview (fp6a Susceptibility)';
          else if (useMMI) titleEl.textContent = 'Nepal Overview (MMI Heatmap)';
          else titleEl.textContent = 'Nepal Overview (PGA Heatmap)';

          const grid = useKsn ? DATA.overview.ksn : (useSusc ? DATA.overview.susc_mean : (useMMI ? DATA.overview.mmi : DATA.overview.pga_g));
          const gs = DATA.overview.grid_size;
          const cellW = (w - 16) / gs;
          const cellH = (h - 16) / gs;
          for (let r = 0; r < gs; r++) {
            for (let c = 0; c < gs; c++) {
              const val = grid[r][c];
              if (val < 0) continue;
              let rgb;
              if (useKsn) {
                rgb = ksnRGB((val - 50) / 1400);
              } else if (useSusc) {
                rgb = suscRGB((Math.log10(Math.max(1e-4, val)) + 2.2) / 3.4);
              } else if (useMMI) {
                rgb = shakeMapRGB((val - 5.5) / (8.7 - 5.5));
              } else {
                rgb = shakeMapRGB((val - 0.10) / (0.80 - 0.10));
              }
              miniCtx.fillStyle = `rgba(${Math.round(rgb[0])},${Math.round(rgb[1])},${Math.round(rgb[2])},0.62)`;
              const px = 8 + c * cellW;
              const py = 8 + (gs - 1 - r) * cellH;
              miniCtx.fillRect(px, py, Math.ceil(cellW), Math.ceil(cellH));
            }
          }
        }"""
assert old_minimap_block in html, "old_minimap_block not found"
html = html.replace(old_minimap_block, new_minimap_block)

# 10. Update render3D quad averaging and getTerrainQuadColor call
html = html.replace(
    """            const pgaAvg = 0.25 * (v00.pga + v10.pga + v11.pga + v01.pga);
            const mmiAvg = 0.25 * (v00.mmi + v10.mmi + v11.mmi + v01.mmi);
            const [nx, ny, nz] = regData.normals[r][c];
            const shade = Math.max(0, nx * sunX + ny * sunY + nz * sunZ);
            renderables.push({
              type: 'quad',
              depth: avgDepth,
              p00, p10, p11, p01,
              zAvg,
              pgaAvg,
              mmiAvg,
              slope: regData.slopes[r][c],
              shade
            });""",
    """            const pgaAvg = 0.25 * (v00.pga + v10.pga + v11.pga + v01.pga);
            const mmiAvg = 0.25 * (v00.mmi + v10.mmi + v11.mmi + v01.mmi);
            const suscAvg = 0.25 * (v00.suscMean + v10.suscMean + v11.suscMean + v01.suscMean);
            const suscSdAvg = 0.25 * (v00.suscSd + v10.suscSd + v11.suscSd + v01.suscSd);
            const ksnAvg = 0.25 * (v00.ksn + v10.ksn + v11.ksn + v01.ksn);
            const [nx, ny, nz] = regData.normals[r][c];
            const shade = Math.max(0, nx * sunX + ny * sunY + nz * sunZ);
            renderables.push({
              type: 'quad',
              depth: avgDepth,
              p00, p10, p11, p01,
              zAvg,
              pgaAvg,
              mmiAvg,
              suscAvg,
              suscSdAvg,
              ksnAvg,
              slope: regData.slopes[r][c],
              shade
            });""",
)

html = html.replace(
    "const { p00, p10, p11, p01, zAvg, pgaAvg, mmiAvg, slope, shade } = item;",
    "const { p00, p10, p11, p01, zAvg, pgaAvg, mmiAvg, suscAvg, suscSdAvg, ksnAvg, slope, shade } = item;",
)
html = html.replace(
    "const col = getTerrainQuadColor(zAvg, pgaAvg, mmiAvg, slope, shade, regData, isLight);",
    "const col = getTerrainQuadColor(zAvg, pgaAvg, mmiAvg, suscAvg, suscSdAvg, ksnAvg, slope, shade, regData, isLight);",
)

# 11. Update selectFeature, populateFeatureList, updateLegendLabels, selectRegion, tooltip, and quick buttons
old_select_feat = """        document.getElementById('insp-fid').textContent = `FID #${f.fid}`;
        document.getElementById('insp-area').textContent = `${f.area_m2.toLocaleString()} m²`;
        document.getElementById('insp-pga').textContent = `${f.pga_g.toFixed(3)} g`;
        document.getElementById('insp-pga-ln').textContent = `ln(PGA) = ${f.pga_ln.toFixed(2)}`;
        document.getElementById('insp-mmi').textContent = `MMI ${f.mmi.toFixed(2)}`;"""

new_select_feat = """        document.getElementById('insp-fid').textContent = `FID #${f.fid}`;
        document.getElementById('insp-area').textContent = `${f.area_m2.toLocaleString()} m²`;
        document.getElementById('insp-ksn').textContent = `k_sn = ${f.ksn}`;
        document.getElementById('insp-ksn-max').textContent = `Max on ring: ${f.ksn_max}`;
        document.getElementById('insp-susc').textContent = `μ = ${f.susc_mean.toFixed(3)} (log ${f.susc_log10.toFixed(2)})`;
        document.getElementById('insp-susc-sd').textContent = `SD ${f.susc_sd.toFixed(2)} · q97.5: ${f.susc_q975.toFixed(2)}`;
        document.getElementById('insp-pga').textContent = `${f.pga_g.toFixed(3)} g`;
        document.getElementById('insp-pga-ln').textContent = `ln(PGA) = ${f.pga_ln.toFixed(2)}`;
        document.getElementById('insp-mmi').textContent = `MMI ${f.mmi.toFixed(2)}`;"""
assert old_select_feat in html, "old_select_feat not found"
html = html.replace(old_select_feat, new_select_feat)

html = html.replace(
    """              <span class="block text-[var(--muted-foreground)] font-mono">PGA ${f.pga_g.toFixed(2)}g · MMI ${f.mmi.toFixed(1)}</span>""",
    """              <span class="block text-[var(--muted-foreground)] font-mono">k_sn ${f.ksn} · fp6a ${f.susc_mean.toFixed(2)} · ${f.pga_g.toFixed(2)}g</span>""",
)

old_legend_fn = """        if (state.terrainTheme === 'mmi') {
          const m0 = state.shakeScale === 'local' ? st.mmi_min : 6.0;
          const m1 = state.shakeScale === 'local' ? st.mmi_max : 8.7;
          tTitle.textContent = '3D Terrain MMI (mmi_mean.flt)';
          tMin.textContent = `MMI ${m0.toFixed(2)}`;
          tMid.textContent = `MMI ${(0.5 * (m0 + m1)).toFixed(2)}`;
          tMax.textContent = `MMI ${m1.toFixed(2)}`;
        } else {
          const p0 = state.shakeScale === 'local' ? st.pga_min_g : 0.15;
          const p1 = state.shakeScale === 'local' ? st.pga_max_g : 0.80;
          tTitle.textContent = '3D Terrain PGA (pga_mean.flt)';
          tMin.textContent = `${p0.toFixed(3)} g`;
          tMid.textContent = `${(0.5 * (p0 + p1)).toFixed(3)} g`;
          tMax.textContent = `${p1.toFixed(3)} g`;
        }"""

new_legend_fn = """        const tBar = document.getElementById('terrain-legend-bar');
        if (state.terrainTheme === 'ksn') {
          const k0 = state.shakeScale === 'local' ? st.ksn_min : 50;
          const k1 = state.shakeScale === 'local' ? Math.max(k0 + 50, st.ksn_p90 * 1.25) : 1600;
          tTitle.textContent = '3D Terrain Channel Steepness (k_sn)';
          tBar.style.background = 'linear-gradient(90deg, #0f236e, #06b6d4, #84cc16, #f97316, #e11d48)';
          tMin.textContent = `k_sn ${Math.round(k0)}`;
          tMid.textContent = `k_sn ${Math.round(0.5 * (k0 + k1))}`;
          tMax.textContent = `k_sn ${Math.round(k1)}`;
        } else if (state.terrainTheme.startsWith('susc')) {
          tTitle.textContent = state.terrainTheme === 'susc_sd' ? '3D Terrain fp6a Posterior SD' : '3D Terrain Bayesian Susc. (fp6a.gpkg)';
          tBar.style.background = 'linear-gradient(90deg, #161044, #6b21a8, #db2777, #f97316, #fef08a)';
          tMin.textContent = `μ ${st.susc_min.toFixed(3)}`;
          tMid.textContent = `Med ${st.susc_median.toFixed(2)}`;
          tMax.textContent = `Max ${st.susc_max.toFixed(2)}`;
        } else if (state.terrainTheme === 'mmi') {
          const m0 = state.shakeScale === 'local' ? st.mmi_min : 6.0;
          const m1 = state.shakeScale === 'local' ? st.mmi_max : 8.7;
          tTitle.textContent = '3D Terrain MMI (mmi_mean.flt)';
          tBar.style.background = 'linear-gradient(90deg, #2563eb, #06b6d4, #eab308, #f97316, #dc2626, #7f1d1d)';
          tMin.textContent = `MMI ${m0.toFixed(2)}`;
          tMid.textContent = `MMI ${(0.5 * (m0 + m1)).toFixed(2)}`;
          tMax.textContent = `MMI ${m1.toFixed(2)}`;
        } else {
          const p0 = state.shakeScale === 'local' ? st.pga_min_g : 0.15;
          const p1 = state.shakeScale === 'local' ? st.pga_max_g : 0.80;
          tTitle.textContent = '3D Terrain PGA (pga_mean.flt)';
          tBar.style.background = 'linear-gradient(90deg, #2563eb, #06b6d4, #eab308, #f97316, #dc2626, #7f1d1d)';
          tMin.textContent = `${p0.toFixed(3)} g`;
          tMid.textContent = `${(0.5 * (p0 + p1)).toFixed(3)} g`;
          tMax.textContent = `${p1.toFixed(3)} g`;
        }"""
assert old_legend_fn in html, "old_legend_fn not found"
html = html.replace(old_legend_fn, new_legend_fn)

old_poly_leg = """        if (state.colorMode === 'area') {
          minEl.textContent = '50 m²'; midEl.textContent = '5,000 m²'; maxEl.textContent = '200,000+ m²';"""

new_poly_leg = """        if (state.colorMode === 'ksn') {
          const k0 = state.shakeScale === 'local' ? st.ksn_min : 50;
          const k1 = state.shakeScale === 'local' ? Math.max(k0 + 50, st.ksn_p90 * 1.25) : 1600;
          minEl.textContent = `k_sn ${Math.round(k0)}`; midEl.textContent = `k_sn ${Math.round(0.5 * (k0 + k1))}`; maxEl.textContent = `k_sn ${Math.round(k1)}`;
        } else if (state.colorMode === 'susc') {
          minEl.textContent = `μ ${st.susc_min.toFixed(2)}`; midEl.textContent = `Med ${st.susc_median.toFixed(2)}`; maxEl.textContent = `Max ${st.susc_max.toFixed(1)}`;
        } else if (state.colorMode === 'susc_sd') {
          minEl.textContent = `SD ${st.susc_sd_min.toFixed(2)}`; midEl.textContent = `SD ${(0.5*(st.susc_sd_min+st.susc_sd_max)).toFixed(2)}`; maxEl.textContent = `SD ${st.susc_sd_max.toFixed(2)}`;
        } else if (state.colorMode === 'area') {
          minEl.textContent = '50 m²'; midEl.textContent = '5,000 m²'; maxEl.textContent = '200,000+ m²';"""
assert old_poly_leg in html, "old_poly_leg not found"
html = html.replace(old_poly_leg, new_poly_leg)

old_qbtn_update = """        // Update quick surface buttons
        const qPga = document.getElementById('btn-quick-pga');
        const qMmi = document.getElementById('btn-quick-mmi');
        const qHyp = document.getElementById('btn-quick-hypso');
        const activeCls = 'px-2.5 py-1 rounded-lg text-xs font-semibold border border-rose-500 bg-rose-500/15 text-[var(--foreground)]';
        const idleCls = 'px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)] text-[var(--muted-foreground)]';
        qPga.className = state.terrainTheme === 'pga' ? activeCls : idleCls;
        qMmi.className = state.terrainTheme === 'mmi' ? activeCls : idleCls;
        qHyp.className = state.terrainTheme === 'hypso' ? activeCls : idleCls;"""

new_qbtn_update = """        // Update quick surface buttons
        const qKsn = document.getElementById('btn-quick-ksn');
        const qSusc = document.getElementById('btn-quick-susc');
        const qPga = document.getElementById('btn-quick-pga');
        const qMmi = document.getElementById('btn-quick-mmi');
        const qHyp = document.getElementById('btn-quick-hypso');
        const activeCls = 'px-2.5 py-1 rounded-lg text-xs font-semibold border border-cyan-400 bg-cyan-500/15 text-[var(--foreground)]';
        const idleCls = 'px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)] text-[var(--muted-foreground)]';
        qKsn.className = state.terrainTheme === 'ksn' ? activeCls : idleCls;
        qSusc.className = state.terrainTheme.startsWith('susc') ? activeCls : idleCls;
        qPga.className = state.terrainTheme === 'pga' ? activeCls : idleCls;
        qMmi.className = state.terrainTheme === 'mmi' ? activeCls : idleCls;
        qHyp.className = state.terrainTheme === 'hypso' ? activeCls : idleCls;"""
assert old_qbtn_update in html, "old_qbtn_update not found"
html = html.replace(old_qbtn_update, new_qbtn_update)

old_stats_update = """        document.getElementById('stat-pga').textContent = `${st.pga_min_g.toFixed(3)}–${st.pga_max_g.toFixed(3)} g`;
        document.getElementById('stat-pga-ln').textContent = `ln: ${st.pga_ln_min.toFixed(2)} to ${st.pga_ln_max.toFixed(2)}`;
        document.getElementById('stat-mmi').textContent = `MMI ${st.mmi_min.toFixed(2)}–${st.mmi_max.toFixed(2)}`;
        document.getElementById('stat-elev').textContent = `${st.elev_min_m.toLocaleString()}–${st.elev_max_m.toLocaleString()} m`;
        document.getElementById('stat-area').textContent = `${st.total_area_km2} km² (${st.mean_slope_deg}°)`;"""

new_stats_update = """        document.getElementById('stat-ksn').textContent = `${st.ksn_min.toFixed(0)}–${st.ksn_max.toFixed(0)}`;
        document.getElementById('stat-ksn-med').textContent = `Med: ${st.ksn_median.toFixed(0)} · P90: ${st.ksn_p90.toFixed(0)}`;
        document.getElementById('stat-susc').textContent = `μ ${st.susc_min.toFixed(2)}–${st.susc_max.toFixed(2)}`;
        document.getElementById('stat-pga').textContent = `${st.pga_min_g.toFixed(3)}–${st.pga_max_g.toFixed(3)} g`;
        document.getElementById('stat-mmi').textContent = `MMI ${st.mmi_min.toFixed(2)}–${st.mmi_max.toFixed(2)}`;
        document.getElementById('stat-elev').textContent = `${st.elev_min_m.toLocaleString()}–${st.elev_max_m.toLocaleString()} m`;
        document.getElementById('stat-area').textContent = `${st.total_area_km2} km² (${st.mean_slope_deg}°)`;"""
assert old_stats_update in html, "old_stats_update not found"
html = html.replace(old_stats_update, new_stats_update)

old_tooltip = """              <div class="font-mono font-bold text-amber-500">FID #${hit.fid} · ${hit.area_m2.toLocaleString()} m²</div>
              <div class="font-mono text-rose-400">PGA: ${hit.pga_g.toFixed(3)} g (ln ${hit.pga_ln.toFixed(2)}) · MMI: ${hit.mmi.toFixed(2)}</div>
              <div class="text-[var(--muted-foreground)]">Elev: ${hit.elev_min}–${hit.elev_max} m (ΔZ ${hit.relief_m}m, ${hit.slope_deg}°)</div>"""

new_tooltip = """              <div class="font-mono font-bold text-amber-500">FID #${hit.fid} · ${hit.area_m2.toLocaleString()} m²</div>
              <div class="font-mono text-cyan-400">k_sn: ${hit.ksn} (max ${hit.ksn_max}) · fp6a μ: ${hit.susc_mean.toFixed(3)}</div>
              <div class="font-mono text-rose-400">PGA: ${hit.pga_g.toFixed(3)} g · MMI: ${hit.mmi.toFixed(2)}</div>
              <div class="text-[var(--muted-foreground)]">Elev: ${hit.elev_min}–${hit.elev_max} m (ΔZ ${hit.relief_m}m, ${hit.slope_deg}°)</div>"""
assert old_tooltip in html, "old_tooltip not found"
html = html.replace(old_tooltip, new_tooltip)

old_qbtn_listeners = """      document.getElementById('btn-quick-pga').addEventListener('click', () => {"""
new_qbtn_listeners = """      document.getElementById('btn-quick-ksn').addEventListener('click', () => {
        state.terrainTheme = 'ksn';
        document.getElementById('terrain-theme').value = 'ksn';
        updateLegendLabels(prepareRegion(state.regionId));
        drawMinimap();
        render3D();
      });

      document.getElementById('btn-quick-susc').addEventListener('click', () => {
        state.terrainTheme = 'susc_log';
        document.getElementById('terrain-theme').value = 'susc_log';
        updateLegendLabels(prepareRegion(state.regionId));
        drawMinimap();
        render3D();
      });

      document.getElementById('btn-quick-pga').addEventListener('click', () => {"""
assert old_qbtn_listeners in html, "old_qbtn_listeners not found"
html = html.replace(old_qbtn_listeners, new_qbtn_listeners)

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)
with open(ARTIFACT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated index.html and gorkha_landslides_3d_viewer.html!")

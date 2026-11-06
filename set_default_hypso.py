import os

PATHS = [
    r"C:\Users\mhs4118\.gemini\antigravity\brain\38ec0b63-c099-4411-a09e-791a249c2aa3\gorkha_landslides_3d_viewer.html",
    r"C:\Users\mhs4118\.gemini\antigravity\scratch\gorkha-landslides-3d\index.html",
]

for path in PATHS:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    has_crlf = "\r\n" in text
    s = text.replace("\r\n", "\n")

    # 1. Select options in #terrain-theme
    old_select = """          <select id="terrain-theme" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] px-2.5 py-1.5 font-medium">
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

    new_select = """          <select id="terrain-theme" class="w-full text-xs rounded-lg border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)] px-2.5 py-1.5 font-medium">
            <option value="hypso" selected>Hypsometric Elevation + Hillshade</option>
            <option value="ksn">Channel Steepness k_sn (cop30dem_..._near.tif) + Hillshade</option>
            <option value="susc_log">Bayesian Susceptibility (fp6a.gpkg — Log10 μ) + Hillshade</option>
            <option value="susc_lin">Bayesian Susceptibility Hotspots (fp6a.gpkg — Linear μ)</option>
            <option value="susc_sd">Bayesian Posterior Uncertainty (fp6a.gpkg — SD)</option>
            <option value="pga">PGA Ground Motion (pga_mean.flt) + Hillshade</option>
            <option value="mmi">MMI Intensity (mmi_mean.flt) + Hillshade</option>
            <option value="slope">Terrain Slope Steepness Heatmap</option>
            <option value="dark">Dark Relief (High-Contrast Base)</option>
            <option value="wire">3D Topographic Wireframe</option>
          </select>"""
    assert old_select in s, f"old_select not found in {path}"
    s = s.replace(old_select, new_select, 1)

    # 2. Initial Terrain Legend HTML
    old_tleg = """          <div class="flex justify-between text-xs text-[var(--muted-foreground)] mb-1">
            <span id="terrain-legend-title" class="font-medium text-[var(--foreground)]">3D Terrain PGA Scale</span>
            <span class="font-mono text-xs">Iso-lines shown on 3D mesh</span>
          </div>
          <div class="h-2.5 w-full rounded-full" id="terrain-legend-bar" style="background: linear-gradient(90deg, #2563eb, #06b6d4, #eab308, #f97316, #dc2626, #7f1d1d);"></div>
          <div class="flex justify-between text-xs font-mono text-[var(--muted-foreground)] mt-1">
            <span id="tleg-min">0.565 g</span>
            <span id="tleg-mid">0.622 g</span>
            <span id="tleg-max">0.680 g</span>
          </div>"""

    new_tleg = """          <div class="flex justify-between text-xs text-[var(--muted-foreground)] mb-1">
            <span id="terrain-legend-title" class="font-medium text-[var(--foreground)]">3D Terrain Hypsometric Elevation (DEM)</span>
            <span class="font-mono text-xs">Iso-lines shown on 3D mesh</span>
          </div>
          <div class="h-2.5 w-full rounded-full" id="terrain-legend-bar" style="background: linear-gradient(90deg, #38603e, #687e4e, #9e8c68, #bab2a8, #f8fafc);"></div>
          <div class="flex justify-between text-xs font-mono text-[var(--muted-foreground)] mt-1">
            <span id="tleg-min">1,150 m</span>
            <span id="tleg-mid">2,950 m</span>
            <span id="tleg-max">4,750 m</span>
          </div>"""
    assert old_tleg in s, f"old_tleg not found in {path}"
    s = s.replace(old_tleg, new_tleg, 1)

    # 3. Quick buttons initial highlight
    old_qbtns = """        <button id="btn-quick-ksn" class="px-2.5 py-1 rounded-lg text-xs font-semibold border border-cyan-400 bg-cyan-500/15 text-[var(--foreground)]">
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

    new_qbtns = """        <button id="btn-quick-hypso" class="px-2.5 py-1 rounded-lg text-xs font-semibold border border-cyan-400 bg-cyan-500/15 text-[var(--foreground)]">
          3D Elevation
        </button>
        <button id="btn-quick-ksn" class="px-2.5 py-1 rounded-lg text-xs font-medium bg-[var(--background)] border border-[var(--border)]">
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
        </button>"""
    assert old_qbtns in s, f"old_qbtns not found in {path}"
    s = s.replace(old_qbtns, new_qbtns, 1)

    # 4. Update updateLegendLabels for hypso / slope / dark / wire
    old_leg_fn = """        const tBar = document.getElementById('terrain-legend-bar');
        if (state.terrainTheme === 'ksn') {"""

    new_leg_fn = """        const tBar = document.getElementById('terrain-legend-bar');
        if (state.terrainTheme === 'hypso' || state.terrainTheme === 'dark' || state.terrainTheme === 'wire') {
          tTitle.textContent = state.terrainTheme === 'hypso'
            ? '3D Terrain Hypsometric Elevation (DEM)'
            : (state.terrainTheme === 'dark' ? '3D Dark Shaded Relief (DEM)' : '3D Topographic Wireframe (DEM)');
          tBar.style.background = state.terrainTheme === 'dark'
            ? 'linear-gradient(90deg, #22252a, #475569, #94a3b8)'
            : 'linear-gradient(90deg, #38603e, #687e4e, #9e8c68, #bab2a8, #f8fafc)';
          tMin.textContent = `${regData.zMin.toLocaleString()} m`;
          tMid.textContent = `${Math.round(regData.zMid).toLocaleString()} m`;
          tMax.textContent = `${regData.zMax.toLocaleString()} m`;
        } else if (state.terrainTheme === 'slope') {
          tTitle.textContent = '3D Terrain Slope Steepness (°)';
          tBar.style.background = 'linear-gradient(90deg, #2d5f82, #7ca56e, #dc8728)';
          tMin.textContent = '0°';
          tMid.textContent = '25°';
          tMax.textContent = '50°+';
        } else if (state.terrainTheme === 'ksn') {"""
    assert old_leg_fn in s, f"old_leg_fn not found in {path}"
    s = s.replace(old_leg_fn, new_leg_fn, 1)

    # 5. For index.html, also update state.terrainTheme directly
    if path.endswith("index.html"):
        s = s.replace(
            "terrainTheme: 'ksn',     // Default directly to Channel Steepness Index k_sn on 3D terrain!",
            "terrainTheme: 'hypso',   // Default to Hypsometric Elevation + Hillshade on 3D terrain!",
            1,
        )

    if has_crlf:
        s = s.replace("\n", "\r\n")

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("Updated:", path)

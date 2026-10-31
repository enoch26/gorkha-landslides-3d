import os

PATHS = [
    r"C:\Users\mhs4118\.gemini\antigravity\brain\38ec0b63-c099-4411-a09e-791a249c2aa3\gorkha_landslides_3d_viewer.html",
    r"C:\Users\mhs4118\.gemini\antigravity\scratch\gorkha-landslides-3d\index.html",
]

OLD_HEADER_PILLS = """      <button data-region="rupture_corridor" class="region-btn px-2.5 py-1 rounded-lg text-xs font-medium border border-[var(--border)] transition">
        5. Full Rupture Corridor
      </button>
    </div>
  </header>"""

NEW_HEADER_PILLS = """      <button data-region="rupture_corridor" class="region-btn px-2.5 py-1 rounded-lg text-xs font-medium border border-[var(--border)] transition">
        5. Full Rupture Corridor
      </button>
      <span class="text-[var(--border)] px-0.5">|</span>
      <button id="btn-launch-tour" class="px-3 py-1 rounded-lg text-xs font-semibold border border-emerald-400 bg-emerald-500/20 text-[var(--foreground)] hover:bg-emerald-500/30 transition flex items-center gap-1.5 shadow-sm">
        <span id="btn-launch-tour-icon">&#9654;</span>
        <span id="btn-launch-tour-text">Video Demo Tour (0:56)</span>
      </button>
    </div>
  </header>"""

OLD_VIEWPORT_OVERLAY = """      <!-- Hover Tooltip -->
      <div id="hover-tooltip" class="hidden fixed z-30 pointer-events-none bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-2 shadow-lg text-xs"></div>

      <!-- 3D Interactive Canvas -->"""

NEW_VIEWPORT_OVERLAY = """      <!-- Guided Video Demo Lower-Third HUD -->
      <div id="demo-hud" class="hidden absolute bottom-12 left-3 right-3 z-20 bg-[var(--card)]/95 backdrop-blur-md border-2 border-emerald-400/70 rounded-2xl p-3.5 shadow-2xl">
        <div class="flex items-center justify-between gap-2 mb-1.5 flex-wrap">
          <div class="flex items-center gap-2">
            <span id="demo-step-badge" class="px-2 py-0.5 rounded-md text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-400/50">
              STEP 1 / 7
            </span>
            <h3 id="demo-step-title" class="text-sm font-bold text-[var(--foreground)]">
              1. 3D Hypsometric Elevation &amp; Interactive Orbit
            </h3>
          </div>
          <div class="flex items-center gap-1.5">
            <span id="demo-time-label" class="text-xs font-mono text-[var(--muted-foreground)] mr-1">0:00 / 0:56</span>
            <button id="demo-btn-prev" class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)] text-xs text-[var(--foreground)] hover:opacity-80">
              &#9664; Prev
            </button>
            <button id="demo-btn-play" class="px-2.5 py-0.5 rounded border border-emerald-400 bg-emerald-500/20 text-xs font-semibold text-[var(--foreground)] hover:opacity-90">
              &#10074;&#10074; Pause
            </button>
            <button id="demo-btn-next" class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)] text-xs text-[var(--foreground)] hover:opacity-80">
              Next &#9654;
            </button>
            <button id="demo-btn-close" class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)] text-xs text-rose-400 hover:opacity-80 ml-1">
              Exit &#10005;
            </button>
          </div>
        </div>
        <p id="demo-step-desc" class="text-xs text-[var(--muted-foreground)] leading-relaxed mb-2.5">
          By default, the 3D terrain mesh displays Hypsometric Elevation + Hillshade with 21,151 mapped landslide polygons from Valagussa et al. (2021). Left-drag to orbit in 3D, Shift-drag to pan, and scroll to zoom.
        </p>
        <!-- 7-Chapter Segmented Progress Bar -->
        <div id="demo-progress-row" class="grid grid-cols-7 gap-1.5"></div>
      </div>

      <!-- Animated Demo Spotlight Cursor -->
      <div id="demo-cursor" class="hidden fixed z-40 pointer-events-none" style="left: 500px; top: 300px; transform: translate(-22px, -22px);">
        <div class="relative flex items-center">
          <div class="w-11 h-11 rounded-full border-2 border-emerald-400 bg-emerald-400/20 flex items-center justify-center shadow-lg">
            <div class="w-3 h-3 rounded-full bg-emerald-400 shadow"></div>
          </div>
          <div id="demo-cursor-label" class="ml-2.5 px-2.5 py-1 rounded-lg bg-[var(--card)] border-2 border-emerald-400 text-[var(--foreground)] text-xs font-semibold font-mono whitespace-nowrap shadow-xl">
            Hypsometric Elevation + Hillshade
          </div>
        </div>
      </div>

      <!-- Hover Tooltip -->
      <div id="hover-tooltip" class="hidden fixed z-30 pointer-events-none bg-[var(--card)] border border-[var(--border)] rounded-lg px-3 py-2 shadow-lg text-xs"></div>

      <!-- 3D Interactive Canvas -->"""

OLD_SCRIPT_END = """      window.addEventListener('resize', () => {
        drawMinimap();
        render3D();
      });

      selectRegion('trisuli_rasuwa');
    })();"""

NEW_SCRIPT_END = """      window.addEventListener('resize', () => {
        drawMinimap();
        render3D();
      });

      // =====================================================================
      // 7-Chapter Interactive Video Demo Tour & Deterministic Frame Recorder
      // =====================================================================
      const DEMO_CHAPTERS = [
        {
          id: 1,
          start: 0,
          end: 8,
          title: '1. Default 3D Hypsometric Terrain & Orbit Controls',
          desc: 'By default, Panel 1 renders Hypsometric Elevation + Hillshade on the 3D DEM mesh with 21,151 Gorkha landslide polygons (Valagussa_2021.shp). Left-drag to orbit 3D, Shift+drag to pan, and scroll to zoom.',
          targetSelector: '#terrain-theme',
          cursorText: 'Default: Hypsometric Elevation + Hillshade'
        },
        {
          id: 2,
          start: 8,
          end: 16,
          title: '2. Switching Himalayan Test Gorges & Nepal Overview Map',
          desc: 'Click the top Test Area buttons (Trisuli, Bhote Koshi, Langtang, Budi Gandaki, or Full Rupture Corridor) or click any numbered box on the Nepal Overview Mini-Map to switch regions.',
          targetSelector: '.region-btn[data-region="bhote_koshi"]',
          cursorText: 'Switch Test Gorge or Click Mini-Map'
        },
        {
          id: 3,
          start: 16,
          end: 24,
          title: '3. Mapping Channel Steepness Index (k_sn GeoTIFF) on 3D Slopes',
          desc: 'In Panel 1, select Channel Steepness k_sn (cop30dem_channel_tagged_pixels_near.tif) to drape LSDTopoTools fluvial steepness onto the 3D gorge walls and color polygons by k_sn.',
          targetSelector: '#btn-quick-ksn',
          cursorText: 'Layer: Channel Steepness k_sn (.tif)'
        },
        {
          id: 4,
          start: 24,
          end: 32,
          title: '4. Fitted Bayesian Space-Time Susceptibility (fp6a.gpkg)',
          desc: 'Select Bayesian Susceptibility (fp6a.gpkg — Log10 μ or Posterior SD) to map your fitted space-time model predictions and uncertainty directly across the 3D topography.',
          targetSelector: '#btn-quick-susc',
          cursorText: 'Layer: Bayesian Susceptibility (fp6a.gpkg)'
        },
        {
          id: 5,
          start: 32,
          end: 40,
          title: '5. USGS ShakeMap Ground Motion: PGA & MMI (.flt)',
          desc: 'Switch to PGA Ground Motion (pga_mean.flt) or MMI Intensity (mmi_mean.flt) with 3D iso-motion contours, and toggle Local Valley Gradient vs. Regional Nepal Scale.',
          targetSelector: '#btn-quick-pga',
          cursorText: 'Layer: USGS ShakeMap PGA & MMI (.flt)'
        },
        {
          id: 6,
          start: 40,
          end: 48,
          title: '6. 3D Polygon Extrusion, Slip Vectors & Terrain Sliders',
          desc: 'In Panel 2, switch polygons between Draped 3D outlines, 3D Extruded Columns (by Volume/Area), or Crown-to-Toe Slope Vectors. In Panel 3, tune Vertical Exaggeration, Sun Azimuth, and Area filters.',
          targetSelector: '#poly-mode',
          cursorText: '3D Extruded Columns & Crown-to-Toe Vectors'
        },
        {
          id: 7,
          start: 48,
          end: 56,
          title: '7. Inspecting Individual Landslides & 3D Slope Profiles',
          desc: 'Hover or click any landslide polygon in 3D (or select from the right-hand table) to inspect its FID, Area, k_sn, Bayesian μ/SD, PGA, MMI, and Crown-to-Toe 3D elevation profile.',
          targetSelector: '#inspector-content',
          cursorText: 'Inspect Landslide Attributes & 3D Profile'
        }
      ];

      const DEMO_TOTAL_SEC = 56.0;
      const demoState = {
        active: false,
        playing: false,
        tSec: 0,
        lastFrameTs: 0,
        cursorX: 600,
        cursorY: 360
      };

      const demoHudEl = document.getElementById('demo-hud');
      const demoCursorEl = document.getElementById('demo-cursor');
      const demoCursorLabelEl = document.getElementById('demo-cursor-label');
      const demoStepBadgeEl = document.getElementById('demo-step-badge');
      const demoStepTitleEl = document.getElementById('demo-step-title');
      const demoStepDescEl = document.getElementById('demo-step-desc');
      const demoTimeLabelEl = document.getElementById('demo-time-label');
      const demoProgRowEl = document.getElementById('demo-progress-row');
      const demoPlayBtn = document.getElementById('demo-btn-play');
      const launchTourBtn = document.getElementById('btn-launch-tour');
      const launchTourIcon = document.getElementById('btn-launch-tour-icon');
      const launchTourText = document.getElementById('btn-launch-tour-text');

      // Build 7-segment progress bar
      const progFillEls = [];
      DEMO_CHAPTERS.forEach((ch, idx) => {
        const wrap = document.createElement('button');
        wrap.className = 'text-left group focus:outline-none';
        wrap.title = ch.title;
        wrap.innerHTML = `
          <div class="h-1.5 w-full rounded-full bg-[var(--background)] border border-[var(--border)] overflow-hidden">
            <div class="h-full bg-emerald-400 transition-none" style="width: 0%"></div>
          </div>
          <div class="text-[10px] font-mono text-[var(--muted-foreground)] truncate mt-0.5">${idx + 1}. ${ch.title.split('.')[1].trim()}</div>
        `;
        wrap.addEventListener('click', () => {
          setDemoTime(ch.start + 0.05);
        });
        demoProgRowEl.appendChild(wrap);
        progFillEls.push(wrap.querySelector('div > div'));
      });

      function fmtSec(s) {
        const m = Math.floor(s / 60);
        const sec = Math.floor(s % 60);
        return `${m}:${sec < 10 ? '0' : ''}${sec}`;
      }

      function getElementAnchor(selector) {
        const el = document.querySelector(selector);
        if (!el) return [window.innerWidth * 0.5, window.innerHeight * 0.45];
        const r = el.getBoundingClientRect();
        return [r.left + Math.min(r.width * 0.35, 90), r.top + Math.min(r.height * 0.5, 28)];
      }

      function applyDemoUIState(regionKey, terrainTheme, polyMode, colorMode, shakeScale, vExag, sunAz) {
        if (state.regionId !== regionKey) {
          selectRegion(regionKey);
        }
        state.terrainTheme = terrainTheme;
        state.polyMode = polyMode;
        state.colorMode = colorMode;
        state.shakeScale = shakeScale;
        state.vExag = vExag;
        state.sunAzimuth = sunAz;

        document.getElementById('terrain-theme').value = terrainTheme;
        document.getElementById('poly-mode').value = polyMode;
        document.getElementById('color-mode').value = colorMode;
        document.getElementById('shake-scale').value = shakeScale;
        document.getElementById('rng-vexag').value = String(vExag);
        document.getElementById('lbl-vexag').textContent = `${vExag.toFixed(2)}×`;
        document.getElementById('rng-sun').value = String(Math.round(sunAz));
        document.getElementById('lbl-sun').textContent = `${Math.round(sunAz)}° (${aspectToCardinal(sunAz)})`;
      }

      function setDemoTime(tSec) {
        tSec = Math.max(0, Math.min(DEMO_TOTAL_SEC, tSec));
        demoState.tSec = tSec;
        demoState.active = true;
        demoHudEl.classList.remove('hidden');
        demoCursorEl.classList.remove('hidden');
        launchTourIcon.innerHTML = '&#9632;';
        launchTourText.textContent = 'Tour Active';

        // Find current chapter
        let chapter = DEMO_CHAPTERS[0];
        for (const ch of DEMO_CHAPTERS) {
          if (tSec >= ch.start && tSec <= ch.end) {
            chapter = ch;
            break;
          }
        }
        const u = Math.max(0, Math.min(1, (tSec - chapter.start) / (chapter.end - chapter.start)));

        demoStepBadgeEl.textContent = `STEP ${chapter.id} / ${DEMO_CHAPTERS.length}`;
        demoStepTitleEl.textContent = chapter.title;
        demoStepDescEl.textContent = chapter.desc;
        demoTimeLabelEl.textContent = `${fmtSec(tSec)} / ${fmtSec(DEMO_TOTAL_SEC)}`;

        DEMO_CHAPTERS.forEach((ch, idx) => {
          let pct = 0;
          if (tSec >= ch.end) pct = 100;
          else if (tSec > ch.start) pct = ((tSec - ch.start) / (ch.end - ch.start)) * 100;
          progFillEls[idx].style.width = `${pct.toFixed(1)}%`;
        });

        let targetSel = chapter.targetSelector;
        let cursorLabel = chapter.cursorText;
        tooltip.classList.add('hidden');

        if (chapter.id === 1) {
          // Chapter 1 (0-8s): Default Hypsometric Elevation + Hillshade, smooth 3D orbit
          applyDemoUIState('trisuli_rasuwa', 'hypso', 'draped', 'ksn', 'local', 1.35, 315);
          state.yaw = -0.75 + u * 0.52;
          state.pitch = 0.56 + Math.sin(u * Math.PI) * 0.12;
          state.zoom = 1.16 + Math.sin(u * Math.PI) * 0.10;
          state.panX = 0;
          state.panY = 0.02;
          if (u > 0.45) {
            targetSel = '#viewport-3d';
            cursorLabel = 'Drag to Orbit 3D · Scroll to Zoom';
          }
        } else if (chapter.id === 2) {
          // Chapter 2 (8-16s): Switch test regions & highlight Mini-Map
          let reg = 'trisuli_rasuwa';
          if (u < 0.38) {
            reg = 'bhote_koshi';
            targetSel = '.region-btn[data-region="bhote_koshi"]';
            cursorLabel = 'Region 2: Bhote Koshi Gorge';
          } else if (u < 0.72) {
            reg = 'langtang';
            targetSel = '.region-btn[data-region="langtang"]';
            cursorLabel = 'Region 3: Langtang Valley';
          } else {
            reg = 'trisuli_rasuwa';
            targetSel = '#minimap-canvas';
            cursorLabel = 'Click Nepal Mini-Map to Jump Regions';
          }
          applyDemoUIState(reg, 'hypso', 'draped', 'ksn', 'local', 1.35, 315);
          state.yaw = -0.55 + u * 0.45;
          state.pitch = 0.58;
          state.zoom = 1.18;
        } else if (chapter.id === 3) {
          // Chapter 3 (16-24s): Channel Steepness k_sn (.tif) on 3D Terrain
          applyDemoUIState('trisuli_rasuwa', 'ksn', 'draped', 'ksn', 'local', 1.45, 315);
          state.yaw = -0.48 + u * 0.55;
          state.pitch = 0.46 + 0.14 * Math.sin(u * Math.PI);
          state.zoom = 1.26;
          targetSel = u < 0.45 ? '#terrain-theme' : '#btn-quick-ksn';
          cursorLabel = '3D Surface: Channel Steepness k_sn (.tif)';
        } else if (chapter.id === 4) {
          // Chapter 4 (24-32s): Fitted Bayesian Susceptibility (fp6a.gpkg)
          const theme = u < 0.68 ? 'susc_log' : 'susc_sd';
          const cMode = u < 0.68 ? 'susc' : 'susc_sd';
          applyDemoUIState('trisuli_rasuwa', theme, 'draped', cMode, 'local', 1.40, 300);
          state.yaw = -0.62 + u * 0.52;
          state.pitch = 0.60;
          state.zoom = 1.22;
          targetSel = u < 0.5 ? '#terrain-theme' : '#btn-quick-susc';
          cursorLabel = u < 0.68 ? 'fp6a.gpkg: Bayesian Posterior Mean (Log10 μ)' : 'fp6a.gpkg: Bayesian Posterior Uncertainty (SD)';
        } else if (chapter.id === 5) {
          // Chapter 5 (32-40s): USGS ShakeMap PGA & MMI (.flt)
          const theme = u < 0.52 ? 'pga' : 'mmi';
          const scaleMode = (u > 0.30 && u < 0.50) ? 'regional' : 'local';
          applyDemoUIState('trisuli_rasuwa', theme, 'draped', theme, scaleMode, 1.35, 325);
          state.yaw = -0.50 + u * 0.48;
          state.pitch = 0.64;
          state.zoom = 1.20;
          targetSel = u < 0.52 ? '#btn-quick-pga' : '#btn-quick-mmi';
          cursorLabel = u < 0.52 ? 'pga_mean.flt: Peak Ground Acceleration (g)' : 'mmi_mean.flt: Modified Mercalli Intensity';
        } else if (chapter.id === 6) {
          // Chapter 6 (40-48s): 3D Extruded Columns, Slope Vectors & Geometry Sliders
          const pMode = u < 0.52 ? 'extruded' : 'vectors';
          const vex = 1.35 + Math.sin(u * Math.PI) * 0.55;
          const sun = 315 - u * 75;
          applyDemoUIState('trisuli_rasuwa', 'hypso', pMode, 'area', 'local', vex, sun);
          state.yaw = -0.65 + u * 0.65;
          state.pitch = 0.44 + 0.16 * Math.cos(u * Math.PI);
          state.zoom = 1.28;
          targetSel = u < 0.52 ? '#poly-mode' : '#rng-vexag';
          cursorLabel = u < 0.52 ? 'Polygon Mode: 3D Extruded Volume Columns' : `Vertical Exaggeration: ${vex.toFixed(2)}×`;
        } else {
          // Chapter 7 (48-56s): Inspecting a Landslide Polygon & Center in 3D
          applyDemoUIState('trisuli_rasuwa', 'hypso', 'draped', 'ksn', 'local', 1.40, 315);
          const regData = prepareRegion('trisuli_rasuwa');
          const feat = regData.features[0];
          state.selectedFeature = feat;
          state.hoveredFeature = feat;
          selectFeature(feat);

          const flyU = Math.min(1, u * 1.4);
          state.yaw = -0.52 + u * 0.25;
          state.pitch = 0.58;
          const cosYaw = Math.cos(state.yaw);
          const sinYaw = Math.sin(state.yaw);
          const rx = feat.cx * cosYaw - feat.cy * sinYaw;
          const ry = feat.cx * sinYaw + feat.cy * cosYaw;
          state.panX = -rx * 0.55 * flyU;
          state.panY = -ry * Math.sin(state.pitch) * 0.55 * flyU;
          state.zoom = 1.20 + 0.68 * flyU;
          targetSel = u < 0.45 ? '#viewport-3d' : '#profile-canvas';
          cursorLabel = u < 0.45 ? `Click Polygon FID #${feat.fid} on 3D Mesh` : 'Inspect k_sn, fp6a μ, PGA & 3D Slope Profile';
        }

        const regData = prepareRegion(state.regionId);
        updateLegendLabels(regData);
        drawMinimap();
        render3D();

        // Position animated spotlight cursor
        let [tx, ty] = getElementAnchor(targetSel);
        if (targetSel === '#viewport-3d') {
          const rect = canvas.getBoundingClientRect();
          tx = rect.left + rect.width * (0.48 + 0.08 * Math.cos(tSec * 1.5));
          ty = rect.top + rect.height * (0.46 + 0.06 * Math.sin(tSec * 1.5));
          if (chapter.id === 7 && state.screenPolys.length > 0) {
            const sp = state.screenPolys.find(p => p.feature.fid === state.selectedFeature.fid);
            if (sp && sp.pts.length > 0) {
              tx = rect.left + sp.pts[0].sx;
              ty = rect.top + sp.pts[0].sy;
            }
          }
        }
        // Clamp cursor so label stays on screen
        tx = Math.max(36, Math.min(window.innerWidth - 320, tx));
        ty = Math.max(36, Math.min(window.innerHeight - 140, ty));
        demoCursorEl.style.left = `${Math.round(tx)}px`;
        demoCursorEl.style.top = `${Math.round(ty)}px`;
        demoCursorLabelEl.textContent = cursorLabel;
      }

      function demoLoop(now) {
        if (!demoState.active || !demoState.playing) return;
        const dt = Math.min(0.1, (now - demoState.lastFrameTs) / 1000);
        demoState.lastFrameTs = now;
        let nextT = demoState.tSec + dt;
        if (nextT >= DEMO_TOTAL_SEC) {
          nextT = 0; // loop seamlessly
        }
        setDemoTime(nextT);
        requestAnimationFrame(demoLoop);
      }

      function startDemoTour(fromSec = 0) {
        demoState.active = true;
        demoState.playing = true;
        demoState.lastFrameTs = performance.now();
        demoPlayBtn.innerHTML = '&#10074;&#10074; Pause';
        setDemoTime(fromSec);
        requestAnimationFrame(demoLoop);
      }

      function stopDemoTour() {
        demoState.active = false;
        demoState.playing = false;
        demoHudEl.classList.add('hidden');
        demoCursorEl.classList.add('hidden');
        launchTourIcon.innerHTML = '&#9654;';
        launchTourText.textContent = 'Video Demo Tour (0:56)';
        applyDemoUIState('trisuli_rasuwa', 'hypso', 'draped', 'ksn', 'local', 1.35, 315);
        state.yaw = -0.58;
        state.pitch = 0.62;
        state.zoom = 1.18;
        state.panX = 0;
        state.panY = 0.02;
        const regData = prepareRegion(state.regionId);
        updateLegendLabels(regData);
        drawMinimap();
        render3D();
      }

      launchTourBtn.addEventListener('click', () => {
        if (demoState.active) {
          stopDemoTour();
        } else {
          startDemoTour(0);
        }
      });

      demoPlayBtn.addEventListener('click', () => {
        demoState.playing = !demoState.playing;
        if (demoState.playing) {
          demoPlayBtn.innerHTML = '&#10074;&#10074; Pause';
          demoState.lastFrameTs = performance.now();
          requestAnimationFrame(demoLoop);
        } else {
          demoPlayBtn.innerHTML = '&#9654; Play';
        }
      });

      document.getElementById('demo-btn-prev').addEventListener('click', () => {
        let curIdx = 0;
        DEMO_CHAPTERS.forEach((ch, idx) => {
          if (demoState.tSec >= ch.start && demoState.tSec <= ch.end) curIdx = idx;
        });
        const targetIdx = Math.max(0, curIdx - 1);
        setDemoTime(DEMO_CHAPTERS[targetIdx].start + 0.05);
      });

      document.getElementById('demo-btn-next').addEventListener('click', () => {
        let curIdx = 0;
        DEMO_CHAPTERS.forEach((ch, idx) => {
          if (demoState.tSec >= ch.start && demoState.tSec <= ch.end) curIdx = idx;
        });
        const targetIdx = Math.min(DEMO_CHAPTERS.length - 1, curIdx + 1);
        setDemoTime(DEMO_CHAPTERS[targetIdx].start + 0.05);
      });

      document.getElementById('demo-btn-close').addEventListener('click', stopDemoTour);

      // Expose deterministic tour controls globally for headless video capture
      window.setDemoTime = setDemoTime;
      window.startDemoTour = startDemoTour;
      window.stopDemoTour = stopDemoTour;
      window.DEMO_TOTAL_SEC = DEMO_TOTAL_SEC;

      selectRegion('trisuli_rasuwa');
      if (window.location.search.includes('autotour=1')) {
        startDemoTour(0);
      }
    })();"""

for path in PATHS:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    has_crlf = "\r\n" in text
    s = text.replace("\r\n", "\n")

    assert OLD_HEADER_PILLS in s, f"OLD_HEADER_PILLS not found in {path}"
    s = s.replace(OLD_HEADER_PILLS, NEW_HEADER_PILLS, 1)

    assert OLD_VIEWPORT_OVERLAY in s, f"OLD_VIEWPORT_OVERLAY not found in {path}"
    s = s.replace(OLD_VIEWPORT_OVERLAY, NEW_VIEWPORT_OVERLAY, 1)

    assert OLD_SCRIPT_END in s, f"OLD_SCRIPT_END not found in {path}"
    s = s.replace(OLD_SCRIPT_END, NEW_SCRIPT_END, 1)

    if has_crlf:
        s = s.replace("\n", "\r\n")

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("Injected interactive Video Demo Tour into:", path)

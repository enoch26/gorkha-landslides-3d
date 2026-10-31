"""
Records a narrated 1600x900 MP4 video demo of the 3D Gorkha Landslide & Multi-Hazard Terrain Viewer
by driving headless Chrome via Chrome DevTools Protocol (CDP), synthesizing chapter narration via edge-tts,
and encoding H.264 + AAC via imageio-ffmpeg.
"""

import asyncio
import base64
import json
import os
import shutil
import subprocess
import time
import urllib.request

import edge_tts
import imageio_ffmpeg
import websocket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_DIR = r"C:\Users\mhs4118\.gemini\antigravity\brain\38ec0b63-c099-4411-a09e-791a249c2aa3"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

CHAPTER_SCRIPTS = [
    (
        0,
        8,
        "Welcome to the 2015 Gorkha Earthquake 3D Landslide Explorer. By default, the 3D mesh renders Hypsometric Elevation and hillshading with 21,000 landslide polygons. Left-drag to orbit, Shift-drag to pan, and scroll to zoom.",
    ),
    (
        8,
        16,
        "Use the top Test Area buttons—or click directly on the Nepal Overview Mini-Map—to jump between Trisuli Gorge, Bhote Koshi, Langtang Valley, Budi Gandaki, or the full Rupture Corridor.",
    ),
    (
        16,
        24,
        "In Panel 1, switch the 3D Terrain Surface Layer to Channel Steepness k-s-n to drape LSDTopoTools fluvial steepness from the 30-meter Copernicus DEM onto the gorge walls.",
    ),
    (
        24,
        32,
        "Select Bayesian Susceptibility from fp6a dot gpkg to map your fitted space-time model's posterior mean intensity mu and standard deviation directly across the 3D slopes.",
    ),
    (
        32,
        40,
        "Switch to USGS ShakeMap PGA or MMI ground motion rasters to inspect seismic shaking and 3D iso-motion contours, toggling between local valley contrast and the regional Nepal scale.",
    ),
    (
        40,
        48,
        "In Panel 2, switch polygons between Draped 3D outlines, 3D Extruded Volume Columns, or Crown-to-Toe Slope Vectors, and use Panel 3 sliders to tune Vertical Exaggeration and Sun Azimuth.",
    ),
    (
        48,
        56,
        "Finally, click any landslide polygon in 3D or from the ranked table on the right to inspect its Feature ID, k-s-n, Bayesian susceptibility, PGA, MMI, and Crown-to-Toe 3D elevation profile.",
    ),
]


async def build_voiceover(audio_dir):
    os.makedirs(audio_dir, exist_ok=True)
    part_paths = []
    for idx, (t0, t1, text) in enumerate(CHAPTER_SCRIPTS):
        raw_mp3 = os.path.join(audio_dir, f"ch_{idx+1}_raw.mp3")
        pad_wav = os.path.join(audio_dir, f"ch_{idx+1}_pad.wav")
        comm = edge_tts.Communicate(text, voice="en-US-AriaNeural", rate="+15%")
        await comm.save(raw_mp3)
        # Pad or trim each segment to exact 8.0s duration using ffmpeg
        dur = t1 - t0
        cmd = [
            FFMPEG_EXE,
            "-y",
            "-i",
            raw_mp3,
            "-af",
            f"apad=whole_dur={dur}",
            "-t",
            str(dur),
            "-ar",
            "44100",
            "-ac",
            "2",
            pad_wav,
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        part_paths.append(pad_wav)

    # Concatenate all 7 WAV segments into full_voiceover.wav (56.0s)
    concat_txt = os.path.join(audio_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in part_paths:
            f.write("file '" + p.replace("\\", "/") + "'\n")

    full_wav = os.path.join(audio_dir, "full_voiceover.wav")
    subprocess.run(
        [
            FFMPEG_EXE,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_txt,
            "-c",
            "copy",
            full_wav,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return full_wav


def cdp_call(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    ws.send(json.dumps(payload))
    while True:
        raw = ws.recv()
        data = json.loads(raw)
        if data.get("id") == msg_id:
            return data.get("result", {})


def main():
    audio_dir = os.path.join(BASE_DIR, "demo_audio_tmp")
    print("1. Synthesizing 7-chapter voiceover narration...")
    full_wav = None
    try:
        full_wav = asyncio.run(build_voiceover(audio_dir))
        print("   Voiceover ready:", full_wav)
    except Exception as e:
        print("   Voiceover synthesis skipped/failed, proceeding without TTS:", e)

    chrome_profile = os.path.join(BASE_DIR, "chrome_demo_profile")
    if os.path.exists(chrome_profile):
        shutil.rmtree(chrome_profile, ignore_errors=True)
    os.makedirs(chrome_profile, exist_ok=True)

    port = 9236
    url = "http://127.0.0.1:8765/"
    print("2. Launching isolated headless Chrome at 1600x900...")
    chrome_proc = subprocess.Popen(
        [
            CHROME_EXE,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={chrome_profile}",
            f"--remote-debugging-port={port}",
            "--window-size=1600,900",
            "--force-device-scale-factor=1",
            "--hide-scrollbars",
            url,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for DevTools endpoint
        ws_url = None
        for _ in range(30):
            time.sleep(0.3)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json") as resp:
                    tabs = json.loads(resp.read().decode())
                    for t in tabs:
                        if t.get("type") == "page" and "127.0.0.1:8765" in t.get("url", ""):
                            ws_url = t.get("webSocketDebuggerUrl")
                            break
                    if not ws_url and tabs:
                        ws_url = tabs[0].get("webSocketDebuggerUrl")
                    if ws_url:
                        break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError("Could not connect to headless Chrome DevTools websocket")

        ws = websocket.create_connection(ws_url, timeout=30)
        msg_id = 1

        # Ensure exact 1600x900 viewport
        cdp_call(
            ws,
            msg_id,
            "Emulation.setDeviceMetricsOverride",
            {"width": 1600, "height": 900, "deviceScaleFactor": 1, "mobile": False},
        )
        msg_id += 1

        # Wait 1.5s for Tailwind CDN & fonts & initial 3D canvas render
        time.sleep(1.5)

        fps = 12
        total_sec = 56.0
        total_frames = int(total_sec * fps)

        out_mp4_project = os.path.join(BASE_DIR, "gorkha_3d_viewer_demo.mp4")
        out_mp4_artifact = os.path.join(ARTIFACT_DIR, "gorkha_3d_viewer_demo.mp4")

        ffmpeg_cmd = [
            FFMPEG_EXE,
            "-y",
            "-f",
            "image2pipe",
            "-vcodec",
            "mjpeg",
            "-r",
            str(fps),
            "-i",
            "-",
        ]
        if full_wav and os.path.exists(full_wav):
            ffmpeg_cmd.extend(["-i", full_wav, "-c:a", "aac", "-b:a", "128k", "-shortest"])

        ffmpeg_cmd.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                out_mp4_project,
            ]
        )

        print(f"3. Capturing {total_frames} frames ({total_sec}s @ {fps} FPS) -> {out_mp4_project} ...")
        ff_proc = subprocess.Popen(
            ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        t_start = time.time()
        for f_idx in range(total_frames):
            t_sec = f_idx / fps
            cdp_call(
                ws,
                msg_id,
                "Runtime.evaluate",
                {"expression": f"window.setDemoTime({t_sec:.3f});", "awaitPromise": False},
            )
            msg_id += 1

            res = cdp_call(
                ws,
                msg_id,
                "Page.captureScreenshot",
                {"format": "jpeg", "quality": 90, "fromSurface": True},
            )
            msg_id += 1

            img_bytes = base64.b64decode(res["data"])
            ff_proc.stdin.write(img_bytes)

            if (f_idx + 1) % 84 == 0 or f_idx == total_frames - 1:
                elapsed = time.time() - t_start
                print(f"   Frame {f_idx+1}/{total_frames} (t={t_sec:.1f}s) [{elapsed:.1f}s elapsed]")

        ff_proc.stdin.close()
        ff_err = ff_proc.stderr.read().decode("utf-8", errors="ignore")
        ff_proc.wait()
        if ff_proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed ({ff_proc.returncode}): {ff_err[-600:]}")

        ws.close()
        shutil.copy2(out_mp4_project, out_mp4_artifact)
        sz_mb = os.path.getsize(out_mp4_artifact) / (1024 * 1024)
        print(f"4. Done! Video saved to {out_mp4_artifact} ({sz_mb:.2f} MB)")

    finally:
        chrome_proc.terminate()
        shutil.rmtree(chrome_profile, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)


if __name__ == "__main__":
    main()

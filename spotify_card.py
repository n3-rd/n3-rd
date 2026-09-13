"""
Generates dist/spotify.svg from Godwin's own now-playing API
(https://music.n3-rd.xyz/api/now-playing) instead of talking to Spotify
directly — no client id/secret/refresh token needed at all.

Card is fully self-contained: the album art is embedded as the base64
data URI the API already returns, so nothing external has to load when
GitHub renders the SVG.
"""
import html
import json
import urllib.request

API_URL = "https://music.n3-rd.xyz/api/now-playing"


def fetch_now_playing():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "n3-rd-readme"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def esc(s, limit=42):
    return html.escape((s or "")[:limit])


def make_svg(data):
    title = esc(data.get("title") or "nothing on repeat right now")
    artist = esc(data.get("artist") or "n3rd")
    album = esc(data.get("album") or "")
    art = data.get("imageBase64")
    accent = (data.get("color") or {}).get("hex") or "#00FF9D"
    is_playing = data.get("isPlaying")
    is_recent = data.get("isRecentlyPlayed")
    status = "VIBING TO" if is_playing else ("LAST PLAYED" if is_recent else "OFFLINE")

    progress_pct = data.get("progressPercent") or 0
    fmt_progress = esc(data.get("formattedProgress") or "0:00", 10)
    fmt_duration = esc(data.get("formattedDuration") or "0:00", 10)

    bar_x, bar_w = 130, 300
    fill_w = round(bar_w * min(max(progress_pct, 0), 100) / 100, 1)

    art_block = (
        f'<clipPath id="artclip"><rect x="20" y="18" width="90" height="90" rx="8"/></clipPath>'
        f'<image href="{art}" x="20" y="18" width="90" height="90" clip-path="url(#artclip)" preserveAspectRatio="xMidYMid slice"/>'
        if art
        else '<rect x="20" y="18" width="90" height="90" rx="8" fill="#161b22"/>'
    )

    return f'''<svg width="450" height="126" viewBox="0 0 450 126" xmlns="http://www.w3.org/2000/svg">
  <rect width="450" height="126" rx="10" fill="#0d1117"/>
  {art_block}
  <text x="130" y="34" fill="{accent}" font-family="monospace" font-size="11" letter-spacing="2">{status}</text>
  <text x="130" y="58" fill="#f0f6fc" font-family="monospace" font-size="16" font-weight="700">{title}</text>
  <text x="130" y="78" fill="#8b949e" font-family="monospace" font-size="12">{artist}{' — ' + album if album else ''}</text>
  <rect x="{bar_x}" y="96" width="{bar_w}" height="4" rx="2" fill="#21262d"/>
  <rect x="{bar_x}" y="96" width="{fill_w}" height="4" rx="2" fill="{accent}"/>
  <text x="{bar_x}" y="114" fill="#6e7681" font-family="monospace" font-size="10">{fmt_progress}</text>
  <text x="{bar_x + bar_w}" y="114" fill="#6e7681" font-family="monospace" font-size="10" text-anchor="end">{fmt_duration}</text>
</svg>'''


def fallback_svg():
    return make_svg({})


def main():
    import os
    os.makedirs("dist", exist_ok=True)
    try:
        data = fetch_now_playing()
        svg = make_svg(data)
    except Exception:
        svg = fallback_svg()

    with open("dist/spotify.svg", "w") as f:
        f.write(svg)


if __name__ == "__main__":
    main()

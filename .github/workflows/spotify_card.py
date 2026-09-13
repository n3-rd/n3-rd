"""
Generates dist/spotify.svg from the Spotify API — either the track
currently playing, or the most recently played one if nothing is
playing right now. Styled to match the n3rd neon README theme.

Needs three repo secrets: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
SPOTIFY_REFRESH_TOKEN. See the setup notes for how to get these.
"""
import os
import base64
import html
import requests

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]


def get_access_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_track(token):
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers=headers,
        timeout=15,
    )
    if r.status_code == 200 and r.content:
        data = r.json()
        if data.get("is_playing") and data.get("item"):
            return data["item"], True

    r = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=1",
        headers=headers,
        timeout=15,
    )
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None, False
    return items[0]["track"], False


def make_svg(name, artist, playing):
    name = html.escape(name)[:40]
    artist = html.escape(artist)[:40]
    status = "VIBING TO" if playing else "LAST PLAYED"
    return f'''<svg width="450" height="120" viewBox="0 0 450 120" xmlns="http://www.w3.org/2000/svg">
  <rect width="450" height="120" rx="10" fill="#0d1117"/>
  <text x="20" y="32" fill="#00D4FF" font-family="monospace" font-size="12" letter-spacing="2">{status}</text>
  <text x="20" y="62" fill="#00FF9D" font-family="monospace" font-size="18" font-weight="700">{name}</text>
  <text x="20" y="88" fill="#FF00C8" font-family="monospace" font-size="14">{artist}</text>
</svg>'''


def fallback_svg():
    return make_svg("nothing on repeat right now", "n3rd", False)


def main():
    os.makedirs("dist", exist_ok=True)
    try:
        token = get_access_token()
        item, playing = get_track(token)
        if item is None:
            svg = fallback_svg()
        else:
            name = item["name"]
            artist = ", ".join(a["name"] for a in item.get("artists", []))
            svg = make_svg(name, artist, playing)
    except Exception:
        svg = fallback_svg()

    with open("dist/spotify.svg", "w") as f:
        f.write(svg)


if __name__ == "__main__":
    main()

# Spotify Listener

A lightweight ETL service that polls the Spotify API for your recently played tracks and stores them in a normalized SQLite database. Built to run continuously in a container, laying the groundwork for a personal listening-history dashboard.

## Overview

Spotify's API doesn't retain your play history, and its "recently played" endpoint only returns the last 50 tracks. This project closes that gap: a small Python service authenticates with Spotify via [Spotipy](https://spotipy.readthedocs.io/), polls the API every 30 seconds, and persists any new plays to a local SQLite database with proper relational structure for tracks, albums, and artists (including multi-artist tracks).

## How it works

1. **Authenticate** with the Spotify API using OAuth (`user-read-recently-played` scope), with the token cached to disk so re-authentication isn't required on every restart.
2. **Poll** the `current_user_recently_played` endpoint every 30 seconds.
3. **Deduplicate** by comparing each item's `played_at` timestamp against the most recent timestamp already stored, so only new plays are processed.
4. **Insert** the album, artists, and track into their respective tables, then link the track to each of its artists (with position, to preserve artist order for multi-artist tracks).
5. **Log** what was added on each poll, and continue on error rather than crashing the service.

## Database schema

Four tables, defined in `schema.sql`:

| Table | Purpose |
|---|---|
| `albums` | One row per album (id, name, release date, artwork URL, etc.) |
| `tracks` | One row per play, keyed by `played_at` so repeat plays of the same track are stored separately |
| `artists` | One row per artist |
| `track_artists` | Junction table linking tracks to artists, preserving artist order for collaborations |

Indexes are set on `artist_id`, `album_id`, `played_at`, and `track_id` to keep lookups fast as the history grows.

## Project structure

```
spotify-listener/
├── app.py              # Main polling service
├── schema.sql           # Database schema
├── requirements.txt     # Python dependencies
├── Dockerfile            # Container definition
├── LICENSE
└── scripts/              # Exploratory utilities used during development
    ├── spotify-kpis.py      # Prints top artists/tracks from Spotify's "top items" endpoint
    ├── readDatabase.py      # Dumps the full contents of a local database for inspection
    ├── read database.py     # Read-only dump of a spotify_history.db table
    └── testPythonScript.py  # Scratch script for exploring the raw API response shape
```

The `scripts/` folder holds one-off scripts used while building and debugging the pipeline. They aren't wired into the main service and some reference different database files or environment variable names than `app.py`.

## Setup

### Prerequisites

- Python 3.12+, or Docker
- A Spotify Developer app (client ID and secret) from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard), with a redirect URI registered

### 1. Clone and configure

```bash
git clone https://github.com/GarrettMeldrum/spotify-listener.git
cd spotify-listener
```

Create a `.env` file in the project root:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
DB=data/spotify_history.db
```

### 2. Run locally

```bash
pip install -r requirements.txt
python app.py
```

On first run, Spotipy opens the OAuth flow and caches the resulting token. Note that the cache path is currently hardcoded to `/app/data/.cache` in `app.py`, so when running outside Docker, create that directory relative to your working directory (`mkdir -p app/data`) or update the path before running.

### 3. Run with Docker

```bash
docker build -t spotify-listener .
docker run -d \
  --name spotify-listener \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  spotify-listener
```

Mounting `/app/data` persists both the SQLite database and the OAuth token cache across container restarts.

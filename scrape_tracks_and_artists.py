import streamlit as st
import pandas as pd
import numpy as np
import random
from tqdm import tqdm
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
import datetime

# TO MODIFY BELOW - add own Spotify Developer credentials
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="your_spotify_client_id",
        client_secret="your_spotify_client_secret_key",
        redirect_uri="https://localhost:8080",
        scope="user-library-read",
    )
)


def scrape_all_tracks(sp):
    # Fetching all saved tracks
    results = sp.current_user_saved_tracks(limit=50)
    tracks = results["items"]

    while results["next"]:
        results = sp.next(results)  # Fetch the next set of tracks
        tracks.extend(results["items"])
        if len(tracks) % 1000 == 0:
            print(f"{len(tracks)} tracks scraped...")
    print(f"{len(tracks)} scraped in total!")
    return tracks


def unique_artists(tracks):
    # Get list of unique artists' names
    artists_data = []

    for track in tqdm(tracks):
        artists = track["track"]["artists"]
        for artist in artists:
            artists_data.append((artist["name"], artist["id"]))

    artists_data_unq = sorted(set(artists_data))
    return artists_data_unq


if __name__ == "__main__":
    print("Scraping all tracks...")
    tracks = scrape_all_tracks(sp)

    print("Getting all unique artists...")
    artists_unique = unique_artists(tracks)

    filename = "artists_unique.csv"

    # Save the list to a CSV file
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Artist", "ID"])  # Write header
        writer.writerows(artists_unique)  # Write data rows

    print(f"Saved the list to {filename}")

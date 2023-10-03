import os
import subprocess

import streamlit as st
import pandas as pd
import numpy as np
import random
from tqdm import tqdm
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import datetime


# TO MODIFY BELOW - add own Spotify Developer credentials
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="your_spotify_client_id",
        client_secret="your_spotify_client_secret_key",
        redirect_uri="https://localhost:2023",
        scope="user-library-read",
    )
)


def scrape_n_random_artists(artists_data_unq):
    current_date = datetime.datetime.now().date()
    # can be changed but here let's only keep last 8 days to only get most recent releases
    threshold_date = current_date - datetime.timedelta(days=8)

    releases = []

    for idx, artist in tqdm(artists_data_unq.iterrows()):
        albums = sp.artist_albums(artist[1], album_type="album", limit=50)
        singles = sp.artist_albums(artist[1], album_type="single", limit=50)
        for release in albums["items"] + singles["items"]:
            release_date_str = release["release_date"]

            if len(release_date_str) < 4:
                pass
            else:
                if len(release_date_str) == 4:
                    # If release date is only a year, set it to January 1st of that year
                    release_date_str += "-01-01"
                try:
                    release_date = datetime.datetime.strptime(
                        release_date_str, "%Y-%m-%d"
                    ).date()
                    if release_date >= threshold_date:
                        releases.append(release)
                except:
                    pass
    # Sort releases by release date in ascending order
    releases.sort(key=lambda r: r["release_date"], reverse=True)
    return releases


def releases_df(releases):
    artists_featured = []
    albums_singles_names = []
    release_types = []
    release_dates = []
    spotify_urls = []
    cover_urls = []
    for release in releases:
        artists_featured.append(
            ", ".join([artist["name"] for artist in release["artists"]])
        )
        albums_singles_names.append(release["name"])
        release_types.append(release["album_type"])
        release_dates.append(release["release_date"])
        spotify_urls.append(release["external_urls"]["spotify"])
        cover_urls.append(release["images"][0]["url"])
    releases_df = pd.DataFrame(
        {
            "Artist(s)": artists_featured,
            "Album/Single Name": albums_singles_names,
            "Album or Single?": release_types,
            "Release Date": release_dates,
            "Spotify URL": spotify_urls,
            "Cover URL": cover_urls,
        }
    )
    return releases_df


def app():
    st.title(f"🎵 New Releases - Account: {sp.current_user()['display_name']} 😊")

    # Load your table data into a pandas DataFrame
    # df = pd.read_csv("releases_small.csv")

    # Get the number of artists to scrape from user input
    num_artists = st.number_input(
        "Choose the number of artists to scrape:", min_value=1, value=10
    )

    # Process the number of artists and display the result
    if st.button("Scrape"):
        st.write(f"{len(artists_unique)} different artists in your library!")
        st.write(f"Scraping {num_artists} random artists...")

        random_select = artists_unique.sample(num_artists)

        # Display the list of selected artists
        st.write("Here are some of the selected artists:")
        for artist in random_select.Artist.tolist()[:10]:
            st.markdown(f"- {artist}")

        rd_releases = scrape_n_random_artists(random_select)
        releases = releases_df(rd_releases)

        st.write("Here are the releases of those artists!")
        # Sort the DataFrame by the release date in descending order
        releases["Release Date"] = pd.to_datetime(releases["Release Date"])
        releases = releases.sort_values(by="Release Date", ascending=False)

        # Group the releases by release date
        grouped = releases.groupby(releases["Release Date"].dt.date)

        # Iterate through the grouped DataFrame and display releases by release date
        for release_date, releases in reversed(list(grouped)):
            st.subheader(release_date.strftime("%A, %B %d"))

            # Sort the releases within the group by release date in descending order
            releases = releases.sort_values(by="Release Date", ascending=False)

            # Split releases into chunks of 3
            chunks = np.array_split(releases, len(releases) // 3 + 1)

            # Create a row of columns for each chunk of releases
            for chunk in chunks:
                cols = st.columns(len(chunk))

                for idx, (_, row) in enumerate(chunk.iterrows()):
                    artist_names = row["Artist(s)"]
                    release_title = row["Album/Single Name"]
                    release_type = row["Album or Single?"]
                    spotify_url = row["Spotify URL"]
                    cover_url = row["Cover URL"]

                    with cols[idx]:
                        st.markdown(
                            f'<a href="{spotify_url}" target="_blank">'
                            f'<img src="{cover_url}" width="200" height="200"></a>',
                            unsafe_allow_html=True,
                        )
                        st.write(release_title)
                        st.write(artist_names)
                        st.write(release_type)

            st.write("---")


if __name__ == "__main__":
    artists_unique_csv = "artists_unique.csv"
    if artists_unique_csv not in os.listdir():
        # Run the scrape_tracks_and_artists.py file
        subprocess.run(["python", "scrape_tracks_and_artists.py"], check=True)
    else:
        print("Artists database already collected!")
    artists_unique = pd.read_csv("artists_unique.csv")
    app()

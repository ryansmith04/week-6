# your code here ...

import os

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class Genius:
    """retrieving artist information from the Genius API."""

    BASE_URL = "https://api.genius.com"

    def __init__(self, access_token):
        """Store the access token used to authorize every request."""
        self.access_token = access_token

    def _get(self, path, params=None):
        """Send a GET request to a Genius API path and return the JSON."""
        response = requests.get(
            self.BASE_URL + path,
            params=params,
            headers={"Authorization": "Bearer " + self.access_token},
        )
        response.raise_for_status()
        return response.json()

    def search(self, search_term, per_page=15):
        """Return the list of hits for a search term."""
        json_data = self._get(
            "/search", params={"q": search_term, "per_page": per_page}
        )
        return json_data["response"]["hits"]

    def _get_artist_id(self, search_term):
        """Return the primary artist ID from the first hit, or None."""
        hits = self.search(search_term, per_page=1)
        if not hits:
            return None
        return hits[0]["result"]["primary_artist"]["id"]

    def get_artist(self, search_term):
        """Return JSON for the most likely artist for a search term."""
        artist_id = self._get_artist_id(search_term)
        if artist_id is None:
            return None
        return self._get(f"/artists/{artist_id}")

    def _artist_row(self, search_term, artist_json):
        """Build one DataFrame row from an artist's JSON."""
        if artist_json is None:
            artist = {}
        else:
            artist = artist_json["response"]["artist"]
        return {
            "search_term": search_term,
            "artist_name": artist.get("name"),
            "artist_id": artist.get("id"),
            "followers_count": artist.get("followers_count"),
        }

    def get_artists(self, search_terms):
        """Return a DataFrame with one row of artist info per search term."""
        rows = [
            self._artist_row(term, self.get_artist(term))
            for term in search_terms
        ]

        return pd.DataFrame(rows)

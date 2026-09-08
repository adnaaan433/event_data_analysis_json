import streamlit as st
from mplsoccer import Sbapi


@st.cache_data(show_spinner=False)
def load_competitions(username: str, password: str) -> list:
    """
    Returns list of competition JSON objects directly from StatsBomb API.
    """
    parser = Sbapi(username=username, password=password, dataframe=False)
    url = f"{parser.url}4/competitions"
    try:
        data = parser._get_data(url)
        return data if isinstance(data, list) else []
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_matches(comp_id: int, season_id: int, username: str, password: str) -> list:
    """
    Returns list of match JSON objects for given comp_id and season_id.
    """
    parser = Sbapi(username=username, password=password, dataframe=False)
    url = f"{parser.url}6/competitions/{comp_id}/seasons/{season_id}/matches"
    try:
        data = parser._get_data(url)
        if not isinstance(data, list):
            return []
        matches = []
        for match in data:
            match_status = match.get("match_status")
            match_status_360 = match.get("match_status_360")
            if match_status == "available" or match_status_360 == "available":
                matches.append(match)
        return matches
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_events(match_id: int, username: str, password: str) -> list:
    """
    Returns raw event JSON list for a single match.
    """
    parser = Sbapi(username=username, password=password, dataframe=False)
    url = f"{parser.url}7/events/{match_id}"
    try:
        data = parser._get_data(url)
        return data if isinstance(data, list) else []
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_360_data(match_id: int, username: str, password: str) -> list:
    """
    Returns raw 360 frames JSON list for a single match.
    """
    parser = Sbapi(username=username, password=password, dataframe=False)
    url = f"{parser.url}2/360-frames/{match_id}"
    try:
        data = parser._get_data(url)
        return data if isinstance(data, list) else []
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_player_match_stats(match_id: int, username: str, password: str) -> list:
    """
    Returns player match stats JSON list for a single match (API v8.0.0).
    """
    parser = Sbapi(username=username, password=password, dataframe=False)
    url = f"{parser.url}8/matches/{match_id}/player-stats"
    try:
        data = parser._get_data(url)
        return data if isinstance(data, list) else []
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def load_team_match_stats(match_id: int, username: str, password: str) -> list:
    """
    Returns team match stats JSON list for a single match (API v4.0.0).
    """
    parser = Sbapi(username=username, password=password, dataframe=False)
    url = f"{parser.url}4/matches/{match_id}/team-stats"
    try:
        data = parser._get_data(url)
        return data if isinstance(data, list) else []
    except Exception:
        return []
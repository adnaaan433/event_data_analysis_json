"""
StatsBomb Event Data Explorer (Pure JSON Mode)
A Streamlit app to browse StatsBomb 360 event data as JSON by competition → season → match.
"""

import json
import streamlit as st
from data_loader import (
    load_competitions,
    load_matches,
    load_events,
    load_360_data,
    load_player_match_stats,
    load_team_match_stats,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StatsBomb JSON Explorer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Password Authentication System ────────────────────────────────────────────
APP_PASSWORD = st.secrets.get("app_password", "YOUR_DEFAULT_PASSWORD")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    auth_container = st.container()
    with auth_container:
        st.title("🔒 Restricted Access")
        st.write("Please enter the password to view the StatsBomb Event Explorer.")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Unlock"):
            if password_input == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

# ── Credentials from secrets.toml ─────────────────────────────────────────────
if "statsbomb" in st.secrets:
    username: str = st.secrets["statsbomb"]["username"]
    password: str = st.secrets["statsbomb"]["password"]
else:
    username: str = ""
    password: str = ""

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1b2838 100%);
        border-right: 1px solid #2a3a4a;
    }
    section[data-testid="stSidebar"] * {
        color: #e0e8f0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label {
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #7ecfff !important;
    }

    /* ── Selectbox dropdown ── */
    div[data-baseweb="select"] > div {
        background-color: #1e2d3d !important;
        border: 1px solid #2e4a62 !important;
        border-radius: 8px !important;
        color: #e0e8f0 !important;
    }

    /* ── Text input ── */
    div[data-baseweb="input"] > div {
        background-color: #1e2d3d !important;
        border: 1px solid #2e4a62 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #e0e8f0 !important;
    }

    /* ── Main area ── */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ── Hero header ── */
    .hero-header {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #0d1b2a 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid #1e3a5f;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .hero-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7ecfff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-header p {
        margin: 0.4rem 0 0;
        color: #8ba3be;
        font-size: 0.95rem;
    }

    /* ── Info cards ── */
    .info-card {
        background: #0d1b2a;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 1rem;
    }
    .info-card .label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #7ecfff;
    }
    .info-card .value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e0e8f0;
        margin-top: 0.2rem;
    }

    /* ── Tab headers ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #0d1b2a;
        border-radius: 10px;
        gap: 4px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8ba3be !important;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e4d82, #2a1f5e) !important;
        color: #ffffff !important;
    }

    /* ── Load button & Download button ── */
    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #1e4d82, #4c1d95);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(30,77,130,0.4);
    }
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30,77,130,0.6);
        background: linear-gradient(135deg, #2563a8, #5b21b6);
    }

    /* ── Section divider ── */
    hr.divider {
        border: none;
        border-top: 1px solid #1e3a5f;
        margin: 1.5rem 0;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #4a6a8a;
    }
    .empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
    .empty-state p { font-size: 1rem; }

    /* ── Code / JSON block ── */
    code, pre {
        font-family: 'Fira Code', monospace !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <h1>⚽ StatsBomb Event Explorer (JSON Mode)</h1>
        <p>Browse & inspect raw StatsBomb event and 360 data preserved directly in pure JSON format.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏆 Match Selection")

    # ── Competitions JSON ─────────────────────────────────────────────────────
    comp_list: list = []
    selected_comp_json = None
    selected_season_name = None
    selected_match_id = None
    selected_match_json = None
    match_label = None

    with st.spinner("Loading competitions JSON…"):
        try:
            comp_list = load_competitions(username, password)
        except Exception as e:
            st.error(f"Could not load competitions:\n{e}")

    if comp_list:
        # Filter for competitions from England only
        england_comps = [
            c for c in comp_list
            if str(c.get("country_name", "")).strip().lower() == "england"
        ]

        if not england_comps:
            st.warning("No competitions found for England.")
        else:
            # Group competitions strictly by competition_id
            comp_by_id = {}
            display_to_id = {}

            for c in england_comps:
                c_id = c.get("competition_id")
                c_name = c.get("competition_name", "")
                country = c.get("country_name", "")
                gender = str(c.get("competition_gender", "")).strip()

                if c_id not in comp_by_id:
                    comp_by_id[c_id] = []
                    if gender and gender.lower() != "male":
                        display = f"{c_name} ({gender.capitalize()}) · {country}"
                    else:
                        display = f"{c_name} · {country}"
                    display_to_id[display] = c_id

                comp_by_id[c_id].append(c)

            sorted_comp_labels = sorted(display_to_id.keys())
            selected_comp_label = st.selectbox("🌍 Competition", sorted_comp_labels)
            selected_comp_id = display_to_id[selected_comp_label]

            # Seasons available strictly for the selected competition
            comp_items = comp_by_id[selected_comp_id]
            season_dict = {}
            for item in comp_items:
                m_avail = item.get("match_available")
                m_avail_360 = item.get("match_available_360")
                # Filter out seasons without available matches if availability info is present
                if "match_available" in item and m_avail is None and m_avail_360 is None:
                    continue
                s_name = str(item.get("season_name", ""))
                s_id = item.get("season_id", 0)
                season_dict[s_name] = (s_id, item)

            # Fallback if filtering yielded empty season dict
            if not season_dict:
                for item in comp_items:
                    s_name = str(item.get("season_name", ""))
                    s_id = item.get("season_id", 0)
                    season_dict[s_name] = (s_id, item)

            # Sort seasons by season_id descending
            sorted_seasons = sorted(
                season_dict.keys(), key=lambda s: season_dict[s][0], reverse=True
            )
            selected_season_name = st.selectbox("📅 Season", sorted_seasons)

            season_id, selected_comp_json = season_dict[selected_season_name]
            comp_id = int(selected_comp_json.get("competition_id"))

            # ── Matches JSON ──────────────────────────────────────────────────────
            with st.spinner("Loading matches JSON…"):
                try:
                    matches_list = load_matches(comp_id, season_id, username, password)
                except Exception as e:
                    st.error(f"Could not load matches:\n{e}")
                    matches_list = []

            if matches_list:
                match_dict = {}
                for m in matches_list:
                    m_id = m.get("match_id")
                    # Home/Away can be string or dict in StatsBomb JSON
                    home = m.get("home_team", {})
                    home_name = (
                        home.get("home_team_name")
                        if isinstance(home, dict)
                        else m.get("home_team_name", "?")
                    )
                    away = m.get("away_team", {})
                    away_name = (
                        away.get("away_team_name")
                        if isinstance(away, dict)
                        else m.get("away_team_name", "?")
                    )
                    m_date = str(m.get("match_date", ""))[:10]
                    label = f"{m_date}  ·  {home_name} vs {away_name}"
                    match_dict[label] = (m_id, m)

                match_labels = list(match_dict.keys())
                selected_match_label = st.selectbox("⚽ Match", match_labels)
                selected_match_id, selected_match_json = match_dict[selected_match_label]
                match_label = selected_match_label
            else:
                st.info("No available matches found for this season.")
    else:
        st.warning("No competitions loaded.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    load_disabled = selected_match_id is None
    load_clicked = st.button("⚡ Load Match Data (JSON)", disabled=load_disabled)

# ── Session state ─────────────────────────────────────────────────────────────
if "loaded_data" not in st.session_state:
    st.session_state.loaded_data = None

if load_clicked and selected_match_id is not None:
    with st.spinner("Fetching event, 360, player stats, and team stats JSON data — this may take a moment…"):
        events_json = load_events(selected_match_id, username, password)
        frames_360_json = load_360_data(selected_match_id, username, password)
        player_stats_json = load_player_match_stats(selected_match_id, username, password)
        team_stats_json = load_team_match_stats(selected_match_id, username, password)

    st.session_state.loaded_data = {
        "match_label": match_label,
        "match_id": selected_match_id,
        "match_json": selected_match_json,
        "comp_json": selected_comp_json,
        "events_json": events_json,
        "frames_360_json": frames_360_json,
        "player_stats_json": player_stats_json,
        "team_stats_json": team_stats_json,
    }
    st.success("✅ Match events, 360 frames, player & team stats loaded in pure JSON format!")

# ── Main content ──────────────────────────────────────────────────────────────
data = st.session_state.loaded_data

if data is None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="icon">🏟️</div>
            <p>Select a <strong>competition</strong>, <strong>season</strong>, and <strong>match</strong>
            in the sidebar, then click <em>Load Match Data (JSON)</em> to explore raw JSON datasets.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # ── Match summary cards ────────────────────────────────────────────────────
    st.markdown(f"### 📋 Match: `{data['match_label']}`")

    events_json: list = data.get("events_json", [])
    frames_360_json: list = data.get("frames_360_json", [])
    player_stats_json: list = data.get("player_stats_json", [])
    team_stats_json: list = data.get("team_stats_json", [])
    match_json: dict = data.get("match_json", {})
    comp_json: dict = data.get("comp_json", {})

    # Extract distinct event types from events_json
    event_types = sorted(
        list(
            {
                ev.get("type", {}).get("name")
                for ev in events_json
                if isinstance(ev, dict) and isinstance(ev.get("type"), dict) and ev.get("type").get("name")
            }
        )
    )

    # 360 metrics from JSON
    lb_pass_count = sum(
        1 for f in frames_360_json if isinstance(f, dict) and f.get("line_breaking_pass")
    )
    space_receipt_count = sum(
        1 for f in frames_360_json if isinstance(f, dict) and f.get("ball_receipt_in_space")
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f'<div class="info-card"><div class="label">Total Events (JSON)</div>'
            f'<div class="value">{len(events_json):,}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="info-card"><div class="label">360 Frames (JSON)</div>'
            f'<div class="value">{len(frames_360_json):,}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="info-card"><div class="label">Player Stats (JSON)</div>'
            f'<div class="value">{len(player_stats_json):,}</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="info-card"><div class="label">Team Stats (JSON)</div>'
            f'<div class="value">{len(team_stats_json):,}</div></div>',
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f'<div class="info-card"><div class="label">Line Breaking Passes</div>'
            f'<div class="value">{lb_pass_count:,}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Tabs for JSON Data Explorer ──────────────────────────────────────────
    tab_events, tab_360, tab_player_stats, tab_team_stats, tab_meta = st.tabs(
        [
            "📊 Event Data (JSON)",
            "🎯 360 Frames (JSON)",
            "🏃 Player Match Stats (JSON)",
            "🛡️ Team Match Stats (JSON)",
            "📋 Match Metadata (JSON)",
        ]
    )

    # ── Tab 1: Event Data (JSON) ──────────────────────────────────────────────
    with tab_events:
        st.markdown("#### 📊 Raw Event JSON Dataset")

        if not events_json:
            st.info("No event JSON data available.")
        else:
            # Controls
            ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])
            with ctrl1:
                selected_types = st.multiselect(
                    "🏷️ Filter by Event Type",
                    options=event_types,
                    default=[],
                    placeholder="All Event Types",
                )
            with ctrl2:
                search_query = st.text_input(
                    "🔍 Search Event JSON",
                    placeholder="Search keywords, player names, team names, IDs...",
                )
            with ctrl3:
                view_mode = st.selectbox(
                    "👁️ View Mode",
                    options=["Interactive Tree", "Formatted JSON Code", "Sample Array (10 items)"],
                )

            # Filter logic on JSON objects
            filtered_events = events_json
            if selected_types:
                filtered_events = [
                    ev for ev in filtered_events
                    if isinstance(ev, dict)
                    and isinstance(ev.get("type"), dict)
                    and ev.get("type").get("name") in selected_types
                ]

            if search_query:
                query_lower = search_query.lower()
                filtered_events = [
                    ev for ev in filtered_events
                    if query_lower in json.dumps(ev).lower()
                ]

            st.caption(
                f"Showing **{len(filtered_events):,}** of **{len(events_json):,}** event JSON objects"
            )

            # Download JSON button
            st.download_button(
                label="📥 Download Events JSON",
                data=json.dumps(filtered_events, indent=2),
                file_name=f"events_match_{data['match_id']}.json",
                mime="application/json",
                key="download_events_json",
            )

            st.markdown("<hr class='divider'>", unsafe_allow_html=True)

            # Render based on view mode
            if view_mode == "Interactive Tree":
                # Limit initial display to first 200 matching items to keep browser performant
                display_limit = st.slider(
                    "Max JSON objects to render in interactive tree",
                    min_value=10,
                    max_value=min(500, max(10, len(filtered_events))),
                    value=min(50, max(10, len(filtered_events))),
                    step=10,
                    key="event_tree_limit",
                )
                st.json(filtered_events[:display_limit], expanded=False)
            elif view_mode == "Formatted JSON Code":
                max_code_items = min(100, len(filtered_events))
                json_str = json.dumps(filtered_events[:max_code_items], indent=2)
                st.code(json_str, language="json")
                if len(filtered_events) > max_code_items:
                    st.caption(f"Showing first {max_code_items} items in code view. Use download button for full JSON.")
            else:
                for idx, ev in enumerate(filtered_events[:10]):
                    ev_type = ev.get("type", {}).get("name", "Event")
                    ev_time = f"{ev.get('minute', 0)}':{ev.get('second', 0):02d}"
                    team_name = ev.get("team", {}).get("name", "")
                    st.subheader(f"#{ev.get('index', idx+1)} {ev_type} ({ev_time}) — {team_name}")
                    st.json(ev, expanded=False)

    # ── Tab 2: 360 Frames (JSON) ──────────────────────────────────────────────
    with tab_360:
        st.markdown("#### 🎯 StatsBomb 360 Frames JSON Dataset")

        if not frames_360_json:
            st.info("No StatsBomb 360 frame JSON data available for this match.")
        else:
            ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])
            with ctrl1:
                filter_360 = st.multiselect(
                    "⚡ Filter 360 Features",
                    options=["line_breaking_pass", "ball_receipt_in_space", "has_freeze_frame"],
                    default=[],
                )
            with ctrl2:
                search_360 = st.text_input(
                    "🔍 Search 360 JSON",
                    placeholder="Search event UUID, visible area, freeze frame...",
                )
            with ctrl3:
                view_mode_360 = st.selectbox(
                    "👁️ View Mode (360)",
                    options=["Interactive Tree", "Formatted JSON Code", "Sample Array (10 items)"],
                    key="view_mode_360",
                )

            filtered_360 = frames_360_json
            if "line_breaking_pass" in filter_360:
                filtered_360 = [f for f in filtered_360 if isinstance(f, dict) and f.get("line_breaking_pass")]
            if "ball_receipt_in_space" in filter_360:
                filtered_360 = [f for f in filtered_360 if isinstance(f, dict) and f.get("ball_receipt_in_space")]
            if "has_freeze_frame" in filter_360:
                filtered_360 = [f for f in filtered_360 if isinstance(f, dict) and len(f.get("freeze_frame") or []) > 0]

            if search_360:
                s_lower = search_360.lower()
                filtered_360 = [f for f in filtered_360 if s_lower in json.dumps(f).lower()]

            st.caption(
                f"Showing **{len(filtered_360):,}** of **{len(frames_360_json):,}** 360 frame JSON objects"
            )

            st.download_button(
                label="📥 Download 360 Frames JSON",
                data=json.dumps(filtered_360, indent=2),
                file_name=f"360_frames_match_{data['match_id']}.json",
                mime="application/json",
                key="download_360_json",
            )

            st.markdown("<hr class='divider'>", unsafe_allow_html=True)

            if view_mode_360 == "Interactive Tree":
                display_limit_360 = st.slider(
                    "Max JSON objects to render",
                    min_value=10,
                    max_value=min(500, max(10, len(filtered_360))),
                    value=min(50, max(10, len(filtered_360))),
                    step=10,
                    key="limit_360",
                )
                st.json(filtered_360[:display_limit_360], expanded=False)
            elif view_mode_360 == "Formatted JSON Code":
                max_code_360 = min(100, len(filtered_360))
                json_str = json.dumps(filtered_360[:max_code_360], indent=2)
                st.code(json_str, language="json")
                if len(filtered_360) > max_code_360:
                    st.caption(f"Showing first {max_code_360} items in code view. Use download button for full JSON.")
            else:
                for idx, frame in enumerate(filtered_360[:10]):
                    uuid = frame.get("event_uuid", f"frame_{idx}")
                    st.subheader(f"Frame #{idx+1} (Event UUID: `{uuid}`)")
                    st.json(frame, expanded=False)

    # ── Tab 3: Player Match Stats (JSON) ──────────────────────────────────────
    with tab_player_stats:
        st.markdown("#### 🏃 StatsBomb Player Match Stats JSON Dataset (v8.0.0)")

        if not player_stats_json:
            st.info("No player match stats JSON data available for this match.")
        else:
            teams = sorted(
                list(
                    {
                        p.get("team_name")
                        for p in player_stats_json
                        if isinstance(p, dict) and p.get("team_name")
                    }
                )
            )
            players = sorted(
                list(
                    {
                        p.get("player_name")
                        for p in player_stats_json
                        if isinstance(p, dict) and p.get("player_name")
                    }
                )
            )

            ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.5, 1.5, 2, 1])
            with ctrl1:
                selected_teams = st.multiselect(
                    "🛡️ Filter by Team",
                    options=teams,
                    default=[],
                    placeholder="All Teams",
                    key="player_team_filter",
                )
            with ctrl2:
                selected_players = st.multiselect(
                    "🏃 Filter by Player",
                    options=players,
                    default=[],
                    placeholder="All Players",
                    key="player_name_filter",
                )
            with ctrl3:
                search_player = st.text_input(
                    "🔍 Search Player Stats JSON",
                    placeholder="Search metrics, OBV, passes, xG...",
                    key="search_player_stats",
                )
            with ctrl4:
                view_mode_player = st.selectbox(
                    "👁️ View Mode",
                    options=["Interactive Tree", "Formatted JSON Code", "Sample Array (Player Cards)"],
                    key="view_mode_player_stats",
                )

            filtered_player_stats = player_stats_json
            if selected_teams:
                filtered_player_stats = [
                    p for p in filtered_player_stats
                    if isinstance(p, dict) and p.get("team_name") in selected_teams
                ]
            if selected_players:
                filtered_player_stats = [
                    p for p in filtered_player_stats
                    if isinstance(p, dict) and p.get("player_name") in selected_players
                ]
            if search_player:
                p_lower = search_player.lower()
                filtered_player_stats = [
                    p for p in filtered_player_stats
                    if p_lower in json.dumps(p).lower()
                ]

            st.caption(
                f"Showing **{len(filtered_player_stats):,}** of **{len(player_stats_json):,}** player stats JSON objects"
            )

            st.download_button(
                label="📥 Download Player Stats JSON",
                data=json.dumps(filtered_player_stats, indent=2),
                file_name=f"player_match_stats_{data['match_id']}.json",
                mime="application/json",
                key="download_player_stats_json",
            )

            st.markdown("<hr class='divider'>", unsafe_allow_html=True)

            if view_mode_player == "Interactive Tree":
                display_limit_p = st.slider(
                    "Max JSON objects to render",
                    min_value=5,
                    max_value=min(200, max(5, len(filtered_player_stats))),
                    value=min(25, max(5, len(filtered_player_stats))),
                    step=5,
                    key="limit_player_stats",
                )
                st.json(filtered_player_stats[:display_limit_p], expanded=False)
            elif view_mode_player == "Formatted JSON Code":
                max_code_p = min(50, len(filtered_player_stats))
                json_str = json.dumps(filtered_player_stats[:max_code_p], indent=2)
                st.code(json_str, language="json")
                if len(filtered_player_stats) > max_code_p:
                    st.caption(f"Showing first {max_code_p} items in code view. Use download button for full JSON.")
            else:
                for idx, p_item in enumerate(filtered_player_stats[:10]):
                    p_name = p_item.get("player_name", f"Player #{idx+1}")
                    t_name = p_item.get("team_name", "")
                    mins = p_item.get("player_match_minutes", "?")
                    st.subheader(f"⚽ {p_name} ({t_name}) — Played: {mins} mins")
                    st.json(p_item, expanded=False)

    # ── Tab 4: Team Match Stats (JSON) ────────────────────────────────────────
    with tab_team_stats:
        st.markdown("#### 🛡️ StatsBomb Team Match Stats JSON Dataset (v4.0.0)")

        if not team_stats_json:
            st.info("No team match stats JSON data available for this match.")
        else:
            team_names = sorted(
                list(
                    {
                        t.get("team_name")
                        for t in team_stats_json
                        if isinstance(t, dict) and t.get("team_name")
                    }
                )
            )

            ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])
            with ctrl1:
                selected_team_names = st.multiselect(
                    "🛡️ Filter by Team",
                    options=team_names,
                    default=[],
                    placeholder="All Teams",
                    key="team_stats_filter",
                )
            with ctrl2:
                search_team = st.text_input(
                    "🔍 Search Team Stats JSON",
                    placeholder="Search PPDA, possession, xG, OBV, passes...",
                    key="search_team_stats",
                )
            with ctrl3:
                view_mode_team = st.selectbox(
                    "👁️ View Mode",
                    options=["Interactive Tree", "Formatted JSON Code", "Sample Array (Team Cards)"],
                    key="view_mode_team_stats",
                )

            filtered_team_stats = team_stats_json
            if selected_team_names:
                filtered_team_stats = [
                    t for t in filtered_team_stats
                    if isinstance(t, dict) and t.get("team_name") in selected_team_names
                ]
            if search_team:
                t_lower = search_team.lower()
                filtered_team_stats = [
                    t for t in filtered_team_stats
                    if t_lower in json.dumps(t).lower()
                ]

            st.caption(
                f"Showing **{len(filtered_team_stats):,}** of **{len(team_stats_json):,}** team stats JSON objects"
            )

            st.download_button(
                label="📥 Download Team Stats JSON",
                data=json.dumps(filtered_team_stats, indent=2),
                file_name=f"team_match_stats_{data['match_id']}.json",
                mime="application/json",
                key="download_team_stats_json",
            )

            st.markdown("<hr class='divider'>", unsafe_allow_html=True)

            if view_mode_team == "Interactive Tree":
                st.json(filtered_team_stats, expanded=True)
            elif view_mode_team == "Formatted JSON Code":
                json_str = json.dumps(filtered_team_stats, indent=2)
                st.code(json_str, language="json")
            else:
                for idx, t_item in enumerate(filtered_team_stats):
                    t_name = t_item.get("team_name", f"Team #{idx+1}")
                    opp_name = t_item.get("opposition_name", "")
                    xg = t_item.get("team_match_op_xg", "?")
                    st.subheader(f"🛡️ {t_name} (vs {opp_name}) — Open Play xG: {xg}")
                    st.json(t_item, expanded=False)

    # ── Tab 5: Match Metadata (JSON) ──────────────────────────────────────────
    with tab_meta:
        st.markdown("#### 📋 Match & Competition JSON Metadata")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### ⚽ Match JSON")
            st.json(match_json, expanded=True)
            st.download_button(
                label="📥 Download Match Meta JSON",
                data=json.dumps(match_json, indent=2),
                file_name=f"match_metadata_{data['match_id']}.json",
                mime="application/json",
                key="download_match_meta",
            )

        with col_m2:
            st.markdown("##### 🏆 Competition JSON")
            st.json(comp_json, expanded=True)
            st.download_button(
                label="📥 Download Competition Meta JSON",
                data=json.dumps(comp_json, indent=2),
                file_name=f"competition_metadata_{comp_json.get('competition_id', 'meta')}.json",
                mime="application/json",
                key="download_comp_meta",
            )

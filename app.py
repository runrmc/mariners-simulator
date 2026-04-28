import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random

from src.data.batting import fetch_mariners_batting, get_latest_completed_season
from src.data.pitching import fetch_mariners_pitching, build_pitchers
from src.models.roster import build_roster, sort_batting_order
from src.simulation.game import simulate_game
from src.modes.quick_sim import run_quick_sim
from src.modes.series import run_series
from src.modes.tournament import (
    run_tournament, pick_top_n, pick_random_8,
    get_seed_order, WIN_TOTALS, load_teams, simulate_series
)
from src.output.box_score import generate_box_score, get_player_game_stats, accumulate_stats, get_series_mvp
from src.output.exporter import (
    export_box_score_csv, export_series_csv,
    export_quick_sim_csv, export_tournament_csv
)

LATEST_SEASON = get_latest_completed_season()
FIRST_SEASON = 1977
ALL_YEARS = list(range(FIRST_SEASON, LATEST_SEASON + 1))

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mariners Simulator",
    page_icon="⚾",
    layout="wide"
)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Seattle_Mariners_logo_%28low_resolution%29.svg/200px-Seattle_Mariners_logo_%28low_resolution%29.svg.png",
    width=100
)
st.sidebar.title("⚾ Mariners Simulator")
st.sidebar.markdown("*Who is the greatest M's team ever?*")
st.sidebar.markdown("---")

mode = st.sidebar.radio(
    "Select Mode",
    ["🏟️ Single Game", "🏆 Series", "🎯 Tournament", "⚡ Quick Sim"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Seasons available:** {FIRST_SEASON} — {LATEST_SEASON}")


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_roster_cached(year: int):
    df = fetch_mariners_batting(year)
    return sort_batting_order(build_roster(df))


@st.cache_data(show_spinner=False)
def load_pitchers_cached(year: int, top_n: int = 5):
    df = fetch_mariners_pitching(year, top_n=top_n)
    return build_pitchers(df)


def runs_chart(run_history1: list, run_history2: list, year1: int, year2: int):
    """Plot run distribution histogram."""
    df = pd.DataFrame({
        "Runs": run_history1 + run_history2,
        "Team": [f"{year1} Mariners"] * len(run_history1) +
                [f"{year2} Mariners"] * len(run_history2)
    })
    fig = px.histogram(
        df, x="Runs", color="Team", barmode="overlay",
        title="Run Distribution",
        opacity=0.7,
        color_discrete_sequence=["#005C5C", "#C4CED4"]
    )
    fig.update_layout(bargap=0.1)
    return fig


def win_pct_chart(year1: int, year2: int, wins1: int, wins2: int):
    """Plot win percentage bar chart."""
    total = wins1 + wins2
    fig = go.Figure(data=[
        go.Bar(
            name=f"{year1} Mariners",
            x=[f"{year1}"],
            y=[wins1 / total * 100],
            marker_color="#005C5C"
        ),
        go.Bar(
            name=f"{year2} Mariners",
            x=[f"{year2}"],
            y=[wins2 / total * 100],
            marker_color="#C4CED4"
        )
    ])
    fig.update_layout(
        title="Win Percentage",
        yaxis_title="Win %",
        yaxis_range=[0, 100],
        barmode="group"
    )
    return fig


def player_stats_chart(accumulated_stats: dict, stat: str = "rbi", top_n: int = 10):
    """Bar chart of top players by a given stat."""
    rows = [
        {"Player": name, stat.upper(): s.get(stat, 0)}
        for name, s in accumulated_stats.items()
        if s.get("ab", 0) > 0
    ]
    df = pd.DataFrame(rows).sort_values(stat.upper(), ascending=False).head(top_n)
    fig = px.bar(
        df, x="Player", y=stat.upper(),
        title=f"Top {top_n} Players by {stat.upper()}",
        color_discrete_sequence=["#005C5C"]
    )
    fig.update_layout(xaxis_tickangle=-35)
    return fig


# ─────────────────────────────────────────────
# Single Game Mode
# ─────────────────────────────────────────────
if mode == "🏟️ Single Game":
    st.title("🏟️ Single Game")
    st.markdown("Pick two seasons, select your starting pitchers, and simulate a game.")

    col1, col2 = st.columns(2)
    with col1:
        home_year = st.selectbox("Home Team Year", ALL_YEARS, index=ALL_YEARS.index(2001))
    with col2:
        away_year = st.selectbox("Away Team Year", ALL_YEARS, index=ALL_YEARS.index(2024))

    if st.button("Load Rosters & Pitchers"):
        with st.spinner("Loading..."):
            try:
                st.session_state.home_roster = load_roster_cached(home_year)
                st.session_state.home_pitchers = load_pitchers_cached(home_year)
                st.session_state.away_roster = load_roster_cached(away_year)
                st.session_state.away_pitchers = load_pitchers_cached(away_year)
                st.session_state.home_year = home_year
                st.session_state.away_year = away_year
                st.success("Rosters loaded!")
            except Exception as e:
                st.error(f"Error loading rosters: {e}")

    if "home_roster" in st.session_state:
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"{st.session_state.home_year} Batting Order")
            for i, p in enumerate(st.session_state.home_roster[:9], 1):
                obp = p.prob_single + p.prob_double + p.prob_triple + p.prob_hr + p.prob_walk
                st.markdown(f"**{i}.** {p.name} — OBP: {obp:.3f}")

            home_pitcher_names = [p.name for p in st.session_state.home_pitchers]
            home_pitcher_choice = st.selectbox(
                f"{st.session_state.home_year} Starting Pitcher",
                home_pitcher_names
            )
            home_pitcher = st.session_state.home_pitchers[home_pitcher_names.index(home_pitcher_choice)]
            st.markdown(f"ERA: {home_pitcher.era} | WHIP: {home_pitcher.whip} | K/9: {home_pitcher.k_per_9}")

        with col2:
            st.subheader(f"{st.session_state.away_year} Batting Order")
            for i, p in enumerate(st.session_state.away_roster[:9], 1):
                obp = p.prob_single + p.prob_double + p.prob_triple + p.prob_hr + p.prob_walk
                st.markdown(f"**{i}.** {p.name} — OBP: {obp:.3f}")

            away_pitcher_names = [p.name for p in st.session_state.away_pitchers]
            away_pitcher_choice = st.selectbox(
                f"{st.session_state.away_year} Starting Pitcher",
                away_pitcher_names
            )
            away_pitcher = st.session_state.away_pitchers[away_pitcher_names.index(away_pitcher_choice)]
            st.markdown(f"ERA: {away_pitcher.era} | WHIP: {away_pitcher.whip} | K/9: {away_pitcher.k_per_9}")

        st.markdown("---")
        if st.button("▶️ Simulate Game", type="primary"):
            with st.spinner("Simulating..."):
                result = simulate_game(
                    st.session_state.home_roster,
                    st.session_state.away_roster,
                    home_year=st.session_state.home_year,
                    away_year=st.session_state.away_year,
                    home_pitcher=home_pitcher,
                    away_pitcher=away_pitcher,
                    verbose=False
                )

            # Score display
            col1, col2, col3 = st.columns(3)
            col1.metric(f"{result['away_year']} Mariners", result['away_score'])
            col2.markdown("<h2 style='text-align:center'>FINAL</h2>", unsafe_allow_html=True)
            col3.metric(f"{result['home_year']} Mariners", result['home_score'])

            winner = result['winner']
            st.success(f"🏆 {winner} Mariners win!")

            # Box score
            st.markdown("---")
            st.subheader("Box Score")
            st.text(generate_box_score(result))

            # Play by play
            st.markdown("---")
            st.subheader("Play by Play")
            for play in result["plays"]:
                st.markdown(f"- {play['description']}")

            # Export
            st.markdown("---")
            if st.button("📄 Export Box Score to CSV"):
                path = export_box_score_csv(result)
                st.success(f"Exported to {path}")


# ─────────────────────────────────────────────
# Series Mode
# ─────────────────────────────────────────────
elif mode == "🏆 Series":
    st.title("🏆 Series — Best of 7")
    st.markdown("Simulate a full 7-game series with pitcher rotation and MVP tracking.")

    col1, col2 = st.columns(2)
    with col1:
        year1 = st.selectbox("Team 1", ALL_YEARS, index=ALL_YEARS.index(2001))
    with col2:
        year2 = st.selectbox("Team 2", ALL_YEARS, index=ALL_YEARS.index(2024))

    if st.button("▶️ Simulate Series", type="primary"):
        with st.spinner("Simulating series..."):
            try:
                df_b1 = fetch_mariners_batting(year1)
                df_p1 = fetch_mariners_pitching(year1, top_n=3)
                roster1 = sort_batting_order(build_roster(df_b1))
                pitchers1 = build_pitchers(df_p1)

                df_b2 = fetch_mariners_batting(year2)
                df_p2 = fetch_mariners_pitching(year2, top_n=3)
                roster2 = sort_batting_order(build_roster(df_b2))
                pitchers2 = build_pitchers(df_p2)

                wins1 = 0
                wins2 = 0
                game_num = 1
                accumulated_stats = {}
                game_results = []

                while wins1 < 4 and wins2 < 4:
                    pitcher1 = pitchers1[(game_num - 1) % len(pitchers1)]
                    pitcher2 = pitchers2[(game_num - 1) % len(pitchers2)]

                    result = simulate_game(
                        roster1, roster2,
                        home_year=year1, away_year=year2,
                        home_pitcher=pitcher1, away_pitcher=pitcher2,
                        verbose=False
                    )

                    home_stats = get_player_game_stats(result["home_roster"])
                    away_stats = get_player_game_stats(result["away_roster"])
                    accumulated_stats = accumulate_stats(accumulated_stats, home_stats)
                    accumulated_stats = accumulate_stats(accumulated_stats, away_stats)

                    if result["winner"] == year1:
                        wins1 += 1
                    else:
                        wins2 += 1

                    game_results.append({
                        "Game": game_num,
                        f"{year1} Runs": result["home_score"],
                        f"{year2} Runs": result["away_score"],
                        "Winner": f"{result['winner']} Mariners"
                    })
                    game_num += 1

                series_winner = year1 if wins1 > wins2 else year2
                mvp_name, mvp_stats = get_series_mvp(accumulated_stats)

                st.session_state.series_result = {
                    "winner": series_winner,
                    "wins1": wins1,
                    "wins2": wins2,
                    "mvp": mvp_name,
                    "mvp_stats": mvp_stats,
                    "accumulated_stats": accumulated_stats,
                    "game_results": game_results,
                    "year1": year1,
                    "year2": year2,
                }
            except Exception as e:
                st.error(f"Error: {e}")

    if "series_result" in st.session_state:
        r = st.session_state.series_result
        y1, y2 = r["year1"], r["year2"]

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{y1} Mariners", f"{r['wins1']} wins")
        col2.markdown("<h2 style='text-align:center'>SERIES</h2>", unsafe_allow_html=True)
        col3.metric(f"{y2} Mariners", f"{r['wins2']} wins")
        st.success(f"🏆 {r['winner']} Mariners win the series!")

        # Game log
        st.markdown("---")
        st.subheader("Game Log")
        st.dataframe(pd.DataFrame(r["game_results"]), use_container_width=True)

        # MVP
        st.markdown("---")
        st.subheader("🌟 Series MVP")
        mvp = r["mvp_stats"]
        avg = mvp['hits'] / mvp['ab'] if mvp.get('ab', 0) > 0 else 0
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Player", r["mvp"])
        col2.metric("AVG", f"{avg:.3f}")
        col3.metric("HR", mvp.get('home_runs', 0))
        col4.metric("RBI", mvp.get('rbi', 0))
        col5.metric("H", mvp.get('hits', 0))

        # Charts
        st.markdown("---")
        st.subheader("Player Stats")
        stat_choice = st.selectbox("Stat", ["rbi", "hits", "home_runs", "walks", "strikeouts"])
        st.plotly_chart(
            player_stats_chart(r["accumulated_stats"], stat=stat_choice),
            use_container_width=True
        )

        # Export
        if st.button("📄 Export Series to CSV"):
            path = export_series_csv(r, y1, y2)
            st.success(f"Exported to {path}")


# ─────────────────────────────────────────────
# Tournament Mode
# ─────────────────────────────────────────────
elif mode == "🎯 Tournament":
    st.title("🎯 Tournament")
    st.markdown("Single elimination, best-of-7 each round.")

    tournament_type = st.radio(
        "Tournament Type",
        ["Top 8 by wins", "Top 16 by wins", "Custom 8 teams", "Random 8 teams"]
    )

    years = []

    if tournament_type == "Top 8 by wins":
        years = pick_top_n(8)
    elif tournament_type == "Top 16 by wins":
        years = pick_top_n(16)
    elif tournament_type == "Random 8 teams":
        if st.button("🎲 Generate Random 8"):
            st.session_state.random_years = pick_random_8()
        if "random_years" in st.session_state:
            years = st.session_state.random_years
    elif tournament_type == "Custom 8 teams":
        st.markdown("Pick 8 years for your tournament:")
        cols = st.columns(4)
        custom_years = []
        for i in range(8):
            with cols[i % 4]:
                y = st.selectbox(f"Team {i+1}", ALL_YEARS, key=f"custom_{i}",
                                 index=ALL_YEARS.index(2001 if i == 0 else
                                 ALL_YEARS[min(i * 5, len(ALL_YEARS)-1)]))
                custom_years.append(y)
        if len(set(custom_years)) == 8:
            years = custom_years
        else:
            st.warning("Please select 8 different years.")

    if years:
        seeded = get_seed_order(years)
        st.markdown("### Bracket")
        cols = st.columns(len(seeded))
        for i, (year, col) in enumerate(zip(seeded, cols), 1):
            col.metric(f"Seed {i}", f"{year}", f"{WIN_TOTALS.get(year, '?')} W")

        if st.button("▶️ Run Tournament", type="primary"):
            with st.spinner("Running tournament... this may take a minute."):
                try:
                    result = run_tournament(seeded)
                    st.session_state.tournament_result = result
                except Exception as e:
                    st.error(f"Error: {e}")

    if "tournament_result" in st.session_state:
        r = st.session_state.tournament_result
        st.markdown("---")
        st.success(f"🏆 {r['champion']} Mariners are the greatest team in Mariners history!")

        if r.get("mvp"):
            st.subheader("🌟 Tournament MVP")
            mvp = r["mvp_stats"]
            avg = mvp['hits'] / mvp['ab'] if mvp.get('ab', 0) > 0 else 0
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Player", r["mvp"])
            col2.metric("AVG", f"{avg:.3f}")
            col3.metric("HR", mvp.get('home_runs', 0))
            col4.metric("RBI", mvp.get('rbi', 0))

        if r.get("all_stats"):
            st.markdown("---")
            st.subheader("Tournament Stats")
            stat_choice = st.selectbox("Stat", ["rbi", "hits", "home_runs", "walks", "strikeouts"],
                                       key="tourney_stat")
            st.plotly_chart(
                player_stats_chart(r["all_stats"], stat=stat_choice),
                use_container_width=True
            )

        if st.button("📄 Export Tournament to CSV"):
            path = export_tournament_csv(r)
            st.success(f"Exported to {path}")


# ─────────────────────────────────────────────
# Quick Sim Mode
# ─────────────────────────────────────────────
elif mode == "⚡ Quick Sim":
    st.title("⚡ Quick Sim")
    st.markdown("Simulate up to 1000 games and see who comes out on top.")

    col1, col2 = st.columns(2)
    with col1:
        year1 = st.selectbox("Team 1", ALL_YEARS, index=ALL_YEARS.index(2001))
    with col2:
        year2 = st.selectbox("Team 2", ALL_YEARS, index=ALL_YEARS.index(2024))

    n_games = st.slider("Number of games", min_value=1, max_value=1000, value=100, step=10)

    if st.button("▶️ Run Simulation", type="primary"):
        with st.spinner(f"Simulating {n_games} games..."):
            try:
                df_b1 = fetch_mariners_batting(year1)
                df_p1 = fetch_mariners_pitching(year1)
                roster1 = sort_batting_order(build_roster(df_b1))
                pitchers1 = build_pitchers(df_p1)

                df_b2 = fetch_mariners_batting(year2)
                df_p2 = fetch_mariners_pitching(year2)
                roster2 = sort_batting_order(build_roster(df_b2))
                pitchers2 = build_pitchers(df_p2)

                wins1 = 0
                wins2 = 0
                run_history1 = []
                run_history2 = []

                for _ in range(n_games):
                    pitcher1 = random.choice(pitchers1)
                    pitcher2 = random.choice(pitchers2)

                    result = simulate_game(
                        roster1, roster2,
                        home_year=year1, away_year=year2,
                        home_pitcher=pitcher1, away_pitcher=pitcher2,
                        verbose=False
                    )

                    run_history1.append(result["home_score"])
                    run_history2.append(result["away_score"])

                    if result["winner"] == year1:
                        wins1 += 1
                    else:
                        wins2 += 1

                st.session_state.quick_result = {
                    "year1": year1,
                    "year2": year2,
                    "wins1": wins1,
                    "wins2": wins2,
                    "win_pct1": wins1 / n_games * 100,
                    "win_pct2": wins2 / n_games * 100,
                    "avg_runs1": sum(run_history1) / n_games,
                    "avg_runs2": sum(run_history2) / n_games,
                    "run_history1": run_history1,
                    "run_history2": run_history2,
                    "n_games": n_games,
                }
            except Exception as e:
                st.error(f"Error: {e}")

    if "quick_result" in st.session_state:
        r = st.session_state.quick_result
        st.markdown("---")

        col1, col2 = st.columns(2)
        col1.metric(f"{r['year1']} Mariners", f"{r['wins1']} wins", f"{r['win_pct1']:.1f}%")
        col2.metric(f"{r['year2']} Mariners", f"{r['wins2']} wins", f"{r['win_pct2']:.1f}%")

        champion = r['year1'] if r['wins1'] > r['wins2'] else r['year2']
        st.success(f"🏆 {champion} Mariners win the simulation!")

        col1, col2 = st.columns(2)
        col1.metric(f"{r['year1']} Avg Runs/Game", f"{r['avg_runs1']:.2f}")
        col2.metric(f"{r['year2']} Avg Runs/Game", f"{r['avg_runs2']:.2f}")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                runs_chart(r['run_history1'], r['run_history2'], r['year1'], r['year2']),
                use_container_width=True
            )
        with col2:
            st.plotly_chart(
                win_pct_chart(r['year1'], r['year2'], r['wins1'], r['wins2']),
                use_container_width=True
            )

        if st.button("📄 Export to CSV"):
            path = export_quick_sim_csv(r)
            st.success(f"Exported to {path}")
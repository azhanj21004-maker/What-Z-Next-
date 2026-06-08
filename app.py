import streamlit as st
import pickle
import pandas as pd
import requests
# streamlit run app.py run on terminal to open it on browser
#Shortcul for replace:ctrl+R
#cntrl+c to stop streamlit

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="What'zNext?", page_icon="🎬", layout="wide")

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --gold:   #E8B84B;
    --dark:   #0D0D0D;
    --card:   #161616;
    --border: #2a2a2a;
    --muted:  #666;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--dark) !important;
    color: #e8e8e8;
}

#MainMenu, footer, header { visibility: hidden; }

.hero {
    text-align: center;
    padding: 2.5rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.hero h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3rem, 8vw, 6rem);
    letter-spacing: 0.08em;
    color: var(--gold);
    margin: 0;
    line-height: 1;
}
.hero p {
    color: var(--muted);
    font-size: 0.9rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}

label { color: #aaa !important; font-size: 0.8rem !important; letter-spacing: 0.1em; text-transform: uppercase; }

div.stButton > button {
    background: var(--gold);
    color: #000;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.2rem;
    letter-spacing: 0.12em;
    border: none;
    border-radius: 4px;
    padding: 0.55rem 2.5rem;
    cursor: pointer;
    transition: opacity 0.2s;
    width: 100%;
}
div.stButton > button:hover { opacity: 0.85; }

.movie-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.25s, box-shadow 0.25s;
    height: 100%;
    cursor: pointer;
}
.movie-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 40px rgba(232,184,75,0.18);
}
.movie-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
}
.movie-card .info { padding: 0.75rem; }
.movie-card .rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.8rem;
    color: var(--gold);
    letter-spacing: 0.12em;
}
.movie-card .title {
    font-size: 0.88rem;
    font-weight: 500;
    line-height: 1.3;
    margin-top: 0.2rem;
    color: #e8e8e8;
}
.click-hint {
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.1em;
    color: #fff;
    margin-bottom: 1rem;
    border-left: 4px solid var(--gold);
    padding-left: 0.75rem;
}

.no-poster {
    width: 100%;
    aspect-ratio: 2/3;
    background: #1e1e1e;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
}

/* ── Plot popup box ── */
.plot-box {
    background: #1a1a1a;
    border: 1px solid var(--gold);
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
}
.plot-box img {
    width: 130px;
    min-width: 130px;
    border-radius: 6px;
    object-fit: cover;
}
.plot-box .plot-content h2 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    color: var(--gold);
    margin: 0 0 0.3rem;
    letter-spacing: 0.06em;
}
.plot-box .plot-content .meta {
    font-size: 0.78rem;
    color: var(--muted);
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.plot-box .plot-content p {
    font-size: 0.92rem;
    line-height: 1.7;
    color: #ccc;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


# ── Config ─────────────────────────────────────────────────────────────────────
OMDB_API_KEY = "28f20bf"
PLACEHOLDER  = "https://via.placeholder.com/500x750/1e1e1e/444?text=No+Poster"


# ── OMDb helpers ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_poster(movie_title: str) -> str:
    """Fetch poster URL from OMDb."""
    try:
        url  = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        poster = data.get("Poster", "")
        if poster and poster != "N/A":
            return poster
    except Exception:
        pass
    return PLACEHOLDER


@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_title: str) -> dict:
    """Fetch full movie details (plot, year, genre, rating) from OMDb."""
    try:
        url  = f"http://www.omdbapi.com/?t={movie_title}&plot=short&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        if data.get("Response") == "True":
            return {
                "title":  data.get("Title", movie_title),
                "year":   data.get("Year", "N/A"),
                "genre":  data.get("Genre", "N/A"),
                "rating": data.get("imdbRating", "N/A"),
                "plot":   data.get("Plot", "No plot available."),
                "poster": data.get("Poster", PLACEHOLDER),
            }
    except Exception:
        pass
    return {
        "title": movie_title, "year": "N/A", "genre": "N/A",
        "rating": "N/A", "plot": "No plot available.", "poster": PLACEHOLDER,
    }


# ── Data & recommendation ──────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
    similarity  = pickle.load(open("similarity.pkl",  "rb"))
    return pd.DataFrame(movies_dict), similarity

movies, similarity = load_data()

def recommend(movie: str):
    idx      = movies[movies["title"] == movie].index[0]
    dists    = similarity[idx]
    top5     = sorted(enumerate(dists), key=lambda x: x[1], reverse=True)[1:6]
    titles   = [movies.iloc[i].title for i, _ in top5]
    posters  = [fetch_poster(t) for t in titles]
    return titles, posters


# ── Session state (tracks which movie was clicked) ────────────────────────────
if "selected_detail" not in st.session_state:
    st.session_state.selected_detail = None


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>What'Z Next?</h1>
    <p>Discover your next favourite film</p>
</div>
""", unsafe_allow_html=True)

col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
with col_sel:
    selected = st.selectbox("Choose a movie", movies["title"].values)
with col_btn:
    clicked = st.button("Recommend")


# ── Results ────────────────────────────────────────────────────────────────────
if clicked:
    # Reset detail view when new recommendations are fetched
    st.session_state.selected_detail = None
    with st.spinner("Finding recommendations …"):
        titles, posters = recommend(selected)
    # Store in session so cards stay after a button click
    st.session_state.rec_titles  = titles
    st.session_state.rec_posters = posters

if "rec_titles" in st.session_state:
    titles  = st.session_state.rec_titles
    posters = st.session_state.rec_posters

    st.markdown('<p class="section-header">Recommended for you</p>', unsafe_allow_html=True)

    cols = st.columns(5, gap="small")
    for idx, (col, title, poster) in enumerate(zip(cols, titles, posters), 1):
        with col:
            img_html = (
                f'<img src="{poster}" alt="{title}">'
                if poster != PLACEHOLDER
                else '<div class="no-poster">🎬</div>'
            )
            st.markdown(f"""
            <div class="movie-card">
                {img_html}
                <div class="info">
                    <div class="rank">#{idx} Pick</div>
                    <div class="title">{title}</div>
                    <div class="click-hint">👆 click below for plot</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Invisible button below each card
            if st.button(f"📖 {title}", key=f"btn_{idx}"):
                st.session_state.selected_detail = title

    # ── Plot detail box ────────────────────────────────────────────────────────
    if st.session_state.selected_detail:
        with st.spinner("Loading plot …"):
            d = fetch_movie_details(st.session_state.selected_detail)

        poster_img = (
            f'<img src="{d["poster"]}" alt="{d["title"]}">'
            if d["poster"] != PLACEHOLDER else ""
        )

        st.markdown(f"""
        <div class="plot-box">
            {poster_img}
            <div class="plot-content">
                <h2>{d["title"]}</h2>
                <div class="meta">
                    📅 {d["year"]} &nbsp;|&nbsp; 🎭 {d["genre"]} &nbsp;|&nbsp; ⭐ {d["rating"]} / 10
                </div>
                <p>{d["plot"]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
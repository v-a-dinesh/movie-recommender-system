import pickle
import streamlit as st
import requests
from requests.exceptions import ConnectTimeout, RequestException
import time
import json
import os
from datetime import datetime, timedelta
import gdown
import zipfile

# Configuration
OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "d13737da")  # Use environment variable
OMDB_BASE_URL = "http://www.omdbapi.com/"

# Cache system to reduce API calls
class PosterCache:
    def __init__(self, cache_duration_days=7):
        self.cache_duration = timedelta(days=cache_duration_days)
        # Use Streamlit's session state for caching instead of file system
        if 'poster_cache' not in st.session_state:
            st.session_state.poster_cache = {}
    
    def get(self, movie_title):
        cache = st.session_state.poster_cache
        if movie_title in cache:
            cached_data = cache[movie_title]
            # Check if cache is still valid
            try:
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < self.cache_duration:
                    return cached_data['data']
            except:
                pass
        return None
    
    def set(self, movie_title, data):
        st.session_state.poster_cache[movie_title] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

# Initialize cache
poster_cache = PosterCache()

def fetch_poster_omdb(movie_title, year=None):
    """Fetch movie poster from OMDB API with caching"""
    
    # Check cache first
    cache_key = f"{movie_title}_{year}" if year else movie_title
    cached_data = poster_cache.get(cache_key)
    
    if cached_data:
        poster_url = cached_data.get('Poster', 'N/A')
        if poster_url and poster_url != 'N/A':
            return poster_url
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster+Available"
    
    try:
        # Build the query parameters
        params = {
            'apikey': OMDB_API_KEY,
            't': movie_title,  # Search by title
            'type': 'movie'
        }
        
        # Add year if available for more accurate results
        if year:
            params['y'] = year
        
        # Make the request
        response = requests.get(OMDB_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Cache the response
        if data.get('Response') == 'True':
            poster_cache.set(cache_key, data)
            poster_url = data.get('Poster', 'N/A')
            
            if poster_url and poster_url != 'N/A':
                return poster_url
            else:
                return "https://via.placeholder.com/300x450?text=No+Poster+Available"
        else:
            # Movie not found
            return "https://via.placeholder.com/300x450?text=Movie+Not+Found"
            
    except ConnectTimeout:
        st.warning(f"Connection timeout while fetching poster for {movie_title}")
        return "https://via.placeholder.com/300x450?text=Connection+Timeout"
        
    except RequestException as e:
        st.error(f"Error fetching poster: {str(e)}")
        return "https://via.placeholder.com/300x450?text=Error+Loading+Poster"
        
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return "https://via.placeholder.com/300x450?text=Error"

def get_movie_details_omdb(movie_title, year=None):
    """Get additional movie details from OMDB with caching"""
    
    # Check cache first
    cache_key = f"{movie_title}_{year}" if year else movie_title
    cached_data = poster_cache.get(cache_key)
    
    if cached_data and cached_data.get('Response') == 'True':
        return {
            'title': cached_data.get('Title', movie_title),
            'year': cached_data.get('Year', 'N/A'),
            'rating': cached_data.get('imdbRating', 'N/A'),
            'plot': cached_data.get('Plot', 'No plot available'),
            'genre': cached_data.get('Genre', 'N/A'),
            'director': cached_data.get('Director', 'N/A'),
            'actors': cached_data.get('Actors', 'N/A'),
            'poster': cached_data.get('Poster', 'N/A'),
            'runtime': cached_data.get('Runtime', 'N/A'),
            'awards': cached_data.get('Awards', 'N/A')
        }
    
    try:
        params = {
            'apikey': OMDB_API_KEY,
            't': movie_title,
            'type': 'movie',
            'plot': 'short'
        }
        
        if year:
            params['y'] = year
        
        response = requests.get(OMDB_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Response') == 'True':
            # Cache the response
            poster_cache.set(cache_key, data)
            
            return {
                'title': data.get('Title', movie_title),
                'year': data.get('Year', 'N/A'),
                'rating': data.get('imdbRating', 'N/A'),
                'plot': data.get('Plot', 'No plot available'),
                'genre': data.get('Genre', 'N/A'),
                'director': data.get('Director', 'N/A'),
                'actors': data.get('Actors', 'N/A'),
                'poster': data.get('Poster', 'N/A'),
                'runtime': data.get('Runtime', 'N/A'),
                'awards': data.get('Awards', 'N/A')
            }
        else:
            return None
            
    except Exception as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return None

def recommend(movie, movies, similarity):
    """Generate movie recommendations"""
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_movies = []
        
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, i in enumerate(distances[1:6]):
            # Update progress
            progress = (idx + 1) / 5
            progress_bar.progress(progress)
            status_text.text(f'Loading recommendation {idx + 1} of 5...')
            
            # Get movie title
            movie_title = movies.iloc[i[0]].title
            
            # Small delay to avoid hitting rate limits
            if idx > 0:
                time.sleep(0.1)
            
            # Fetch poster and details from OMDB
            poster_url = fetch_poster_omdb(movie_title)
            movie_details = get_movie_details_omdb(movie_title)
            
            recommended_movies.append({
                'title': movie_title,
                'poster': poster_url,
                'details': movie_details,
                'similarity_score': distances[idx + 1][1]
            })
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return recommended_movies
        
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return []

# Function to download data files from Google Drive or other source
@st.cache_resource
def download_data_files():
    """Download model files if they don't exist"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    movie_list_path = os.path.join(data_dir, "movie_list.pkl")
    similarity_path = os.path.join(data_dir, "similarity.pkl")
    
    # Check if files already exist
    if os.path.exists(movie_list_path) and os.path.exists(similarity_path):
        return movie_list_path, similarity_path
    
    # If using Google Drive, replace these with your file IDs
    # Example:
    # movie_list_id = "YOUR_GOOGLE_DRIVE_FILE_ID_FOR_MOVIE_LIST"
    # similarity_id = "YOUR_GOOGLE_DRIVE_FILE_ID_FOR_SIMILARITY"
    
    # For now, return the expected paths
    # You'll need to upload these files to your deployment
    return movie_list_path, similarity_path

# Load data with error handling
@st.cache_data
def load_data():
    try:
        # Try to load from data directory first
        movie_list_path, similarity_path = download_data_files()
        
        if os.path.exists(movie_list_path) and os.path.exists(similarity_path):
            movies = pickle.load(open(movie_list_path, 'rb'))
            similarity = pickle.load(open(similarity_path, 'rb'))
            return movies, similarity
        else:
            st.error("Required data files not found. Please upload movie_list.pkl and similarity.pkl to the data directory.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# Streamlit UI
st.set_page_config(page_title="Movie Recommender System", page_icon="🎬", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .movie-card {
        padding: 10px;
        border-radius: 10px;
        background-color: #f0f0f0;
        margin-bottom: 10px;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title('🎬 Movie Recommender System')
st.markdown("Powered by OMDB API")
st.markdown("---")

# Load the data
movies, similarity = load_data()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Movie selection
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "🔍 Type or select a movie from the dropdown",
        movie_list,
        help="Select a movie to get recommendations"
    )

with col2:
    st.write("")
    st.write("")
    show_details = st.checkbox("Show selected movie details", value=True)

# Show selected movie details
if show_details:
    with st.container():
        with st.spinner("Fetching movie details..."):
            selected_details = get_movie_details_omdb(selected_movie)
            if selected_details:
                col1, col2 = st.columns([1, 3])
                with col1:
                    if selected_details['poster'] != 'N/A':
                        st.image(selected_details['poster'], width=200)
                    else:
                        st.image("https://via.placeholder.com/200x300?text=No+Poster", width=200)
                with col2:
                    st.subheader(selected_details['title'])
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Rating", f"⭐ {selected_details['rating']}/10")
                    with col_b:
                        st.metric("Year", f"📅 {selected_details['year']}")
                    with col_c:
                        st.metric("Runtime", f"⏱️ {selected_details['runtime']}")
                    
                    st.write(f"**Genre:** {selected_details['genre']}")
                    st.write(f"**Director:** {selected_details['director']}")
                    st.write(f"**Cast:** {selected_details['actors']}")
                    st.write(f"**Plot:** {selected_details['plot']}")
                    if selected_details['awards'] != 'N/A':
                        st.write(f"**Awards:** 🏆 {selected_details['awards']}")

st.markdown("---")

# Recommendation button
if st.button('🎯 Get Movie Recommendations', type='primary'):
    with st.spinner('Finding similar movies...'):
        recommended_movies = recommend(selected_movie, movies, similarity)
    
    if recommended_movies:
        st.markdown("### 🎬 Recommended Movies")
        st.markdown("Based on your selection, you might also enjoy these movies:")
        
        # Display recommendations in columns
        cols = st.columns(5)
        
        for idx, movie in enumerate(recommended_movies):
            with cols[idx]:
                # Movie poster
                st.image(movie['poster'], use_container_width=True)
                
                # Movie title
                st.markdown(f"**{movie['title']}**")
                
                # Similarity score
                st.progress(movie['similarity_score'])
                st.caption(f"Match: {movie['similarity_score']:.1%}")
                
                # Show additional details if available
                if movie['details']:
                    st.caption(f"⭐ {movie['details']['rating']}/10")
                    st.caption(f"📅 {movie['details']['year']}")
                    
                    # Expandable section for more details
                    with st.expander("More info"):
                        st.write(f"**Genre:** {movie['details']['genre']}")
                        st.write(f"**Director:** {movie['details']['director']}")
                        st.write(f"**Plot:** {movie['details']['plot']}")
    else:
        st.error("Unable to generate recommendations. Please try again.")

# Sidebar with API status and settings
with st.sidebar:
    st.header("📊 API Status")
    
    # Test OMDB connection
    if st.button("Test OMDB Connection"):
        with st.spinner("Testing connection..."):
            try:
                test_params = {
                    'apikey': OMDB_API_KEY,
                    't': 'Inception',
                    'type': 'movie'
                }
                response = requests.get(OMDB_BASE_URL, params=test_params, timeout=5)
                data = response.json()
                
                if response.status_code == 200 and data.get('Response') == 'True':
                    st.success("✅ OMDB API connection successful!")
                    st.info(f"Test movie: {data.get('Title')} ({data.get('Year')})")
                    st.caption(f"Director: {data.get('Director')}")
                elif data.get('Error'):
                    st.error(f"❌ API Error: {data.get('Error')}")
                    if "key" in data.get('Error', '').lower():
                        st.warning("Please make sure you've activated your API key by clicking the link in your email!")
                else:
                    st.error("❌ Unknown API error")
                    
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
    
    st.markdown("---")
    
    # Cache statistics
    st.header("💾 Cache Statistics")
    if 'poster_cache' in st.session_state:
        st.metric("Cached Movies", len(st.session_state.poster_cache))
        
        if st.button("Clear Cache"):
            st.session_state.poster_cache = {}
            st.success("Cache cleared!")
            st.rerun()
    else:
        st.info("No cache data available")
    
    st.markdown("---")
    
    # API Information
    st.header("ℹ️ API Information")
    st.caption("Using OMDB API")
    st.caption("Free tier: 1,000 requests/day")
    st.caption(f"API Key: {OMDB_API_KEY[:4]}****")
    
    # Add a link to get more API keys
    st.markdown("[Get your own API key](http://www.omdbapi.com/apikey.aspx)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Built with ❤️ using Streamlit and OMDB API</p>
        <p style='font-size: 0.8em; color: gray;'>Note: Movie recommendations are based on content similarity</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Optional: Add batch download feature
if st.checkbox("📥 Export Recommendations"):
    if 'recommended_movies' in locals() and recommended_movies:
        # Create a text summary
        summary = f"Movie Recommendations for: {selected_movie}\n\n"
        for i, movie in enumerate(recommended_movies, 1):
            summary += f"{i}. {movie['title']}"
            if movie['details']:
                summary += f" ({movie['details']['year']}) - Rating: {movie['details']['rating']}/10"
            summary += f"\n   Similarity: {movie['similarity_score']:.1%}\n"
            if movie['details']:
                summary += f"   Genre: {movie['details']['genre']}\n"
                summary += f"   Plot: {movie['details']['plot']}\n"
            summary += "\n"
        
        # Download button
        st.download_button(
            label="Download Recommendations as Text",
            data=summary,
            file_name=f"recommendations_for_{selected_movie.replace(' ', '_')}.txt",
            mime="text/plain"
        )
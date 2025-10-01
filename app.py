import streamlit as st
import pickle as pkl
import requests
import os  # For env vars
from dotenv import load_dotenv

load_dotenv() 

# Load data (ensure these files are in the project root)
movies = pkl.load(open('movies.pkl', 'rb'))
movies_list = movies['title'].values
similarity = pkl.load(open('similarity.pkl', 'rb'))

# TMDB API key from env var (set in Render dashboard)
TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # Fallback if not set: '96b1edc390e0d1f9d35abc467ae35f05' (but don't use in prod!)

@st.cache_data  # Cache to avoid repeated API calls during session
def fetch_poster(movie_id):
    if not TMDB_API_KEY:
        st.error("TMDB API key not set. Check environment variables.")
        return None
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}'
        )
        response.raise_for_status()  # Raise error for bad status
        data = response.json()
        if data.get('poster_path'):
            return 'https://image.tmdb.org/t/p/w500/' + data['poster_path']
        return None  # No poster
    except Exception as e:
        st.error(f"Error fetching poster for movie ID {movie_id}: {str(e)}")
        return None

def recommend(movie):  # Fixed typo
    try:
        movie_idx = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_idx]
        movie_indices = sorted(list(enumerate(distances)),reverse=True,key=lambda x: x[1])[1:6]
        
        recommended_movies = []
        recommended_movies_posters = []
        
        for i in movie_indices:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            poster = fetch_poster(movie_id)
            recommended_movies_posters.append(poster if poster else 'https://via.placeholder.com/500x750?text=No+Poster')  # Fallback image
            
        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], []

st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select the movie", movies_list)

if st.button('Recommend'):
    names, posters = recommend(selected_movie)
    
    if names:  # Only display if recommendations found
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(names[0])
            st.image(posters[0])
        with col2:
            st.text(names[1])
            st.image(posters[1])
        with col3:
            st.text(names[2])
            st.image(posters[2])
        with col4:
            st.text(names[3])
            st.image(posters[3])
        with col5:
            st.text(names[4])
            st.image(posters[4])
    else:
        st.warning("No recommendations available. Try another movie.")

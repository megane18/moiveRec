import requests
import json
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()
access_token = os.getenv('TMDB_ACCESS_TOKEN')  # Make sure to have this in your .env file

# API endpoint base URL
base_url = 'https://api.themoviedb.org/3'

def get_movie_details(movie_id):
    """
    Fetch movie details from TMDB API using Bearer token authentication
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'accept': 'application/json'
    }
    
    url = f'{base_url}/search/movie?query=Batman'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Find the specific movie in results
        for movie in data['results']:
            if movie['id'] == movie_id:
                return movie
        raise Exception(f"Movie with ID {movie_id} not found in results")
    else:
        raise Exception(f"Error fetching movie details: {response.status_code} - {response.text}")

def get_movie_poster(movie_id):
    """
    Get movie poster path
    """
    movie_data = get_movie_details(movie_id)
    if movie_data and 'poster_path' in movie_data:
        return movie_data['poster_path']
    return None

def display_movie_info(movie_id):
    """
    Display formatted movie information
    """
    try:
        movie_data = get_movie_details(movie_id)
        poster_path = get_movie_poster(movie_id)
        
        print("\nMovie Details:")
        print(f"Title: {movie_data['title']}")
        print(f"Release Date: {movie_data['release_date']}")
        print(f"Overview: {movie_data['overview']}")
        if poster_path:
            print(f"Poster URL: https://image.tmdb.org/t/p/w500{poster_path}")
        else:
            print("No poster available")
        print(f"Vote Average: {movie_data['vote_average']}")
        print(f"Vote Count: {movie_data['vote_count']}")
            
    except KeyError as e:
        print(f"Error: Could not find key {e} in movie data")
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    display_movie_info(268)  # Batman (1989)
"""
Spotify Track Popularity Dashboard
A simple Flask web application to display Spotify track popularity
"""

import os
from flask import Flask, render_template, request, jsonify
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
import base64
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_client_id_here')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_client_secret_here')

# Cache for access token
token_cache = {
    'access_token': None,
    'expires_at': None
}


class SpotifyAPIError(Exception):
    """Custom exception for Spotify API errors"""
    pass


def get_access_token():
    """
    Get Spotify access token using Client Credentials flow
    Implements caching to avoid unnecessary API calls
    """
    try:
        # Check if cached token is still valid
        if token_cache['access_token'] and token_cache['expires_at']:
            if datetime.now() < token_cache['expires_at']:
                return token_cache['access_token']
        
        # Request new token
        auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        json_result = response.json()
        access_token = json_result['access_token']
        expires_in = json_result['expires_in']
        
        # Cache the token
        token_cache['access_token'] = access_token
        token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in - 60)
        
        return access_token
        
    except Timeout:
        raise SpotifyAPIError("Request to Spotify authentication server timed out. Please try again.")
    except ConnectionError:
        raise SpotifyAPIError("Could not connect to Spotify. Please check your internet connection.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise SpotifyAPIError("Invalid Spotify credentials. Please check your Client ID and Secret.")
        raise SpotifyAPIError(f"Spotify authentication failed: {str(e)}")
    except Exception as e:
        raise SpotifyAPIError(f"Unexpected error during authentication: {str(e)}")


def get_track_info(track_id):
    """
    Fetch track information from Spotify API
    
    Args:
        track_id (str): Spotify track ID
        
    Returns:
        dict: Track information including popularity, name, artists, etc.
    """
    try:
        # Validate track ID format (basic validation)
        if not track_id or len(track_id) != 22:
            raise SpotifyAPIError("Invalid track ID format. Spotify track IDs are 22 characters long.")
        
        access_token = get_access_token()
        
        url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Handle specific HTTP errors
        if response.status_code == 404:
            raise SpotifyAPIError(f"Track not found. Please check the track ID: {track_id}")
        elif response.status_code == 400:
            raise SpotifyAPIError("Invalid request. The track ID may be malformed.")
        elif response.status_code == 429:
            raise SpotifyAPIError("Rate limit exceeded. Please wait a moment and try again.")
        
        response.raise_for_status()
        
        track_data = response.json()
        
        # Extract relevant information
        return {
            'id': track_data['id'],
            'name': track_data['name'],
            'artists': ', '.join([artist['name'] for artist in track_data['artists']]),
            'album': track_data['album']['name'],
            'popularity': track_data['popularity'],
            'release_date': track_data['album']['release_date'],
            'duration_ms': track_data['duration_ms'],
            'preview_url': track_data.get('preview_url'),
            'album_image': track_data['album']['images'][0]['url'] if track_data['album']['images'] else None,
            'external_url': track_data['external_urls']['spotify']
        }
        
    except SpotifyAPIError:
        raise
    except Timeout:
        raise SpotifyAPIError("Request timed out while fetching track data. Please try again.")
    except ConnectionError:
        raise SpotifyAPIError("Connection error. Please check your internet connection.")
    except KeyError as e:
        raise SpotifyAPIError(f"Unexpected response format from Spotify API: missing {str(e)}")
    except Exception as e:
        raise SpotifyAPIError(f"Unexpected error while fetching track data: {str(e)}")


@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')


@app.route('/api/track/<track_id>')
def get_track(track_id):
    """
    API endpoint to get track information
    
    Returns JSON with track data or error message
    """
    try:
        track_info = get_track_info(track_id)
        return jsonify({
            'success': True,
            'data': track_info
        })
    except SpotifyAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again later.'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please try again later.'
    }), 500


if __name__ == '__main__':
    # Validate environment variables
    if SPOTIFY_CLIENT_ID == 'your_client_id_here' or SPOTIFY_CLIENT_SECRET == 'your_client_secret_here':
        print("⚠️  WARNING: Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
        print("   or update them directly in the script.")
    
    # Get port from environment variable (for cloud hosting) or default to 5000
    PORT = int(os.getenv('PORT', 5000))
    
    # Use 0.0.0.0 to allow external connections (required for deployment)
    app.run(host='0.0.0.0', port=PORT, debug=False)

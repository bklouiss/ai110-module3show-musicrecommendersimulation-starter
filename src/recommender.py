from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Score all songs and return top-k recommendations.

        Args:
            user: UserProfile object with favorite_genre, favorite_mood, target_energy, likes_acoustic
            k: Number of recommendations to return (default: 5)

        Returns:
            List of top-k Song objects sorted by score descending
        """
        # Convert UserProfile to dict for score_song_with_reasons
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

        # Score each song
        scored_songs = []
        for song in self.songs:
            # Convert Song dataclass to dict for scoring
            song_dict = {
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'genre': song.genre,
                'mood': song.mood,
                'energy': song.energy,
                'tempo_bpm': song.tempo_bpm,
                'valence': song.valence,
                'danceability': song.danceability,
                'acousticness': song.acousticness,
            }
            score, reasons = score_song_with_reasons(song_dict, user_prefs)
            scored_songs.append((song, score))

        # Sort by score descending, then by song ID ascending for tie-breaking
        scored_songs.sort(key=lambda x: (-x[1], x[0].id))

        # Return top-k Song objects
        return [song for song, score in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Generate a human-readable explanation for why a song was recommended.

        Args:
            user: UserProfile object
            song: Song object to explain

        Returns:
            String explaining the match across all scoring dimensions
        """
        # Convert to dicts for scoring
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

        song_dict = {
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'genre': song.genre,
            'mood': song.mood,
            'energy': song.energy,
            'tempo_bpm': song.tempo_bpm,
            'valence': song.valence,
            'danceability': song.danceability,
            'acousticness': song.acousticness,
        }

        score, reasons = score_song_with_reasons(song_dict, user_prefs)
        explanation = f"{song.title} (Score: {score:.2f})\n  • " + "\n  • ".join(reasons)
        return explanation

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Converts numeric columns to appropriate types for computation.

    Args:
        csv_path: Path to the CSV file (e.g., "data/songs.csv")

    Returns:
        List of dictionaries, one per song, with numeric values as float/int
    """
    print(f"Loading songs from {csv_path}...")
    songs = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric columns to float or int
                song = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': float(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness']),
                }
                songs.append(song)

        print(f"Loaded {len(songs)} songs successfully!")
        return songs

    except FileNotFoundError:
        print(f"Error: Could not find file {csv_path}")
        return []
    except Exception as e:
        print(f"Error loading songs: {e}")
        return []

def score_song_with_reasons(song: Dict, user_prefs: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences using the Algorithm Recipe.
    Returns both the numeric score and a list of reasons for transparency.

    Scoring rules (from Algorithm Recipe):
    - Genre match: +2.0 points
    - Mood match: +1.5 points
    - Energy proximity: 1.0 - |song.energy - user.target_energy| points
    - Acoustic preference: ±0.5 points

    Args:
        song: Dictionary with keys: genre, mood, energy, acousticness, etc.
        user_prefs: Dictionary with keys: favorite_genre, favorite_mood,
                    target_energy, likes_acoustic

    Returns:
        Tuple of (score: float, reasons: List[str])
    """
    score = 0.0
    reasons = []

    # Genre match: +2.0 if exact match (primary filter)
    if song['genre'] == user_prefs['favorite_genre']:
        score += 2.0
        reasons.append(f"Genre match: {song['genre']} (+2.0)")
    else:
        reasons.append(f"Genre mismatch: {song['genre']} vs {user_prefs['favorite_genre']} (0.0)")

    # Mood match: +1.5 if exact match (secondary filter)
    if song['mood'] == user_prefs['favorite_mood']:
        score += 1.5
        reasons.append(f"Mood match: {song['mood']} (+1.5)")
    else:
        reasons.append(f"Mood mismatch: {song['mood']} vs {user_prefs['favorite_mood']} (0.0)")

    # Energy proximity: penalize distance from target (0.0 to 1.0)
    energy_distance = abs(song['energy'] - user_prefs['target_energy'])
    energy_score = 1.0 - energy_distance
    score += energy_score
    reasons.append(f"Energy proximity: {song['energy']} vs {user_prefs['target_energy']} (+{energy_score:.3f})")

    # Acoustic preference: ±0.5 bonus/penalty
    acoustic_bonus = 0.0
    if user_prefs['likes_acoustic']:
        if song['acousticness'] > 0.6:
            acoustic_bonus = 0.5
            reasons.append(f"Acoustic match: {song['acousticness']:.2f} high (+0.5)")
        elif song['acousticness'] < 0.3:
            acoustic_bonus = -0.5
            reasons.append(f"Electric preference instead: {song['acousticness']:.2f} low (-0.5)")
    else:
        if song['acousticness'] < 0.3:
            acoustic_bonus = 0.5
            reasons.append(f"Electric match: {song['acousticness']:.2f} low (+0.5)")
        elif song['acousticness'] > 0.6:
            acoustic_bonus = -0.5
            reasons.append(f"Acoustic preference instead: {song['acousticness']:.2f} high (-0.5)")

    score += acoustic_bonus

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of recommendation logic.
    Scores all songs, ranks them, and returns top-k with explanations.

    Args:
        user_prefs: Dictionary with favorite_genre, favorite_mood, target_energy, likes_acoustic
        songs: List of song dictionaries loaded from CSV
        k: Number of recommendations to return (default: 5)

    Returns:
        List of (song_dict, score, explanation_string) tuples, sorted by score descending
    """
    scored_songs = []

    # Score each song
    for song in songs:
        score, reasons = score_song_with_reasons(song, user_prefs)
        # Combine reasons into a single explanation string
        explanation = "; ".join(reasons)
        scored_songs.append((song, score, explanation))

    # Sort by score descending, then by song ID ascending for tie-breaking
    scored_songs.sort(key=lambda x: (-x[1], x[0]['id']))

    # Return top-k
    return scored_songs[:k]

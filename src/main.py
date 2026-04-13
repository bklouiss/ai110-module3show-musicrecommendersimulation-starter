"""
Command line runner for the Music Recommender Simulation.

Tests multiple user profiles to evaluate system behavior across diverse preferences.
"""

from src.recommender import load_songs, recommend_songs


def display_recommendations(user_prefs: dict, songs: list, k: int = 5) -> None:
    """Display top-k recommendations for a user profile with detailed scoring breakdown."""
    recommendations = recommend_songs(user_prefs, songs, k)

    # Display header
    print("\n" + "="*80)
    print(f"TOP {k} RECOMMENDATIONS FOR: {user_prefs['favorite_genre'].upper()} / {user_prefs['favorite_mood'].upper()}")
    print(f"Profile: Energy={user_prefs['target_energy']}, Acoustic={'Yes' if user_prefs['likes_acoustic'] else 'No'}")
    print("="*80 + "\n")

    # Display each recommendation
    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec

        print(f"{rank}. {song['title'].upper()}")
        print(f"   Artist: {song['artist']}")
        print(f"   Score: {score:.2f} / 5.0")

        # Parse and display reasons
        reasons = explanation.split("; ")
        print(f"   Why this match:")
        for reason in reasons:
            print(f"      • {reason}")
        print()

    print("="*80)


def main() -> None:
    """Run recommender system with multiple diverse user profiles."""
    songs = load_songs("data/songs.csv")

    # Define diverse test profiles
    profiles = [
        {
            "name": "Profile 1: Workout Enthusiast",
            "prefs": {
                "favorite_genre": "pop",
                "favorite_mood": "intense",
                "target_energy": 0.85,
                "likes_acoustic": False
            }
        },
        {
            "name": "Profile 2: Chill Lofi Lover",
            "prefs": {
                "favorite_genre": "lofi",
                "favorite_mood": "chill",
                "target_energy": 0.35,
                "likes_acoustic": True
            }
        },
        {
            "name": "Profile 3: Deep Intense Rock",
            "prefs": {
                "favorite_genre": "rock",
                "favorite_mood": "intense",
                "target_energy": 0.88,
                "likes_acoustic": False
            }
        },
        {
            "name": "Profile 4: Acoustic Jazz Enthusiast",
            "prefs": {
                "favorite_genre": "jazz",
                "favorite_mood": "relaxed",
                "target_energy": 0.40,
                "likes_acoustic": True
            }
        },
        {
            "name": "Profile 5: Adversarial - High Energy + Chill Mood",
            "prefs": {
                "favorite_genre": "ambient",
                "favorite_mood": "chill",
                "target_energy": 0.90,  # Conflicting: high energy but chill mood
                "likes_acoustic": True
            }
        },
    ]

    # Run recommender for each profile
    print("\n" + "#"*80)
    print("# MUSIC RECOMMENDER SYSTEM - MULTI-PROFILE EVALUATION")
    print("#"*80)

    for profile_info in profiles:
        print(f"\n{profile_info['name']}")
        display_recommendations(profile_info['prefs'], songs, k=5)


if __name__ == "__main__":
    main()

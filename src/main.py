"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Workout Enthusiast user profile
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "intense",
        "target_energy": 0.85,
        "likes_acoustic": False
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # Display recommendations with clean formatting
    print("\n" + "="*80)
    print(f"TOP 5 RECOMMENDATIONS FOR: {user_prefs['favorite_genre'].upper()} / {user_prefs['favorite_mood'].upper()}")
    print("="*80 + "\n")

    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec

        # Format the heading
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


if __name__ == "__main__":
    main()

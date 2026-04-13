# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This implementation builds a content-based music recommender using a fixed scoring algorithm. Given a user's favorite genre, mood, target energy level, and acoustic preference, it scores all 20 songs in the catalog and returns the top-5 matches. The system is fully transparent—every recommendation has an explainable score breakdown—making it useful for understanding how recommendation systems can amplify or minimize certain music types.

---

## How The System Works

### Real-World Context

Real-world music recommenders (like Spotify or Apple Music) use **collaborative filtering** (what similar users liked) and **content-based filtering** (song audio features). This simulation implements **pure content-based filtering**: we score songs purely on their musical characteristics and how they match a user's stated preferences. Our version prioritizes **interpretability and simplicity** over accuracy—every recommendation decision is transparent and explainable, which is useful for understanding *why* a system makes choices and where bias might creep in.

### Song Features

Each `Song` object uses these attributes to represent its musical profile:

- **Categorical labels**: `genre` (pop, lofi, rock, etc.) and `mood` (happy, chill, intense, etc.)
- **Numeric audio features**:
  - `energy` (0.0–1.0): perceived loudness and intensity
  - `acousticness` (0.0–1.0): acoustic vs. electronic production
  - `valence` (0.0–1.0): musical positivity or brightness
  - `danceability` (0.0–1.0): rhythmic groove suitability
  - `tempo_bpm`: beats per minute

### User Profile

Each `UserProfile` captures:

- `favorite_genre`: the genre they want to hear
- `favorite_mood`: the emotional tone they're seeking
- `target_energy`: their desired energy level (e.g., 0.8 for high-intensity, 0.3 for calm)
- `likes_acoustic`: boolean preference for acoustic vs. produced sounds

### Scoring Algorithm

For each song, we compute a composite score:

```
score = 
  (2.0 × [genre matches])
  + (1.5 × [mood matches])
  + (1.0 × [1.0 - |song.energy - user.target_energy|])
  + (0.5 × [acoustic preference bonus])
```

**Genre** and **mood** are binary matches (0 or 1). **Energy** uses proximity scoring—songs close to the user's target energy get higher scores than songs with extreme values. **Acousticness** adds a small bonus if the user's preference aligns.

### Ranking & Selection

We sort all songs by score (highest first) and return the top-*k* results. Ties are broken by song ID.

### Algorithm Recipe: Finalized Scoring Logic

The scoring function runs independently for each song:

```python
def score_song(song, user_profile):
    """
    Compute a recommendation score for a single song.
    Higher score = better match for this user.
    """
    score = 0.0
    
    # Genre match: +2.0 if exact match (primary filter)
    if song['genre'] == user_profile['favorite_genre']:
        score += 2.0
    
    # Mood match: +1.5 if exact match (secondary filter)
    if song['mood'] == user_profile['favorite_mood']:
        score += 1.5
    
    # Energy proximity: penalize distance from target (0.0 to 1.0)
    energy_distance = abs(song['energy'] - user_profile['target_energy'])
    score += 1.0 - energy_distance
    
    # Acoustic preference: ±0.5 bonus/penalty
    if user_profile['likes_acoustic']:
        if song['acousticness'] > 0.6:
            score += 0.5
        elif song['acousticness'] < 0.3:
            score -= 0.5
    else:
        if song['acousticness'] < 0.3:
            score += 0.5
        elif song['acousticness'] > 0.6:
            score -= 0.5
    
    return score
```

**Maximum possible score:** 5.0 (perfect match on all dimensions)  
**Minimum possible score:** -1.0 (wrong genre, wrong mood, wrong energy, wrong acoustic type)

**Weighting philosophy:**
- **Genre (2.0)** is the strongest signal—a user asking for "pop" won't be satisfied with metal, even if the energy matches
- **Mood (1.5)** is the secondary indicator—ensures emotional context aligns
- **Energy (1.0)** adds precision—differentiates between two songs of the same genre/mood
- **Acoustic (±0.5)** is a tie-breaker—small but meaningful preference signal

### Known Biases & Limitations

This system makes simplifying assumptions that can introduce bias:

1. **Genre rigidity:** The recommendation heavily favors exact genre matches (+2.0 weight). A user who enjoys both pop and indie rock will rarely see indie rock songs, even when they'd be a great fit. **Impact:** Conservative users get repetitive catalogs; explorers miss serendipitous discoveries.

2. **Mood as a proxy:** Mood is a human label assigned once per song, but the same mood (e.g., "chill") spans very different subgenres (ambient, lofi, jazz). Two "chill" songs might feel nothing alike. **Impact:** System conflates distinct emotional experiences.

3. **Feature brittleness:** Energy and acousticness are treated as universal axes, but they're context-dependent. A 0.8 energy symphony feels completely different than 0.8 energy EDM. **Impact:** Numeric features alone can't capture genre-specific semantics.

4. **No temporal or contextual awareness:** The system doesn't know if you're recommending for a workout, dinner party, or study session. The same user profile always produces the same results. **Impact:** No adaptation to use case.

5. **No diversity penalty:** If the top 5 songs all come from the same artist, the system happily returns all 5. **Impact:** Monotonous recommendations; missed opportunity for variety.

6. **Binary acoustic preference:** Real users have nuanced acoustic preferences that vary by genre (love acoustic guitar in folk, want synths in electronic). **Impact:** Oversimplification forces users into an either/or choice.

### Sample Output: CLI Verification

Running the default "Workout Enthusiast" profile (pop + intense + energy 0.85 + not acoustic):

```
================================================================================
TOP 5 RECOMMENDATIONS FOR: POP / INTENSE
================================================================================

1. GYM HERO
   Artist: Max Pulse
   Score: 4.92 / 5.0
   Why this match:
      • Genre match: pop (+2.0)
      • Mood match: intense (+1.5)
      • Energy proximity: 0.93 vs 0.85 (+0.920)
      • Electric match: 0.05 low (+0.5)

2. SUNRISE CITY
   Artist: Neon Echo
   Score: 3.47 / 5.0
   Why this match:
      • Genre match: pop (+2.0)
      • Mood mismatch: happy vs intense (0.0)
      • Energy proximity: 0.82 vs 0.85 (+0.970)
      • Electric match: 0.18 low (+0.5)

3. CONCRETE JUNGLE
   Artist: Drive City
   Score: 3.00 / 5.0
   Why this match:
      • Genre mismatch: hip-hop vs pop (0.0)
      • Mood match: intense (+1.5)
      • Energy proximity: 0.85 vs 0.85 (+1.000)
      • Electric match: 0.12 low (+0.5)

4. STORM RUNNER
   Artist: Voltline
   Score: 2.94 / 5.0
   Why this match:
      • Genre mismatch: rock vs pop (0.0)
      • Mood match: intense (+1.5)
      • Energy proximity: 0.91 vs 0.85 (+0.940)
      • Electric match: 0.10 low (+0.5)

5. THUNDER STRIKE
   Artist: Iron Beast
   Score: 2.89 / 5.0
   Why this match:
      • Genre mismatch: metal vs pop (0.0)
      • Mood match: intense (+1.5)
      • Energy proximity: 0.96 vs 0.85 (+0.890)
      • Electric match: 0.05 low (+0.5)

================================================================================
```

**Key observations:**
- Gym Hero wins decisively (4.92) because it matches on all four dimensions
- Sunrise City scores well but loses points for "happy" mood instead of "intense"
- Concrete Jungle, Storm Runner, and Thunder Strike show the system's flexibility—despite genre mismatch, songs with matching mood and energy rank in the top 5
- Transparency: Every score component is visible, so users understand *why* they got each recommendation

### Stress Testing: Multi-Profile Evaluation

The system was tested with 5 diverse user profiles to evaluate robustness:

#### **Profile 1: Workout Enthusiast** (pop + intense + high energy + not acoustic)
```
1. GYM HERO              Score: 4.92 ✓ Perfect match (all 4 dimensions)
2. SUNRISE CITY          Score: 3.47 (pop genre, but happy mood)
3. CONCRETE JUNGLE       Score: 3.00 (hip-hop, but intense mood + perfect energy)
4. STORM RUNNER          Score: 2.94 (rock, but intense mood)
5. THUNDER STRIKE        Score: 2.89 (metal, but intense mood)
```
**Observation:** Genre matching dominates. Mood provides secondary ranking. Energy proximity fine-tunes scores.

---

#### **Profile 2: Chill Lofi Lover** (lofi + chill + low energy + acoustic)
```
1. LIBRARY RAIN          Score: 5.00 ★ Perfect score (all 4 dimensions aligned)
2. MIDNIGHT CODING       Score: 4.93 (lofi, chill, energy 0.42 vs 0.35, acoustic)
3. FOCUS FLOW            Score: 3.45 (lofi genre match despite focused mood)
4. SPACEWALK THOUGHTS    Score: 2.93 (ambient, chill, very low energy)
5. COFFEE SHOP STORIES   Score: 1.48 (jazz, but energy match + acoustic)
```
**Observation:** Perfect alignment when all preferences match. System clearly differentiates between lofi songs with the same genre but different moods.

---

#### **Profile 3: Deep Intense Rock** (rock + intense + high energy + not acoustic)
```
1. STORM RUNNER          Score: 4.97 ✓ Perfect match (rock + intense + high energy)
2. CONCRETE JUNGLE       Score: 2.97 (hip-hop, but intense mood + energy match)
3. GYM HERO              Score: 2.95 (pop, but intense mood + high energy)
4. THUNDER STRIKE        Score: 2.92 (metal, but intense mood + high energy)
5. NEON PULSE            Score: 1.49 (electronic, mood mismatch despite energy)
```
**Observation:** Genre matching is critical. Note: Thunder Strike (metal) ranks higher than Neon Pulse (electronic) because mood match (intense vs energetic) matters more than energy proximity.

---

#### **Profile 4: Acoustic Jazz Enthusiast** (jazz + relaxed + low energy + acoustic)
```
1. COFFEE SHOP STORIES   Score: 4.97 ✓ Perfect match (jazz + relaxed + acoustic)
2. REGGAE VIBES          Score: 2.85 (reggae, but relaxed mood + acoustic)
3. FOCUS FLOW            Score: 1.50 (lofi + acoustic, but mood mismatch)
4. MIDNIGHT CODING       Score: 1.48 (lofi + acoustic, but mood mismatch)
5. MOUNTAIN ECHO         Score: 1.46 (folk + acoustic, but mood mismatch)
```
**Observation:** Strong genre bias: jazz songs dominate. Non-jazz recommendations drop to ~1.5/5.0 even with acoustic and energy alignment. This reveals the system's "genre-first" limitation.

---

#### **Profile 5: Adversarial - High Energy + Chill Mood** (ambient + chill + energy 0.9 + acoustic)
```
1. SPACEWALK THOUGHTS    Score: 4.38 (ambient match, mood match, BUT energy 0.28 vs 0.9 = -0.62 penalty)
2. ADVENTURE CALLS       Score: 3.26 (ambient match, mood mismatch)
3. MIDNIGHT CODING       Score: 2.52 (genre miss, mood match, energy miss)
4. LIBRARY RAIN          Score: 2.45 (genre miss, mood match, energy miss)
5. SOUTHERN COMFORT      Score: 1.18 (genre miss, mood miss)
```
**Key Finding:** Genre + mood (3.5 points) outweigh conflicting energy (-0.62 penalty). Spacewalk Thoughts wins despite requesting high energy (0.9) but getting ambient (0.28)—a gap of 0.62!

This reveals a **bias in the system**: categorical features (genre, mood) can mask contradictory numeric preferences. A user who says "I want chill music at 0.9 energy" likely made a mistake or has an unusual taste profile.

---

## Summary of Multi-Profile Findings

| Pattern | Observation |
|---|---|
| **Perfect Matches** | When all 4 dimensions align (Profile 2), scores reach 5.0 |
| **Genre Dominance** | Genre matching (+2.0) is the primary ranking signal |
| **Mood Secondary** | Mood matching (+1.5) ranks second; can overcome genre mismatch |
| **Energy Fine-tuning** | Energy proximity helps differentiate similar songs (e.g., two pop+intense songs) |
| **Edge Cases** | Conflicting inputs (Profile 5: high energy + chill mood) expose the genre/mood bias |
| **Acoustic Preference** | Secondary importance; rarely overrides genre/mood decisions |

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"


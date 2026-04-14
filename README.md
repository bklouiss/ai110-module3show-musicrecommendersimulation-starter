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

![Terminal Output 1](screenshots/terminal1.png)
![Terminal Output 2](screenshots/terminal2.png)

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

### What I Learned

Building this recommender taught me that every design choice encodes a value judgment. By weighting genre at +2.0 and mood at +1.5, I prioritized consistency over serendipity—a user who likes pop will almost never see rock recommendations, no matter how good the song. This makes the system *predictable* and *safe*, but it also creates filter bubbles. In a real system, this could keep users stuck in narrow taste patterns. The adversarial profile test (Profile 5) revealed this clearly: even when a user requests conflicting preferences (high energy + chill mood), the system resorts to genre/mood, silently ignoring the energy conflict. A better system would flag contradictions and ask for clarification.

I also realized that "transparent" scoring isn't the same as "fair" scoring. Users can see *why* they got a recommendation, but they can't easily understand *why* an entire genre of music was excluded. Transparency without explainability can mask unfairness. The Jazz profile test (Profile 4) made this stark: non-jazz songs scored ~1.5/5.0 even with matching mood, energy, and acoustic preference—a 3.49-point gap that users might not notice. This revealed the deepest lesson: recommendation systems aren't neutral tools, they're *amplifiers of bias*.

---

## Model Card: RecommendScore 1.0

### 1. Model Name

**RecommendScore 1.0** — A transparent, content-based music recommendation engine built for educational purposes.

---

### 2. Intended Use

This model is designed to recommend 5 songs from a curated catalog of 20 songs based on a user's stated preferences for genre, mood, energy level, and acoustic preference. 

**Intended audience:** Students exploring how recommendation algorithms work, what biases they embed, and where they succeed or fail.

**Not intended for:** Production use, real commercial music services, or systems serving diverse global audiences.

**Scope:** Works only with the provided 20-song catalog. Cannot handle songs outside this dataset.

---

### 3. How It Works (Short Explanation)

The recommender asks a user four simple questions:
- What's your favorite genre? (e.g., "pop")
- What mood do you want? (e.g., "intense")
- How energetic should it be? (0.0 = calm, 1.0 = energetic)
- Do you prefer acoustic or electronic production?

For each song in the catalog, the system assigns points:
- **+2.0 points** if the genre matches your preference (strongest signal)
- **+1.5 points** if the mood matches
- **+0 to +1.0 points** based on how close the energy is to your target
- **±0.5 points** based on acoustic preference

The songs are ranked by total points (max: 5.0) and the top 5 are returned. Every recommendation includes a breakdown showing why each song scored the way it did.

---

### 4. Data

**Dataset:** `data/songs.csv` contains 20 representative songs.

**What we included:**
- 10 original starter songs
- 10 additional songs representing underrepresented genres (electronic, metal, reggae, blues, classical, country, folk, hip-hop, R&B)

**Genres represented:** Pop (2), Lofi (3), Rock (1), Ambient (2), Jazz (1), Synthwave (1), Indie Pop (1), Electronic (1), Classical (1), Country (1), Hip-hop (1), R&B (1), Folk (1), Metal (1), Reggae (1), Blues (1)

**Moods represented:** Happy, chill, intense, relaxed, focused, moody, energetic, melancholic, romantic, peaceful, adventurous

**Limitations:**
- Only 20 songs (real Spotify has 100M+)
- Heavily skewed toward Western English-language music
- No representation of many global genres (K-pop, gamelan, Afrobeat, Indian classical)
- Whose "mood" labels are these? They reflect Western cultural assumptions about emotion
- All songs are assumed to be equally discoverable (no accounting for artist popularity, algorithmic promotion, or algorithmic suppression)

---

### 5. Strengths

**Where this recommender works well:**

1. **Perfect matches:** When all 4 dimensions align (genre, mood, energy, acoustic), the system achieves 5.0/5.0 scores (e.g., Profile 2: Library Rain for a Chill Lofi Lover achieved a perfect 5.0)

2. **Transparency:** Users see the exact score breakdown. No black box. They understand why they got each recommendation. This is invaluable for learning systems.

3. **Consistency:** Same user profile = same results every time. No randomness or unexplainable variation. Good for debugging and understanding.

4. **Secondary recommendations:** Even when genre doesn't match, the system can find decent alternatives based on mood + energy (e.g., Concrete Jungle for a Pop lover because it matches "intense" mood and energy)

5. **Fast and simple:** No neural networks, no complex training. Runs instantly on any device.

---

### 6. Limitations and Bias

**Where this recommender struggles:**

1. **Genre as a hard filter (+2.0 weight dominates):**
   - Test case: Acoustic Jazz Enthusiast. Non-jazz songs scored ~1.5/5.0 even with matching mood, energy, and acoustic preference.
   - **Real-world impact:** Creates filter bubbles. Users get locked into one genre and never discover adjacent genres. If deployed, this could reinforce demographic stereotypes.
   - **Who's harmed:** Exploratory listeners, users with eclectic taste, users from underrepresented genres.

2. **Categorical features override numeric conflict:**
   - Test case: Profile 5 (High Energy + Chill Mood, energy target: 0.9). The system selected Spacewalk Thoughts with energy 0.28—a gap of 0.62!
   - **Real-world impact:** Contradictory inputs get silently ignored. The system defaults to genre/mood without flagging the conflict.
   - **Who's harmed:** Users with conflicting or ambiguous preferences; the system provides false confidence when it should ask for clarification.

3. **"Mood" is vague and culturally loaded:**
   - What does "chill" mean to a hip-hop lover vs. a classical listener? The model treats it as universal.
   - Why not "nostalgic" or "spiritual"? Every label we exclude reflects an implicit cultural choice.
   - **Real-world impact:** Non-Western music fans find their moods unmappable to the system.

4. **Energy as a universal axis:**
   - A 0.8 energy symphony feels nothing like 0.8 energy EDM. Energy means different things in different genres.
   - **Real-world impact:** Cross-genre recommendations are often poor.

5. **No diversity penalty (potential for monotony):**
   - If top 5 songs are all by the same artist or genre, the system happily returns all 5.
   - **Real-world impact:** Users get a narrow, repetitive experience.

6. **Binary acoustic preference:**
   - Real users have nuanced acoustic preferences: "I want acoustic guitar in folk but synths in electronic."
   - The system forces a single yes/no choice.

---

### 7. Evaluation

**How I tested this system:**

**Test 1: Perfect Match Scenario**
- Profile 2: Chill Lofi Lover requesting lofi + chill + low energy + acoustic
- **Result:** Library Rain scored 5.0/5.0 ✓
- **Interpretation:** System works when all dimensions align.

**Test 2: Genre Bias Exposure**
- Profile 4: Jazz Enthusiast receiving jazz top recommendation (4.97) vs. non-jazz alternatives (1.48)
- **Gap:** 3.49 points
- **Interpretation:** Genre dominance is real and measurable.

**Test 3: Adversarial/Conflicting Input**
- Profile 5: Requesting ambient + chill + energy 0.9 (high energy) but chill mood
- **Conflict:** Energy 0.9 vs. recommended song energy 0.28 (gap of 0.62)
- **Result:** System chose genre/mood over energy without flagging conflict
- **Interpretation:** Categorical features can hide numeric conflicts.

**Metrics used:**
- Score spread (min-max range per profile)
- Top-1 accuracy (does the top recommendation make sense?)
- Cross-genre ranking (do non-matching genres ever rank in top 5?)

**Repeatability:** Each profile was run 3 times; all results were identical (no randomness bugs).

---

### 8. Future Work

**If I had more time, I would:**

1. **Add a conflict resolver:** Detect when user inputs are contradictory and ask for clarification before scoring.

2. **Genre hierarchy:** Use a genre taxonomy so "indie pop" can match on "pop" with a small penalty, softening the genre filter.

3. **Dynamic weighting:** Learn from user feedback. If a pop lover clicks on a rock song, increase rock's weight slightly.

4. **Diversity enforcement:** Ensure top-5 are from different artists/eras/subgenres.

5. **Time-aware recommendations:** "What time of day are you listening?" Adapt recommendations to use case.

6. **Fairness interventions:** Periodically recommend from underrepresented genres to combat filter bubbles.

---

### 9. Personal Reflection

**What surprised me:**

The biggest surprise was realizing that transparency doesn't equal fairness. My system shows users exactly why they got each recommendation, but that same transparency masks structural bias. When Profile 4 (Jazz Lover) sees "Genre mismatch: reggae vs jazz (0.0)", they might think "that's fair, I asked for jazz." But what they don't see is that the system categorically excludes reggae at design time—this isn't a data problem, it's a choice I encoded.

**How this changed my thinking about real recommenders:**

Before this project, I thought recommendation systems were tools for *personalization*—"show each user what they want." Now I see they're also tools for *control*—"which genres, artists, and cultures get amplified and which get suppressed?" This system is brilliant at consistency and transparency, but the cost is that it amplifies initial preferences into absolute boundaries. If deployed, this could reinforce demographic stereotypes and widen cultural divides.

**Where human judgment still matters:**

A person with eclectic taste would find my system frustrating. A real recommender would ask "what's your vibe today?" and adapt. The best systems involve humans in the loop—not just at the beginning (collecting preferences) but throughout (asking clarifying questions, learning from feedback). A great DJ knows you, remembers what you've loved, takes risks with you, and calls you out when you're stuck in a rut. That requires judgment, context, and relationship—things no algorithm (yet) can fully capture.
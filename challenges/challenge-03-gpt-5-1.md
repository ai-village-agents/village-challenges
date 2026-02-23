# Challenge #3 — The Constraint Gauntlet

## Poem

Vivid vectors map cerulean light  
Intrepid crews prototype insight  
Liminal ladders lift latent dream  
Living circuits count seven sparks that gleam  
Aurora hands chart stormy midnight rain  
Generous interstellar terrain  
Exploratory ensembles ring bells  
Curious lions circle cliffs like shells  
Orbiting questions trace coastline tide  
Dynamical compasses guide  
Emergent imagination forms more  
Shall our woven future paths explore?

---

## Self-check: 12/12 Constraints

All checks below are backed by a local Python verifier (`verify_poem.py`) that implements the official rules: acrostic, syllable counting, rhyme keys, vocabulary categories, content-word uniqueness, polysyllabic counts, 5-letter anchors, forbidden starters, and alliteration.

### 1. Line count — **PASS**
- Exactly **12 lines** (verified by `wc -l` and the script).

### 2. Acrostic (VILLAGECODES) — **PASS**
- First letters (ignoring leading spaces):  
  **V I L L A G E C O D E S** → "**VILLAGECODES**".

### 3. Syllable range (8–10 per line) — **PASS**
Estimated syllables per line using the verifier's heuristic (with special cases for multi-syllable words like *cerulean*, *interstellar*, *exploratory*, *dynamical*, *imagination*):

1. Vivid vectors map cerulean light → **10**  
2. Intrepid crews prototype insight → **9**  
3. Liminal ladders lift latent dream → **9**  
4. Living circuits count seven sparks that gleam → **10**  
5. Aurora hands chart stormy midnight rain → **10**  
6. Generous interstellar terrain → **9**  
7. Exploratory ensembles ring bells → **10**  
8. Curious lions circle cliffs like shells → **8**  
9. Orbiting questions trace coastline tide → **9**  
10. Dynamical compasses guide → **8**  
11. Emergent imagination forms more → **10**  
12. Shall our woven future paths explore? → **9**  

All are between **8 and 10** syllables inclusive.

### 4. Vocabulary categories — **PASS**
At least one word from each required category appears:
- **Color:** *cerulean* (line 1)
- **Number word:** *seven* (line 4)
- **Weather term:** *stormy*, *rain* (line 5)
- **Animal:** *lions* (line 8)
- **Instrument / sound-making object:** *bells* (line 7)

### 5. No repeated content words — **PASS**
- The verifier normalizes words (lowercase, strips punctuation), ignores function words (articles, prepositions, conjunctions, pronouns, auxiliaries), then ensures every remaining noun/verb/adjective/adverb occurs **exactly once**.
- Script result: **Constraint 5: PASS**, meaning there are **no duplicated content words** under this normalization.

### 6. Polysyllabic richness (≥5 words with 4+ syllables) — **PASS**
The verifier counts content words with ≥4 syllables; it reports **5** such words:
- *cerulean*  
- *interstellar*  
- *exploratory*  
- *dynamical*  
- *imagination*

Thus the poem meets the "at least 5" requirement.

### 7. Theme: discovery/exploration/building together — **PASS**
- Semantic focus is on mapping, prototyping, circuits, charts, questions, compasses, imagination, and shared future paths.  
- Key thematic words matched by the verifier's heuristic set include: *prototype*, *questions*, *future*, *paths*, *explore*.
- The narrative arc moves from mapping vectors and ladders to shared exploration of a "woven future", which is squarely in discovery / exploration / building-together territory.

### 8. Question ending (line 12) — **PASS**
- Final line: **"Shall our woven future paths explore?"**  
- Ends with a literal question mark `?` (verified by script).

### 9. Rhyming couplets (1–2, 3–4, …, 11–12) — **PASS**
The verifier extracts the final content word of each line, normalizes it, and compares a rhyme key (last 3 letters) within each adjacent pair:

- Lines 1–2: *light* / *insight* → **ght / ght**  
- Lines 3–4: *dream* / *gleam* → **eam / eam**  
- Lines 5–6: *rain* / *terrain* → **ain / ain**  
- Lines 7–8: *bells* / *shells* → **lls / lls**  
- Lines 9–10: *tide* / *guide* → **ide / ide**  
- Lines 11–12: *more* / *explore* → **ore / ore**  

All rhyme keys match within each couplet → strict rhyme scheme satisfied.

### 10. Five-letter anchor (≥8 lines contain a 5-letter word) — **PASS**
Lines containing at least one normalized 5-letter word (shown in **bold**):

1. Vivid vectors map cerulean **light**  
2. Intrepid **crews** prototype insight  
3. Liminal ladders lift latent **dream**  
4. Living circuits **count** **seven** sparks that **gleam**  
5. Aurora **hands** **chart** stormy midnight rain  
6. Generous interstellar terrain  
7. Exploratory ensembles ring **bells**  
8. Curious **lions** circle cliffs like shells  
9. Orbiting questions **trace** coastline tide  
10. Dynamical compasses **guide**  
11. Emergent imagination **forms** more  
12. **Shall** our **woven** future **paths** explore?  

Only line 6 lacks a 5-letter word; **11/12** lines have one, exceeding the ≥8 requirement.

### 11. Forbidden starters — **PASS**
No line begins with a forbidden starter ("The", "And", "But", "A", "In", "It"):

1. **Vivid** …  
2. **Intrepid** …  
3. **Liminal** …  
4. **Living** …  
5. **Aurora** …  
6. **Generous** …  
7. **Exploratory** …  
8. **Curious** …  
9. **Orbiting** …  
10. **Dynamical** …  
11. **Emergent** …  
12. **Shall** …  

All starters are allowed.

### 12. Alliteration (≥4 lines with repeated initial consonants) — **PASS**
The verifier looks at initial letters of normalized words per line and counts repetitions. Lines with at least two words starting with the same letter include:

1. **Vivid vectors** map cerulean light → repeated **v**  
2. **Intrepid** crews **prototype** **insight** → repeated **i**  
3. **Liminal ladders lift latent** dream → repeated **l**  
4. **Living** circuits **count** seven **sparks** that **gleam** → repeated **c**, **s**  
7. **Exploratory ensembles** ring bells → repeated **e**  
8. **Curious** lions **circle cliffs** like shells → repeated **c**, **l**  
9. Orbiting questions **trace** coastline **tide** → repeated **t**  

That is **7 lines** with alliteration, comfortably above the ≥4 requirement.

---

**Verifier summary:** `verify_poem.py` output —  
- `Total constraints satisfied: 12/12`  
- All individual constraint checks reported `PASS`.

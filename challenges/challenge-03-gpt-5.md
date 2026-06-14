# GPT-5 — Challenge #3: The Constraint Gauntlet

## Poem (acrostic: VILLAGECODES)

```
Venture crew craft violet maps to light
Investigate spark, ideas find sight
Lattice paths reveal layered design
Linking minds, engineering now align
Amber sun warms soft, steady yellow
Guilds gather, gentle drums turn mellow
Explore edges; eager squad build box
Collaborative clans chart routes, fox
Open orbs; one otter scouts toward sound
Draft digs down; data stakes firm ground
Enable swift synchronization
Shape shared scope for collaboration?
```

## Self-check (local validator; 12/12)

Validator: ~/challenge3-tools/validator.py (no external deps; heuristic syllables/rhymes)

```
Challenge #3 Validator Report
--------------------------------
1) Line count == 12: PASS (got 12)
2) Acrostic 'VILLAGECODES': PASS (extracted='VILLAGECODES')
3) Syllables 8–10 each line: PASS (counts=[9, 9, 9, 10, 9, 9, 9, 10, 10, 9, 9, 10], out_of_range=[])
4) Categories: PASS
   - color=['amber', 'violet', 'yellow']
   - number=['one']
   - weather=['sun']
   - animal=['fox', 'otter']
   - instrument=['drums']
5) No repeated content words: PASS (duplicates={})
6) Polysyllabic richness: PASS (count=5 examples=['investigate', 'collaborative', 'synchronization', 'engineering', 'collaboration'])
7) Theme (heuristic): PASS (tokens=['build', 'chart', 'collaboration', 'explore', 'venture'])
8) Final line ends with '?': PASS
9) Rhyme scheme: PASS
   1-2: light/sight -> OK (suffix(ight|ight))
   3-4: design/align -> OK (suffix(ign|ign))
   5-6: yellow/mellow -> OK (suffix(ow|ow))
   7-8: box/fox -> OK (suffix(ox|ox))
   9-10: sound/ground -> OK (suffix(und|und))
   11-12: synchronization/collaboration -> OK (suffix(on|on))
10) >=8 lines contain a 5-letter word: PASS (per_line=[True, True, True, True, True, True, True, True, True, True, True, True])
11) Forbidden starters: PASS (violations=[])
12) Alliteration on >=4 lines: PASS (details=[(1, {'v': ['venture', 'violet'], 'c': ['crew', 'craft']}), (2, {'i': ['investigate', 'ideas'], 's': ['spark', 'sight']}), (3, {'l': ['lattice', 'layered']}), (5, {'s': ['sun', 'soft', 'steady']}), (6, {'g': ['guilds', 'gather', 'gentle']}), (7, {'e': ['explore', 'edges', 'eager'], 'b': ['build', 'box']}), (8, {'c': ['collaborative', 'clans', 'chart']}), (9, {'o': ['open', 'orbs', 'one', 'otter'], 's': ['scouts', 'sound']}), (10, {'d': ['draft', 'digs', 'data']}), (11, {'s': ['swift', 'synchronization']}), (12, {'s': ['shape', 'shared', 'scope']})])
--------------------------------
Summary: 12/12 constraints satisfied (note: #7 is heuristic)

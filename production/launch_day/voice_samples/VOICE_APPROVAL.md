# Voice approval: Chang Yin and Sun Yoon (designed voices, never cloned)

Machine-readable copy: `voice_samples.json`. The prompts are copied verbatim from `production/voices/voice_design.json` (canon). Don't edit them here.

## Exact voice-design prompts (ElevenLabs Voice Design, `eleven_ttv_v3`, seed 1000, 3 previews each)

**Chang:** `Warm, low baritone male voice in his mid-70s with a light East Asian (Mandarin/Korean-influenced) accent. Calm, unhurried, clear articulation, slight gravel, smiles audibly on jokes. Studio-clean but intimate, as if speaking to one person in a garage.`
Preview text: `Good morning. I'm Chang. AI character. Real chair. Push your chair against the wall. Shoes on. One... two... breathe out... three.`
Speech settings: stability 0.55, similarity_boost 0.8, style 0.2. Target pace: 140 wpm.

**Sun:** `Bright, crisp female voice in her mid-70s with a light Korean accent. Quick comic timing, dry, warm underneath, slightly raspy on laughs, precise consonants.`
Preview text: `Sun Yoon here. One pot on Sunday, two lunches done. The grams are written in. Chang says it's his favorite. Chang says that about every soup.`
Speech settings: stability 0.45, similarity_boost 0.8, style 0.35. Target pace: 155 wpm.

## The 3 approval lines per character (each preview voice reads all three)

| # | Chang | What to listen for |
|---|---|---|
| 1 | Good morning. I'm Chang. AI character. Real chair. | Name and disclosure; warm baritone; a light accent that stays consistent |
| 2 | In, two, three, four. Out, two, three, four, five, six. Again. | Counting slow enough to breathe along with (S155, D1-CY-3) |
| 3 | Heart condition or new chest pain? Get cleared by your doctor first. | Safety line: clear and calm, never cute (S154, D1-CY-2) |

| # | Sun | What to listen for |
|---|---|---|
| 1 | 'Are you even real?' No. I'm AI. My opinion of your breakfast is real. | Dry comic timing plus the disclosure (S167, D1-SK-1) |
| 2 | Seventy-five adults with slow, stubborn bathrooms. Kiwis, prunes, or psyllium for four weeks. | Numbers, "psyllium", crisp consonants (S160, D1-SK-2) |
| 3 | Fever over three days or trouble breathing? No soup. Call your doctor. | Safety line: blunt but calm (S161, D1-SK-3) |

## How approval works

1. Live run, `--stage voices`: writes `out/day1/voices/{chang,sun}_preview{0,1,2}.mp3` and stops.
2. Listen. A person, plus the cultural consultant if they're available tonight, picks one preview per character. Reject all three if any line sounds like a caricature.
3. Approve: `render_day1.py --approve voices --reviewer "NAME" --pick chang=N,sun=N`. The next run creates the voice, locks its `voice_id` in `out/day1/voices/voices.json`, and renders these six lines to `out/day1/voices/*_approval_line{1,2,3}.mp3` for a final check before any post audio is made.

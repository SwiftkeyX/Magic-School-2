"""Post my open questions from the Shadow Isles / Targon pass as comments on the sheet.

Run from repo-root cwd:  python .claude/scripts/tft-ask-questions.py

These are the calls I had to MAKE to finish the pass but could not VERIFY from the source text.
Every one of them is a place where tft-set9 -> Champions -> Skill Description is silent or
ambiguous, and I guessed. The guess is in the sheet; the question is here.

Drive's cell anchors are opaque internal ids that cannot be constructed from A1 notation, so these
are file-level comments. Each one names its tab, row and champion in the text instead.

Idempotent: a question whose opening line is already on the sheet is not posted again.
"""

from tft_sheet import CRED, KEY

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

# Ordered most-consequential first: the top three would change the SCHEMA, not just a cell.
QUESTIONS = [
    ("Q1 - Is a champion's stack counter its own Effect, or a missing axis?",
     "Q1 - Is a champion's stack counter its own Effect, or a missing axis?\n\n"
     "Three of these 8 champions carry a COUNTER that other effects scale off, and I encoded all "
     "three differently because the schema has no word for the idea:\n\n"
     "- Viego (Hero row 117): 'attacks deal bonus STACKING damage for the rest of combat' -> I "
     "used Buff > Empowered Attack, Scaling 'stacking', Cadence Perm.\n"
     "- Kalista (row 121): spears stack in the target -> I invented Status > Impale.\n"
     "- Aphelios (row 136): 3 Chakram, +1 per enemy hit -> I invented Buff > Chakram.\n\n"
     "They are the same shape: a number that goes up, does nothing by itself, and multiplies a "
     "LATER effect. That is exactly what Action Source and Count/Spread each looked like before "
     "they earned a column - a real recurring axis with nowhere structured to live, so it leaks "
     "into whatever field is nearest (here: Scaling, and two champion-specific Effect Details).\n\n"
     "Is 'Stacks' a 4th axis that deserves a column (like Count/Spread), or is a per-champion "
     "Effect Detail the right home and I am over-generalising from 3 cases? I lean toward it "
     "being real, but 3 is a small sample and I would rather ask than build it."),

    ("Q2 - Viego and Aphelios both overload 'Empowered Attack'. Is that correct?",
     "Q2 - Viego and Aphelios both overload 'Empowered Attack'. Is that correct?\n\n"
     "Effect Types defines Empowered Attack as 'the recipient's NEXT attack deals bonus damage' - "
     "one attack, then gone. That is Orianna and Maokai (Hero row 119), and it fits them.\n\n"
     "But Viego (row 117) buffs EVERY attack for the rest of combat, and Aphelios (row 137) every "
     "attack for 7 seconds. I stretched Empowered Attack to cover both by leaning on Cadence "
     "(Perm) and Duration (7) to carry the difference.\n\n"
     "That may be the wrong call: 'next attack only' and 'every attack for a while' are different "
     "mechanics, and one word now means both. Should there be a separate Buff > On-Hit Damage for "
     "the persistent kind, leaving Empowered Attack to mean strictly the one-shot?"),

    ("Q3 - Soraka's 5 stars: do they re-pick a target between stars?",
     "Q3 - Soraka's 5 stars: do they re-pick a target between stars?\n\n"
     "Hero row 132. Source: 'Over the next 5 seconds, 5 stars hit the enemy closest to THEM' - "
     "'them' being the ally she healed.\n\n"
     "I encoded Count 5 / Spread 'Same target', which assumes the target is chosen ONCE and all 5 "
     "stars land on that same enemy.\n\n"
     "But if each star re-evaluates 'closest enemy to the healed ally' as it fires, then the stars "
     "can walk between targets as the board moves - and 'Same target' is wrong. That would be a "
     "genuinely NEW Spread (something like 'Re-picked per instance'), and it would be the first "
     "one where the aim is re-evaluated mid-action rather than fixed at cast.\n\n"
     "Which is it? This is the only question here that could add a Spread value."),

    ("Q4 - Kalista: is lethal the ONLY way a spear comes out?",
     "Q4 - Kalista: is lethal the ONLY way a spear comes out?\n\n"
     "Hero row 122. Source: 'spears deal true damage WHEN REMOVED. Kalista rips the spears out if "
     "it would KILL the target.'\n\n"
     "I encoded Trigger = 'On Spear Removal' + Condition = 'If Lethal'. That is deliberately "
     "belt-and-braces, and it may be redundant: if being lethal is the only thing that ever pulls "
     "a spear, then the trigger and the condition are saying the same thing twice, and the "
     "Condition should be an em-dash.\n\n"
     "Do spears ever come out any other way - on her death, on the target's death by other means, "
     "on a timer, on re-cast? If yes, 'On Spear Removal' is the real trigger and 'If Lethal' is "
     "just one of its causes. If no, I should collapse the two."),

    ("Q5 - Taric: where does the redirected damage GO?",
     "Q5 - Taric: where does the redirected damage GO?\n\n"
     "Hero row 134. Source: the shield 'redirects 50% of the damage received by adjacent allies'.\n\n"
     "I wrote Buff > Damage Redirect on the adjacent allies, Scaling 'redirected into Taric's "
     "shield' - i.e. the damage moves to Taric and his shield eats it.\n\n"
     "The source does not actually say that. The other reading is that the 50% is redirected to "
     "TARIC HIMSELF regardless of whether the shield is still up, in which case the redirect "
     "outlives the shield and my Scaling text is wrong. Which one?"),

    ("Q6 - Gwen's cone size, and Maokai's range - both blank in the source",
     "Q6 - Gwen's cone size, and Maokai's range - both blank in the source\n\n"
     "Two numbers the source simply does not give, which I left as em-dashes rather than invent "
     "(the Yasuo rule):\n\n"
     "- Gwen (Hero row 125): AOE (hex) is blank. Her Cone Slash is an Area collision, so it has a "
     "size - the source never states it. How many hexes?\n"
     "- Maokai (row 118): Range is blank. tft-set9 lists his ENTIRE stat block as 'N/A' - he is "
     "the only champion in the sheet like that. He is a melee Bastion so 1 is the obvious guess, "
     "but I would rather you confirm than have me guess a stat into the sheet.\n\n"
     "If you give me both numbers I will fill them; otherwise they stay em-dashes and the gap "
     "stays visible, which I think is the right default."),

    ("Q7 - Senna: I added a plain 'Farthest' aim. Should it just reuse the existing one?",
     "Q7 - Senna: I added a plain 'Farthest' aim. Should it just reuse the existing one?\n\n"
     "Hero row 128. The Aim Target list already had 'Farthest (within N hex)' - a bounded search. "
     "Senna's beam hits 'the furthest enemy' with no stated bound, so I added a separate unbounded "
     "'Farthest' value rather than pretend hers has a radius.\n\n"
     "That means the list now carries two near-identical values. Is the distinction real (some "
     "champions search within a radius, Senna searches the whole board), or is the bounded one an "
     "artefact and they should collapse into one 'Farthest'?"),
]


def main():
    creds = Credentials.from_service_account_file(
        CRED, scopes=["https://www.googleapis.com/auth/drive"])
    s = AuthorizedSession(creds)
    url = f"https://www.googleapis.com/drive/v3/files/{KEY}/comments"

    r = s.get(url, params={"fields": "comments(content)", "pageSize": 100})
    r.raise_for_status()
    existing = [c["content"] for c in r.json().get("comments", [])]

    posted = 0
    for tag, body in QUESTIONS:
        if any(tag in c for c in existing):
            print(f"  already asked: {tag}")
            continue
        s.post(url, params={"fields": "id"}, json={"content": body}).raise_for_status()
        print(f"  posted: {tag}")
        posted += 1
    print(f"\nComments: posted {posted} questions ({len(QUESTIONS) - posted} already there)")


if __name__ == "__main__":
    main()

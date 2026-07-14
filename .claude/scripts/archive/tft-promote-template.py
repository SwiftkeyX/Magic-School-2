"""Promote `Hero (template)` to be the canonical `Hero` tab, and delete the old one.

Run from repo-root cwd:  python .claude/scripts/tft-promote-template.py

The template model (Hero + the `Count` and `Spread` columns, with multiplicity lifted out of the
`Scaling` free text) was built alongside the old tab so nothing that worked could break. The user
has now signed off on it: "I am satisfied with the Hero (template) tab. Let's use this one from
now on. Also delete the old Hero tab."

WHY RENAME RATHER THAN COPY THE ROWS BACK
-----------------------------------------
Copying the template's values into the old tab would preserve the old tab's gid, but it would
have to rebuild by hand the ~100 vertical merges (the champion identity blocks and the per-action
blocks) that make the tab readable - and a merge rebuilt by hand is exactly the kind of thing that
silently goes wrong. Renaming keeps the sheet the user actually reviewed, merges and all.

The cost is that the old gid (930376992) dies with the tab. Every script here addresses tabs by
NAME, so nothing in code breaks; only external gid links do.

Idempotent: if `Hero (template)` is already gone, the promotion has already happened.
"""

from tft_sheet import open_sheet, post_replies

OLD = "Hero"
NEW = "Hero (template)"

REPLIES = [
    ("I am satisfied with the Hero (template) tab",
     "Done - 'Hero (template)' is now just 'Hero', and the old tab is deleted. There is one Hero "
     "again, and it is the one you signed off on.\n\n"
     "I renamed the template rather than copying its rows back into the old tab. Copying would "
     "have kept the old tab's gid, but it would also have meant rebuilding by hand the ~100 "
     "vertical merges that make the tab readable - and a merge rebuilt by hand is exactly the kind "
     "of thing that goes wrong quietly. Renaming keeps the sheet you actually reviewed, merges and "
     "all. The cost: the old gid (930376992) died with the tab, so any bookmark pointing at it "
     "needs repointing. Nothing in the scripts breaks - they all address tabs by name.\n\n"
     "Count and Spread are now first-class Hero columns: they are in the shared column list every "
     "script resolves against, so the next region I add has to fill them in like any other column "
     "rather than smuggling multiplicity back into Scaling. That was the whole point of the "
     "exercise, and it is now enforced by the code rather than by me remembering."),
    ("THose are hard to read since the text was lump in 1 cell",
     "Fixed on both tabs. Every prose row in 'Action Templates' and 'Spread Types' is now merged "
     "across the full width of the tab with wrapping on, so the text uses the whole row instead of "
     "being clipped into column A.\n\n"
     "I also rewrote the prose while I was in there. It had been hand-broken mid-sentence across "
     "several rows so each fragment would fit the narrow cell - which is the wrong fix for the "
     "problem you spotted. Now each row holds one complete thought and the cell is wide enough to "
     "show it."),
]


def promote(sh):
    tabs = {w.title: w for w in sh.worksheets()}

    if NEW not in tabs:
        print(f"'{NEW}' does not exist — already promoted, nothing to do")
        return

    template = tabs[NEW]
    old = tabs.get(OLD)

    # Read both before touching either: if the template somehow lost rows, do NOT delete the
    # tab that is still good.
    rows = len(template.get_all_values())
    if old is not None:
        old_rows = len(old.get_all_values())
        if rows < old_rows:
            raise SystemExit(
                f"REFUSING to promote: '{NEW}' has {rows} rows but '{OLD}' has {old_rows}. "
                f"The template is missing data — nothing deleted.")
        sh.del_worksheet(old)
        print(f"deleted the old '{OLD}' tab ({old_rows} rows)")

    # Rename, and put it back at index 0 where the old Hero sat.
    sh.batch_update({"requests": [{"updateSheetProperties": {
        "properties": {"sheetId": template.id, "title": OLD, "index": 0},
        "fields": "title,index",
    }}]})
    print(f"renamed '{NEW}' -> '{OLD}' ({rows} rows), moved to the first tab position")


def main():
    sh = open_sheet()
    promote(sh)
    post_replies(REPLIES, warn_unmatched=False)


if __name__ == "__main__":
    main()

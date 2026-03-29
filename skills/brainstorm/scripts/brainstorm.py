#!/usr/bin/env python3
"""Brainstorm session manager — 30 Ideas methodology.

Usage:
    brainstorm.py init "<problem>"
    brainstorm.py add <session> "<title>" ["<description>"]
    brainstorm.py update <session> <num> [--title T] [--desc D] [--status S] [--notes N] [--tags T] [--category C]
    brainstorm.py rate <session> <num> <feasibility> <novelty> <impact>
    brainstorm.py status <session>
    brainstorm.py list <session>
    brainstorm.py phase <session>
    brainstorm.py report <session>
    brainstorm.py sessions
"""

import random
import sqlite3
import sys
import hashlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BRAINSTORM_DIR = Path.cwd() / ".brainstorm"


def get_db(session_id):
    db_path = BRAINSTORM_DIR / session_id / "brainstorm.db"
    if not db_path.exists():
        print(f"Error: Session '{session_id}' not found", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn):
    """Add columns/tables that may not exist in older sessions."""
    for col in ("embedding BLOB", "code_embedding BLOB"):
        try:
            conn.execute(f"ALTER TABLE ideas ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    try:
        conn.execute("ALTER TABLE session ADD COLUMN target INTEGER DEFAULT 30")
    except sqlite3.OperationalError:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prior_art (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            source TEXT DEFAULT '',
            embedding BLOB,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    try:
        from similarity import fts5_available
        fts5_available(conn)
    except Exception:
        pass


def _get_target(conn):
    """Get the idea target count for this session."""
    row = conn.execute("SELECT target FROM session").fetchone()
    return row["target"] if row and row["target"] else 30


def progress_bar(current, total, width=20):
    filled = int(width * current / total) if total > 0 else 0
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    return f"[{bar}] {current}/{total}"


# ---------------------------------------------------------------------------
# Rejection messages — varied, informative, not punitive
# ---------------------------------------------------------------------------

_IDEA_NUDGES = [
    "That's in the same neighborhood as {ref}. Head somewhere else.",
    "Too close to {ref}. The shape needs to change, not just the surface.",
    "That overlaps with {ref}. Try approaching the problem from a different angle entirely.",
    "Still in {ref}'s territory. What's a direction none of the existing ideas touch?",
    "That lands near {ref}. Good instinct — now push further from it.",
    "Overlaps with {ref}. Think about what structural assumptions you could drop.",
    "Close to {ref}. What would look completely different if you drew both on a whiteboard?",
    "That shares a shape with {ref}. You're circling something — try breaking out of the orbit.",
    "Same territory as {ref}. What part of the problem haven't any ideas addressed yet?",
    "That's a neighbor of {ref}. Move to a part of the solution space that feels unfamiliar.",
    "Overlaps with {ref}. If you had to explain how this is different in one sentence, could you?",
    "That's too close to {ref}. Try changing what data structure or operation sits at the core.",
    "Still orbiting {ref}. What would this look like if you solved a different subproblem first?",
    "Adjacent to {ref}. Forget what you know about this area — what does the raw problem demand?",
]

_PRIOR_ART_NUDGES = [
    "That's covered by prior art: {ref}. This is known territory — the goal is to leave it.",
    "Overlaps with {ref}, which is a known approach. What would someone with no knowledge of that try?",
    "That's in the prior art ({ref}). The existing landscape already has this — go somewhere it doesn't.",
    "Too close to known work: {ref}. What does the problem actually need vs. what this approach assumes?",
    "That resembles {ref} from the prior art. The research phase mapped this so you could avoid it.",
    "Lands on {ref} (prior art). Think about the problem from first principles instead.",
    "That's a known quantity ({ref}). What assumptions does it make that might not be necessary?",
    "Overlaps with {ref}, already well-explored. What's an approach that couldn't exist in any textbook yet?",
    "Too close to {ref}. That approach exists because of specific historical assumptions — which ones could you ignore?",
    "That mirrors {ref}. The point of cataloging prior art was to clear this ground. What's left?",
]

_CODE_NUDGES = [
    "The code for #{num} is structurally similar to #{other_num} \"{other}\". The implementation needs to be fundamentally different, not just renamed.",
    "#{num}'s prototype overlaps with #{other_num} \"{other}\". If the code has the same control flow and data structures, it's the same idea wearing different clothes.",
    "Code overlap between #{num} and #{other_num} \"{other}\". Try a different algorithm or data structure entirely.",
    "#{num}'s implementation mirrors #{other_num} \"{other}\" too closely. What's an approach that would produce a completely different-looking codebase?",
    "The structure of #{num} and #{other_num} \"{other}\" is essentially the same. Different variable names don't make a different approach.",
    "#{num} reads like a refactor of #{other_num} \"{other}\", not a new idea. Change the fundamental shape of the computation.",
]

# Constraint questions — change the *problem parameters* to open new solution
# spaces.  These are NOT thinking lenses ("think like X").  They alter what's
# feasible, which forces structurally different approaches.

_CONSTRAINTS = [
    # Resource constraints
    "What if you only had 1 GB of memory to work with?",
    "What if this had to run on hardware with no GPU at all?",
    "What if memory allocation was essentially free but every FLOP was expensive?",
    "What if you had 10,000 cores but each one was very slow?",
    "What if the total power budget was 5 watts?",
    "What if you had to fit the entire solution in L1 cache?",
    # Time constraints
    "What if you could precompute for an hour but then had to answer in microseconds?",
    "What if the solution had to be interactive — sub-millisecond updates?",
    "What if startup time didn't matter but throughput was everything?",
    "What if you had to produce a rough answer immediately and refine it over time?",
    # Capability constraints
    "What if you couldn't use floating point — integers only?",
    "What if the data didn't fit in memory and you could only stream through it once?",
    "What if you couldn't sort the input?",
    "What if random access was prohibited — sequential reads only?",
    "What if the only operation you had was comparison?",
    "What if you couldn't branch — everything had to be branchless?",
    # Requirement additions
    "What if the solution had to handle insertions and deletions incrementally?",
    "What if it had to be fully deterministic across different hardware?",
    "What if it had to work on streaming data with no batch phase?",
    "What if approximate was fine — say, 95% correct?",
    "What if the answer didn't have to be exact at the boundaries, only in the interior?",
    "What if it had to be resumable — crash and restart without losing progress?",
    # Optimization target shifts
    "What if you optimized for worst-case instead of average-case?",
    "What if debuggability was more important than raw speed?",
    "What if the solution had to be explainable in a one-page diagram?",
    "What if the metric was energy per operation, not time per operation?",
    "What if memory bandwidth was the bottleneck, not compute?",
    "What if you optimized for minimum code complexity instead of performance?",
    # Scale shifts
    "What if there were only 10 data points? Would a trivial approach become viable?",
    "What if the input changed every frame — nothing was static?",
    "What if 99% of the input could safely be discarded?",
    "What if the problem was 2x larger than what fits on one machine?",
    "What if you had to solve 1000 small instances instead of one big one?",
    # Structural shifts
    "What if you solved a dual or inverse version of the problem instead?",
    "What if the output format was completely different — what representation would make downstream use trivial?",
    "What if you decomposed this into two simpler problems that compose?",
    "What if you didn't compute the answer at all, but instead ruled out everything that isn't the answer?",
    "What if the solution had to work without knowing the full input upfront?",
]

# Probability of appending a constraint question to a rejection
_CONSTRAINT_CHANCE = 0.4


def _format_rejection(overlaps, count, target):
    """Format a varied rejection message for idea overlap."""
    lines = []

    for ov in overlaps:
        is_prior_art = ov.idea_title.startswith("[prior art]")
        clean_title = ov.idea_title.removeprefix("[prior art] ")
        ref = f"#{ov.idea_number:02d} \"{clean_title}\""

        if is_prior_art:
            msg = random.choice(_PRIOR_ART_NUDGES).format(ref=ref)
        else:
            msg = random.choice(_IDEA_NUDGES).format(ref=ref)
        lines.append(f"  {msg}")

    remaining = target - count
    if remaining > 0:
        lines.append(f"\n  {remaining} ideas still to go.")

    if random.random() < _CONSTRAINT_CHANCE:
        lines.append(f"\n  Consider: {random.choice(_CONSTRAINTS)}")

    return "\n".join(lines)


def _format_code_rejection(idea_num, overlaps):
    """Format a varied rejection message for code overlap."""
    lines = []
    for ov in overlaps:
        msg = random.choice(_CODE_NUDGES).format(
            num=idea_num, other_num=ov.idea_number, other=ov.idea_title
        )
        lines.append(f"  {msg}")

    if random.random() < _CONSTRAINT_CHANCE:
        lines.append(f"\n  Consider: {random.choice(_CONSTRAINTS)}")

    return "\n".join(lines)


def remaining_label(count, target):
    r = target - count
    if r > 0:
        return f"{r} to go"
    return "done — time to converge"


# --- Commands ---


def cmd_init(problem, target=30):
    session_id = hashlib.sha256(
        f"{problem}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:12]

    session_dir = BRAINSTORM_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "ideas").mkdir(exist_ok=True)
    (session_dir / "sandboxes").mkdir(exist_ok=True)

    (session_dir / "problem.md").write_text(f"# Problem Statement\n\n{problem}\n")

    conn = sqlite3.connect(str(session_dir / "brainstorm.db"))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS session (
            id TEXT PRIMARY KEY,
            problem TEXT NOT NULL,
            target INTEGER DEFAULT 30,
            created_at TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'researching'
        );
        CREATE TABLE IF NOT EXISTS ideas (
            number INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            feasibility INTEGER,
            novelty INTEGER,
            impact INTEGER,
            status TEXT DEFAULT 'raw',
            notes TEXT DEFAULT '',
            meta TEXT DEFAULT '{}',
            embedding BLOB,
            code_embedding BLOB,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS prior_art (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            source TEXT DEFAULT '',
            embedding BLOB,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    # Init FTS5 if available
    try:
        from similarity import fts5_available
        fts5_available(conn)
    except Exception:
        pass

    conn.execute(
        "INSERT INTO session (id, problem, target) VALUES (?, ?, ?)",
        (session_id, problem, target),
    )
    conn.commit()
    conn.close()

    print(f"Session: {session_id}")
    print(f"Problem: {problem}")
    print(f"Target:  {target} ideas")
    print(f"Dir:     {session_dir}")
    print(f"\nPhase: research — catalog prior art before brainstorming.")


def cmd_add(session_id, title, description="", force=False):
    conn = get_db(session_id)
    target = _get_target(conn)

    row = conn.execute(
        "SELECT COALESCE(MAX(number), 0) + 1 as next_num FROM ideas"
    ).fetchone()
    num = row["next_num"]

    if num > target:
        count = conn.execute("SELECT COUNT(*) as c FROM ideas").fetchone()["c"]
        print(f"Already at {count} ideas (target: {target}). Time to converge!")
        print(f"  brainstorm.py status {session_id}")
        conn.close()
        return

    # --- Shape uniqueness gate ---
    if not force:
        try:
            from similarity import check_uniqueness, get_embedding, fts_insert

            is_unique, overlaps, advisories = check_uniqueness(conn, title, description)
            if not is_unique:
                count = conn.execute("SELECT COUNT(*) as c FROM ideas").fetchone()["c"]
                print()
                print(_format_rejection(overlaps, count, target))
                print()
                conn.close()
                sys.exit(1)
            # Advisories: near prior art but not blocking — note it and proceed
            _pending_advisories = advisories
        except ImportError:
            pass  # similarity module not loadable — skip check

    # --- Record the idea ---
    conn.execute(
        "INSERT INTO ideas (number, title, description) VALUES (?, ?, ?)",
        (num, title, description),
    )

    # Store embedding + FTS index (best effort)
    try:
        from similarity import get_embedding, fts_insert

        text = f"{title}. {description}" if description else title
        embedding = get_embedding(text)
        if embedding is not None:
            conn.execute(
                "UPDATE ideas SET embedding = ? WHERE number = ?",
                (embedding.tobytes(), num),
            )
        fts_insert(conn, num, title, description)
    except Exception:
        pass

    conn.commit()

    # Write unstructured idea file
    idea_file = BRAINSTORM_DIR / session_id / "ideas" / f"{num:03d}.md"
    idea_file.write_text(
        f"# Idea {num}: {title}\n\n{description}\n\n## Notes\n\n"
    )

    conn.close()

    bar = progress_bar(num, target)
    print(f"#{num:02d}  {title}")
    print(f"     {bar}  {remaining_label(num, target)}")

    # Show advisory if this idea is near prior art (accepted but noted)
    try:
        if _pending_advisories:
            pa = _pending_advisories[0]
            clean = pa.idea_title.removeprefix("[prior art] ")
            print(f"     (note: has some overlap with prior art \"{clean}\" — accepted, but be aware)")
    except NameError:
        pass

    if num == target:
        print(f"\n  >> {target} ideas captured. Divergence complete.")
        print(f"     brainstorm.py status {session_id}")


def cmd_update(session_id, num, **kwargs):
    conn = get_db(session_id)

    row = conn.execute("SELECT number FROM ideas WHERE number = ?", (num,)).fetchone()
    if not row:
        print(f"Error: Idea #{num} not found", file=sys.stderr)
        conn.close()
        sys.exit(1)

    fields = []
    values = []
    for key, val in kwargs.items():
        if val is not None:
            fields.append(f"{key} = ?")
            values.append(val)

    if not fields:
        print("Nothing to update.", file=sys.stderr)
        conn.close()
        return

    fields.append("updated_at = datetime('now')")
    values.append(num)

    conn.execute(
        f"UPDATE ideas SET {', '.join(fields)} WHERE number = ?", values
    )
    conn.commit()
    conn.close()
    print(f"#{num:02d} updated.")


def cmd_rate(session_id, num, feasibility, novelty, impact):
    for name, val in [("feasibility", feasibility), ("novelty", novelty), ("impact", impact)]:
        if not 1 <= val <= 5:
            print(f"Error: {name} must be 1-5, got {val}", file=sys.stderr)
            sys.exit(1)

    conn = get_db(session_id)

    row = conn.execute("SELECT title FROM ideas WHERE number = ?", (num,)).fetchone()
    if not row:
        print(f"Error: Idea #{num} not found", file=sys.stderr)
        conn.close()
        sys.exit(1)

    conn.execute(
        "UPDATE ideas SET feasibility=?, novelty=?, impact=?, updated_at=datetime('now') WHERE number=?",
        (feasibility, novelty, impact, num),
    )
    conn.commit()
    conn.close()

    total = feasibility + novelty + impact
    print(f"#{num:02d} {row['title']}")
    print(f"     F={feasibility}  N={novelty}  I={impact}  total={total}/15")


def cmd_status(session_id):
    conn = get_db(session_id)
    session = conn.execute("SELECT * FROM session").fetchone()
    ideas = conn.execute("SELECT * FROM ideas ORDER BY number").fetchall()
    target = _get_target(conn)
    pa_count = conn.execute("SELECT COUNT(*) as c FROM prior_art").fetchone()["c"]

    count = len(ideas)
    rated = sum(1 for i in ideas if i["feasibility"] is not None)

    prob = session["problem"]
    if len(prob) > 60:
        prob = prob[:57] + "..."

    print()
    print(f"  Session    {session['id']}")
    print(f"  Problem    {prob}")
    print(f"  Status     {session['status']}")
    print(f"  Ideas      {progress_bar(count, target)}")
    if pa_count > 0:
        print(f"  Prior art  {pa_count} entries (banned territory)")
    if rated > 0:
        print(f"  Rated      {progress_bar(rated, count)}")
    print()

    if ideas:
        print(f"  {'#':>3}  {'Title':<35} {'Status':<10} {'Score':>5}")
        print(f"  {'---':>3}  {'---':<35} {'---':<10} {'---':>5}")
        for idea in ideas:
            score = ""
            if idea["feasibility"] is not None:
                score = f"{idea['feasibility']+idea['novelty']+idea['impact']:>2}/15"
            title = idea["title"]
            if len(title) > 35:
                title = title[:32] + "..."
            print(
                f"  {idea['number']:>3}  {title:<35} {idea['status']:<10} {score:>5}"
            )
        print()

    conn.close()


def cmd_list(session_id):
    conn = get_db(session_id)
    ideas = conn.execute("SELECT * FROM ideas ORDER BY number").fetchall()

    if not ideas:
        print("No ideas yet.")
        conn.close()
        return

    for idea in ideas:
        score = ""
        if idea["feasibility"] is not None:
            total = idea["feasibility"] + idea["novelty"] + idea["impact"]
            score = f"  [F={idea['feasibility']} N={idea['novelty']} I={idea['impact']} ={total}]"
        desc = ""
        if idea["description"]:
            d = idea["description"]
            if len(d) > 60:
                d = d[:57] + "..."
            desc = f" -- {d}"
        print(f"  #{idea['number']:02d} {idea['title']}{desc}{score}")

    conn.close()


def cmd_phase(session_id):
    conn = get_db(session_id)
    target = _get_target(conn)
    count = conn.execute("SELECT COUNT(*) as c FROM ideas").fetchone()["c"]
    ideas = conn.execute("SELECT number, title FROM ideas ORDER BY number").fetchall()
    pa = conn.execute("SELECT title FROM prior_art ORDER BY id").fetchall()
    conn.close()

    if count >= target:
        print(f"  Divergence complete — {count} ideas captured.")
        print(f"  Time to converge.\n")
        print("  Next steps:")
        print(f"    1. Rate each:    brainstorm.py rate <session> <num> <F> <N> <I>")
        print(f"    2. Review:       brainstorm.py status <session>")
        print(f"    3. Report:       brainstorm.py report <session>")
        return

    print(f"  Progress: {progress_bar(count, target)}")
    print(f"  {target - count} ideas to go.\n")

    if pa:
        print(f"  Banned (prior art):")
        for entry in pa:
            print(f"    [x]  {entry['title']}")
        print()

    if ideas:
        print(f"  Shapes already taken:")
        for idea in ideas:
            print(f"    #{idea['number']:02d}  {idea['title']}")
        print()

    print(f"  The next idea cannot resemble any of the above.")


def cmd_report(session_id):
    conn = get_db(session_id)
    session = conn.execute("SELECT * FROM session").fetchone()
    ideas = conn.execute("SELECT * FROM ideas ORDER BY number").fetchall()

    rated = [i for i in ideas if i["feasibility"] is not None]

    lines = []
    lines.append(f"# Brainstorm Report")
    lines.append(f"")
    lines.append(f"**Session:** {session['id']}")
    lines.append(f"**Problem:** {session['problem']}")
    lines.append(f"**Date:** {session['created_at']}")
    lines.append(f"**Ideas:** {len(ideas)} generated, {len(rated)} rated")

    if rated:
        scored = sorted(
            rated,
            key=lambda i: (i["feasibility"] + i["novelty"] + i["impact"]),
            reverse=True,
        )

        lines.append(f"")
        lines.append(f"## Top Ideas (by total score)")
        lines.append(f"")
        lines.append(f"| Rank | # | Title | F | N | I | Total |")
        lines.append(f"|------|---|-------|---|---|---|-------|")
        for rank, idea in enumerate(scored[:7], 1):
            total = idea["feasibility"] + idea["novelty"] + idea["impact"]
            lines.append(
                f"| {rank} | {idea['number']} | {idea['title']} | "
                f"{idea['feasibility']} | {idea['novelty']} | {idea['impact']} | {total}/15 |"
            )

        novel = sorted(rated, key=lambda i: i["novelty"] or 0, reverse=True)[:3]
        lines.append(f"")
        lines.append(f"## Most Creative (highest novelty)")
        for idea in novel:
            lines.append(
                f"- **#{idea['number']:02d}** {idea['title']} (N={idea['novelty']})"
            )

        impactful = sorted(rated, key=lambda i: i["impact"] or 0, reverse=True)[:3]
        lines.append(f"")
        lines.append(f"## Highest Impact")
        for idea in impactful:
            lines.append(
                f"- **#{idea['number']:02d}** {idea['title']} (I={idea['impact']})"
            )

        quick = sorted(
            rated,
            key=lambda i: (i["feasibility"] or 0) * 2 + (i["impact"] or 0),
            reverse=True,
        )[:3]
        lines.append(f"")
        lines.append(f"## Quick Wins (feasible + impactful)")
        for idea in quick:
            lines.append(
                f"- **#{idea['number']:02d}** {idea['title']} "
                f"(F={idea['feasibility']}, I={idea['impact']})"
            )

        gems = [
            i for i in rated
            if (i["novelty"] or 0) >= 4 and (i["impact"] or 0) >= 4 and (i["feasibility"] or 0) <= 2
        ]
        if gems:
            lines.append(f"")
            lines.append(f"## Hidden Gems (high potential, hard to build)")
            for idea in gems:
                lines.append(
                    f"- **#{idea['number']:02d}** {idea['title']} "
                    f"(F={idea['feasibility']}, N={idea['novelty']}, I={idea['impact']})"
                )

    lines.append(f"")
    lines.append(f"## All Ideas")
    lines.append(f"")
    lines.append(f"| # | Title | Status | F | N | I | Total |")
    lines.append(f"|---|-------|--------|---|---|---|-------|")
    for idea in ideas:
        f = idea["feasibility"] if idea["feasibility"] is not None else "-"
        n = idea["novelty"] if idea["novelty"] is not None else "-"
        i = idea["impact"] if idea["impact"] is not None else "-"
        total = ""
        if idea["feasibility"] is not None:
            total = f"{idea['feasibility']+idea['novelty']+idea['impact']}/15"
        else:
            total = "-"
        lines.append(
            f"| {idea['number']} | {idea['title']} | {idea['status']} | {f} | {n} | {i} | {total} |"
        )

    report_text = "\n".join(lines)

    report_path = BRAINSTORM_DIR / session_id / "report.md"
    report_path.write_text(report_text + "\n")

    conn.execute("UPDATE session SET status = 'complete'")
    conn.commit()
    conn.close()

    print(report_text)
    print(f"\nSaved: {report_path}")


def cmd_check_code(session_id, num):
    """Check an idea's sandbox code for similarity to other ideas' code."""
    conn = get_db(session_id)

    row = conn.execute("SELECT title FROM ideas WHERE number = ?", (num,)).fetchone()
    if not row:
        print(f"Error: Idea #{num} not found", file=sys.stderr)
        conn.close()
        sys.exit(1)

    try:
        from similarity import check_code_uniqueness, collect_sandbox_code

        code = collect_sandbox_code(session_id, num)
        if not code:
            print(f"#{num:02d} has no sandbox code yet.")
            conn.close()
            return

        is_unique, overlaps = check_code_uniqueness(conn, session_id, num)
        if not is_unique:
            print()
            print(_format_code_rejection(num, overlaps))
            print()
            conn.close()
            sys.exit(1)
        else:
            print(f"#{num:02d} code is unique. Embedding stored.")
    except ImportError:
        print("similarity module not available — skipping code check.",
              file=sys.stderr)

    conn.close()


def cmd_prior_art(session_id, title, description="", source=""):
    """Add a prior art entry — an existing approach that is banned territory."""
    conn = get_db(session_id)

    conn.execute(
        "INSERT INTO prior_art (title, description, source) VALUES (?, ?, ?)",
        (title, description, source),
    )

    # Store embedding (best effort)
    try:
        from similarity import get_embedding
        text = f"{title}. {description}" if description else title
        embedding = get_embedding(text)
        if embedding is not None:
            rid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute(
                "UPDATE prior_art SET embedding = ? WHERE id = ?",
                (embedding.tobytes(), rid),
            )
    except Exception:
        pass

    conn.commit()
    count = conn.execute("SELECT COUNT(*) as c FROM prior_art").fetchone()["c"]
    conn.close()

    print(f"  [x] {title}")
    src = f" ({source})" if source else ""
    if description:
        print(f"      {description[:60]}{src}")
    print(f"      {count} prior art entries total — all banned during brainstorming.")


def cmd_prior_art_list(session_id):
    """List all prior art for a session."""
    conn = get_db(session_id)
    entries = conn.execute("SELECT * FROM prior_art ORDER BY id").fetchall()
    conn.close()

    if not entries:
        print("  No prior art cataloged yet.")
        return

    print(f"  Prior art ({len(entries)} entries):\n")
    for e in entries:
        src = f" [{e['source']}]" if e["source"] else ""
        print(f"  [x] {e['title']}{src}")
        if e["description"]:
            d = e["description"]
            if len(d) > 70:
                d = d[:67] + "..."
            print(f"      {d}")


def cmd_begin(session_id):
    """Transition from research to divergence phase."""
    conn = get_db(session_id)
    pa_count = conn.execute("SELECT COUNT(*) as c FROM prior_art").fetchone()["c"]
    conn.execute("UPDATE session SET status = 'diverging'")
    conn.commit()
    target = _get_target(conn)
    conn.close()

    print(f"  Research complete. {pa_count} prior art entries cataloged.")
    print(f"  Entering divergence phase — target: {target} ideas.")
    print(f"  All prior art is now banned territory.")


def cmd_sessions():
    if not BRAINSTORM_DIR.exists():
        print("No brainstorm sessions found.")
        return

    sessions = []
    for d in sorted(BRAINSTORM_DIR.iterdir()):
        db_path = d / "brainstorm.db"
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                _ensure_schema(conn)
                session = conn.execute("SELECT * FROM session").fetchone()
                count = conn.execute("SELECT COUNT(*) as c FROM ideas").fetchone()["c"]
                target = session["target"] if session["target"] else 30
                conn.close()
                if session:
                    sessions.append(
                        (session["id"], session["problem"], count, target, session["status"])
                    )
            except Exception:
                pass

    if not sessions:
        print("No brainstorm sessions found.")
        return

    print(f"  {'ID':<14} {'Ideas':>7}  {'Status':<14} Problem")
    print(f"  {'---':<14} {'---':>7}  {'---':<14} ---")
    for sid, prob, count, target, status in sessions:
        p = prob if len(prob) <= 40 else prob[:37] + "..."
        print(f"  {sid:<14} {count:>2}/{target:<3}  {status:<14} {p}")


# --- CLI ---


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) < 3:
            print('Usage: brainstorm.py init "<problem>" [--count N]', file=sys.stderr)
            sys.exit(1)
        target = 30
        args = sys.argv[2:]
        if "--count" in args:
            idx = args.index("--count")
            if idx + 1 < len(args):
                target = int(args[idx + 1])
                args = args[:idx] + args[idx + 2:]
        cmd_init(args[0], target=target)

    elif cmd == "add":
        if len(sys.argv) < 4:
            print('Usage: brainstorm.py add <session> "<title>" ["<desc>"]', file=sys.stderr)
            sys.exit(1)
        # --force is a hidden flag, not documented in skill instructions
        force = "--force" in sys.argv
        args = [a for a in sys.argv[2:] if a != "--force"]
        desc = args[2] if len(args) > 2 else ""
        cmd_add(args[0], args[1], desc, force=force)

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: brainstorm.py update <session> <num> [--title T] ...", file=sys.stderr)
            sys.exit(1)
        num = int(sys.argv[3])
        kwargs = {}
        args = sys.argv[4:]
        i = 0
        while i < len(args):
            if args[i] == "--title" and i + 1 < len(args):
                kwargs["title"] = args[i + 1]
                i += 2
            elif args[i] == "--desc" and i + 1 < len(args):
                kwargs["description"] = args[i + 1]
                i += 2
            elif args[i] == "--status" and i + 1 < len(args):
                kwargs["status"] = args[i + 1]
                i += 2
            elif args[i] == "--notes" and i + 1 < len(args):
                kwargs["notes"] = args[i + 1]
                i += 2
            elif args[i] == "--tags" and i + 1 < len(args):
                kwargs["tags"] = args[i + 1]
                i += 2
            elif args[i] == "--category" and i + 1 < len(args):
                kwargs["category"] = args[i + 1]
                i += 2
            else:
                print(f"Unknown flag: {args[i]}", file=sys.stderr)
                i += 1
        cmd_update(session_id=sys.argv[2], num=num, **kwargs)

    elif cmd == "rate":
        if len(sys.argv) < 7:
            print("Usage: brainstorm.py rate <session> <num> <F> <N> <I>", file=sys.stderr)
            sys.exit(1)
        cmd_rate(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))

    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: brainstorm.py status <session>", file=sys.stderr)
            sys.exit(1)
        cmd_status(sys.argv[2])

    elif cmd == "list":
        if len(sys.argv) < 3:
            print("Usage: brainstorm.py list <session>", file=sys.stderr)
            sys.exit(1)
        cmd_list(sys.argv[2])

    elif cmd == "phase":
        if len(sys.argv) < 3:
            print("Usage: brainstorm.py phase <session>", file=sys.stderr)
            sys.exit(1)
        cmd_phase(sys.argv[2])

    elif cmd == "report":
        if len(sys.argv) < 3:
            print("Usage: brainstorm.py report <session>", file=sys.stderr)
            sys.exit(1)
        cmd_report(sys.argv[2])

    elif cmd == "check-code":
        if len(sys.argv) < 4:
            print("Usage: brainstorm.py check-code <session> <idea-number>", file=sys.stderr)
            sys.exit(1)
        cmd_check_code(sys.argv[2], int(sys.argv[3]))

    elif cmd == "prior-art":
        if len(sys.argv) < 4:
            print('Usage: brainstorm.py prior-art <session> "<title>" '
                  '["<desc>"] [--source S]', file=sys.stderr)
            sys.exit(1)
        source = ""
        args = sys.argv[2:]
        if "--source" in args:
            idx = args.index("--source")
            if idx + 1 < len(args):
                source = args[idx + 1]
                args = args[:idx] + args[idx + 2:]
        desc = args[2] if len(args) > 2 else ""
        cmd_prior_art(args[0], args[1], desc, source)

    elif cmd == "prior-art-list":
        if len(sys.argv) < 3:
            print("Usage: brainstorm.py prior-art-list <session>", file=sys.stderr)
            sys.exit(1)
        cmd_prior_art_list(sys.argv[2])

    elif cmd == "begin":
        if len(sys.argv) < 3:
            print("Usage: brainstorm.py begin <session>", file=sys.stderr)
            sys.exit(1)
        cmd_begin(sys.argv[2])

    elif cmd == "sessions":
        cmd_sessions()

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

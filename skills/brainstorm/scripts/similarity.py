#!/usr/bin/env python3
"""Shape uniqueness checker for brainstorm ideas.

Multi-layer similarity detection:
  Layer 1  Static  — content-word and bigram Jaccard similarity
  Layer 2  Semantic — embedding cosine similarity (sentence-transformers)
  Layer 3  Lexical  — FTS5 BM25 ranking boosts borderline semantic matches
  Layer 4  Code    — embedding similarity on prototype/sandbox code

An idea is rejected if it overlaps with any existing idea on any layer.
Degrades gracefully: without sentence-transformers, only layers 1+3 run.
Without FTS5, only layers 1+2 run. Without code, layer 4 is skipped.
"""

import logging
import os
import re
import sqlite3
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

# Suppress noisy model-loading output
warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

try:
    import numpy as np
except ImportError:
    np = None

BRAINSTORM_DIR = Path.cwd() / ".brainstorm"

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

COSINE_THRESHOLD = 0.78
JACCARD_THRESHOLD = 0.65
COMBINED_COSINE = 0.70
CODE_COSINE_THRESHOLD = 0.60
CODE_STRUCTURAL_THRESHOLD = 0.70  # trigram Jaccard on normalized code tokens

# Prior art: only block literal restatements of known approaches
PA_COSINE_THRESHOLD = 0.90
PA_JACCARD_THRESHOLD = 0.75

# ---------------------------------------------------------------------------
# Static analysis
# ---------------------------------------------------------------------------

STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did will "
    "would could should may might can shall to of in for on with at by from "
    "as into through during before after above below between out off over "
    "under again further then once that this these those it its and but or "
    "nor not so yet both each few more most other some such no only own same "
    "than too very just because about up down here there when where why how "
    "all any every what which who whom use using based via".split()
)


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def bigrams(tokens):
    return [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]


def jaccard(a, b):
    if not a and not b:
        return 0.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def static_similarity(text_a, text_b):
    """Weighted unigram + bigram Jaccard."""
    tok_a, tok_b = tokenize(text_a), tokenize(text_b)
    uni = jaccard(set(tok_a), set(tok_b))
    bi = jaccard(set(bigrams(tok_a)), set(bigrams(tok_b)))
    return 0.7 * uni + 0.3 * bi


# ---------------------------------------------------------------------------
# Semantic analysis (sentence-transformers)
# ---------------------------------------------------------------------------

_model = None
_model_attempted = False


def get_model():
    global _model, _model_attempted
    if _model_attempted:
        return _model
    _model_attempted = True
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        _model = None
        print(
            "  [similarity] sentence-transformers not installed — "
            "semantic layer disabled.",
            file=sys.stderr,
        )
        print(
            "  [similarity] pip install sentence-transformers",
            file=sys.stderr,
        )
    return _model


def get_embedding(text):
    model = get_model()
    if model is None or np is None:
        return None
    return model.encode(text, normalize_embeddings=True).astype(np.float32)


def cosine_sim(a, b):
    return float(np.dot(a, b))


# ---------------------------------------------------------------------------
# Code collection
# ---------------------------------------------------------------------------

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".java", ".c", ".cpp",
    ".h", ".hpp", ".rb", ".sh", ".bash", ".sql", ".r", ".jl", ".lua", ".zig",
    ".swift", ".kt", ".scala", ".cs", ".php", ".pl", ".ex", ".exs", ".clj",
    ".hs", ".ml", ".yaml", ".yml", ".toml", ".json", ".html", ".css",
}


def collect_sandbox_code(session_id, idea_number):
    """Read all code files from an idea's sandbox, return as single string."""
    sandbox = BRAINSTORM_DIR / session_id / "sandboxes" / f"idea-{idea_number:03d}"
    if not sandbox.exists():
        return None

    chunks = []
    for path in sorted(sandbox.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        try:
            text = path.read_text(errors="replace")
            # Skip empty/trivial files
            if len(text.strip()) < 20:
                continue
            # Cap per-file to avoid blowing up embeddings on huge files
            chunks.append(text[:4000])
        except Exception:
            continue

    return "\n\n".join(chunks) if chunks else None


# ---------------------------------------------------------------------------
# Code structural normalization
# ---------------------------------------------------------------------------

# Keywords across common languages — not exhaustive, just enough to keep them
# from being replaced with ID during normalization.
_LANG_KEYWORDS = frozenset(
    # python
    "def class if elif else for while with try except finally return yield "
    "import from as in not and or is lambda pass break continue raise global "
    "nonlocal assert async await True False None "
    # js/ts
    "function var let const typeof instanceof new delete void this super "
    "switch case default throw catch of export require extends implements "
    "interface type enum "
    # rust
    "fn let mut pub struct enum impl trait match loop mod use crate self "
    "where unsafe extern ref move "
    # go
    "func package import var type struct interface map chan go select defer "
    "range fallthrough "
    # general
    "int float double string bool char byte long short unsigned signed void "
    "static final abstract override virtual public private protected "
    "null nil true false".split()
)


def normalize_code(code):
    """Replace identifiers with positional tokens, keep structure.

    Two functions that differ only in variable/function names will
    normalize to the same token sequence.
    """
    # Tokenize: identifiers, numbers, operators, punctuation
    raw_tokens = re.findall(r"[a-zA-Z_]\w*|\d+(?:\.\d+)?|[^\s\w]|\n", code)
    # Map each unique non-keyword identifier to a positional token
    id_map = {}
    counter = 0
    normalized = []
    for tok in raw_tokens:
        if tok == "\n":
            normalized.append("NL")
        elif re.match(r"^\d", tok):
            normalized.append("NUM")
        elif re.match(r"^[a-zA-Z_]", tok):
            low = tok.lower()
            if low in _LANG_KEYWORDS:
                normalized.append(low)
            elif tok.startswith(("__", "self", "this", "cls")):
                normalized.append(low)
            else:
                if tok not in id_map:
                    id_map[tok] = f"V{counter}"
                    counter += 1
                normalized.append(id_map[tok])
        else:
            normalized.append(tok)
    return normalized


def code_trigrams(tokens):
    """Generate trigrams from a token list."""
    return {
        f"{tokens[i]}|{tokens[i+1]}|{tokens[i+2]}"
        for i in range(len(tokens) - 2)
    }


def code_structural_similarity(code_a, code_b):
    """Trigram Jaccard on structurally normalized code."""
    norm_a = normalize_code(code_a)
    norm_b = normalize_code(code_b)
    tri_a = code_trigrams(norm_a)
    tri_b = code_trigrams(norm_b)
    return jaccard(tri_a, tri_b)


# ---------------------------------------------------------------------------
# FTS5
# ---------------------------------------------------------------------------

_fts5_available = None


def fts5_available(conn):
    global _fts5_available
    if _fts5_available is not None:
        return _fts5_available
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS ideas_fts "
            "USING fts5(title, description, content='', content_rowid='rowid')"
        )
        _fts5_available = True
    except Exception:
        _fts5_available = False
    return _fts5_available


def fts_insert(conn, rowid, title, description):
    if not fts5_available(conn):
        return
    try:
        conn.execute(
            "INSERT INTO ideas_fts(rowid, title, description) VALUES (?, ?, ?)",
            (rowid, title, description),
        )
    except Exception:
        pass


def fts_query(conn, text, limit=5):
    """Query FTS5 for matching ideas. Returns set of matching rowids."""
    if not fts5_available(conn):
        return set()
    safe = re.sub(r"[^\w\s]", " ", text)
    tokens = safe.split()[:20]
    if not tokens:
        return set()
    query = " OR ".join(tokens)
    try:
        rows = conn.execute(
            "SELECT rowid FROM ideas_fts WHERE ideas_fts MATCH ? LIMIT ?",
            (query, limit),
        ).fetchall()
        return {r[0] for r in rows}
    except Exception:
        return set()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass
class Overlap:
    idea_number: int
    idea_title: str
    reason: str
    score: float

    def __str__(self):
        return (
            f"  #{self.idea_number:02d} \"{self.idea_title}\" "
            f"— {self.reason} ({self.score:.0%})"
        )


def _check_against_entries(text, new_emb, entries, fts_flagged,
                           label_prefix="",
                           cosine_thresh=None, jaccard_thresh=None,
                           combined_thresh=None):
    """Check text against a list of entries with configurable thresholds."""
    cos_t = cosine_thresh if cosine_thresh is not None else COSINE_THRESHOLD
    jac_t = jaccard_thresh if jaccard_thresh is not None else JACCARD_THRESHOLD
    com_t = combined_thresh if combined_thresh is not None else COMBINED_COSINE

    overlaps = []
    has_emb = new_emb is not None

    for entry in entries:
        entry_id = entry["number"] if "number" in entry.keys() else entry["id"]
        entry_text = (
            f"{entry['title']}. {entry['description']}"
            if entry["description"]
            else entry["title"]
        )
        entry_title = f"{label_prefix}{entry['title']}"

        # Layer 1: static word/bigram overlap
        static = static_similarity(text, entry_text)
        if static > jac_t:
            overlaps.append(
                Overlap(entry_id, entry_title, "word overlap", static)
            )
            continue

        # Layer 2: semantic cosine similarity
        if has_emb and entry["embedding"]:
            existing_emb = np.frombuffer(entry["embedding"], dtype=np.float32)
            cos = cosine_sim(new_emb, existing_emb)

            if cos > cos_t:
                overlaps.append(
                    Overlap(entry_id, entry_title, "semantic similarity", cos)
                )
                continue

            # Layer 3: FTS5 flag + moderate cosine
            if entry_id in fts_flagged and cos > com_t:
                overlaps.append(
                    Overlap(entry_id, entry_title, "keyword + semantic overlap", cos)
                )
                continue

    return overlaps


def check_uniqueness(conn, title, description, session_id=None):
    """Check a proposed idea against existing ideas (hard gate) and prior art (soft gate).

    Prior art uses much higher thresholds — it only blocks near-duplicates of
    known approaches, not ideas that happen to share domain vocabulary.
    Ideas-vs-ideas uses the standard thresholds to prevent self-repetition.

    Returns (is_unique: bool, overlaps: list[Overlap], advisories: list[Overlap]).
    Advisories are near-prior-art matches that are noted but not blocking.
    """
    text = f"{title}. {description}" if description else title
    new_emb = get_embedding(text)
    fts_flagged = fts_query(conn, text)

    # Hard gate: check against existing ideas (standard thresholds)
    ideas = conn.execute(
        "SELECT number, title, description, embedding "
        "FROM ideas ORDER BY number"
    ).fetchall()
    overlaps = _check_against_entries(text, new_emb, ideas, fts_flagged)

    # Soft gate: check against prior art (higher thresholds — only block
    # near-duplicates, not domain-adjacent ideas)
    advisories = []
    prior = conn.execute(
        "SELECT id, title, description, embedding "
        "FROM prior_art ORDER BY id"
    ).fetchall()
    if prior:
        pa_blocks = _check_against_entries(
            text, new_emb, prior, set(),
            label_prefix="[prior art] ",
            cosine_thresh=PA_COSINE_THRESHOLD,
            jaccard_thresh=PA_JACCARD_THRESHOLD,
            combined_thresh=PA_COSINE_THRESHOLD,
        )
        overlaps.extend(pa_blocks)

        # Also check at standard thresholds for advisories (noted but not blocking)
        if not pa_blocks:
            pa_near = _check_against_entries(
                text, new_emb, prior, set(),
                label_prefix="[prior art] ",
            )
            advisories.extend(pa_near)

    return len(overlaps) == 0, overlaps, advisories


def check_code_uniqueness(conn, session_id, idea_number):
    """Check an idea's sandbox code against all other ideas' code.

    Two layers:
      - Structural: normalize identifiers out, compare token trigrams
      - Semantic: embedding cosine on raw code

    Called after prototyping. Returns (is_unique: bool, overlaps: list[Overlap]).
    """
    code = collect_sandbox_code(session_id, idea_number)
    if not code:
        return True, []

    # Compute and store embedding
    code_emb = get_embedding(code[:8000])
    if code_emb is not None:
        conn.execute(
            "UPDATE ideas SET code_embedding = ? WHERE number = ?",
            (code_emb.tobytes(), idea_number),
        )
        conn.commit()

    overlaps = []
    ideas = conn.execute(
        "SELECT number, title, code_embedding FROM ideas "
        "WHERE number != ? ORDER BY number",
        (idea_number,),
    ).fetchall()

    for idea in ideas:
        # Structural: compare normalized code token trigrams
        other_code = collect_sandbox_code(session_id, idea["number"])
        if other_code:
            struct_sim = code_structural_similarity(code, other_code)
            if struct_sim > CODE_STRUCTURAL_THRESHOLD:
                overlaps.append(
                    Overlap(
                        idea["number"], idea["title"],
                        "code structure overlap", struct_sim,
                    )
                )
                continue

        # Semantic: embedding cosine on raw code
        if code_emb is not None and idea["code_embedding"]:
            existing_emb = np.frombuffer(idea["code_embedding"], dtype=np.float32)
            cos = cosine_sim(code_emb, existing_emb)
            if cos > CODE_COSINE_THRESHOLD:
                overlaps.append(
                    Overlap(idea["number"], idea["title"],
                            "code similarity", cos)
                )

    return len(overlaps) == 0, overlaps

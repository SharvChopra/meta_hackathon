import sqlite3
import random
from typing import Dict, Any, Optional

# --- FIXED: Added actual fallback data instead of empty lists ---
FALLBACK_ISSUE_POOL = {
    'easy': [
        {'title': 'Fix typo in README.md',
            'description': 'There is a spelling mistake in the installation instructions. Please add the Docs label.', 'code_snippet': None},
        {'title': 'Button is misaligned',
            'description': 'The submit button is slightly off-center on mobile. Apply the Bug label.', 'code_snippet': None}
    ],
    'medium': [
        {'title': 'Memory Leak in background worker', 'description': 'This issue was already reported. Close this as a duplicate of issue #12.',
            'duplicate_of_id': 12, 'code_snippet': None},
        {'title': 'API Rate limit too low', 'description': 'Users are hitting the limit too fast. Duplicate of issue #45.',
            'duplicate_of_id': 45, 'code_snippet': None}
    ],
    'hard': [
        {'title': 'Update payment gateway webhook', 'description': 'Review the PR. The error handling is missing.',
            'code_snippet': 'def handle_webhook(req):\n    process(req.body)\n    # Missing try/catch here!'},
        {'title': 'Refactor user auth token', 'description': 'The token expiration is hardcoded. Request changes before merging.',
            'code_snippet': 'token.expires_in = 3600; // hardcoded'}
    ]
}

try:
    from mock_data import ISSUE_POOL # type: ignore
    # If the imported pool is empty, use the fallback
    if not ISSUE_POOL.get('easy'):
        ISSUE_POOL = FALLBACK_ISSUE_POOL
except (ImportError, ModuleNotFoundError, AttributeError):
    ISSUE_POOL = FALLBACK_ISSUE_POOL

DB_NAME = "hackathon.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def reset_database() -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS tickets")

    cursor.execute("""
        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY,
            difficulty TEXT,
            status TEXT,
            title TEXT,
            description TEXT,
            code_snippet TEXT,
            linked_issue INTEGER,
            comments TEXT
        )
    """)

    difficulty = random.choice(['easy', 'medium', 'hard'])
    issues = ISSUE_POOL.get(difficulty, [])

    # Safe selection
    if not issues:
        issue = {'title': 'System Error',
                 'description': 'No issues found in pool.'}
    else:
        issue = random.choice(issues)

    title = issue.get('title')
    description = issue.get('description')
    code_snippet = issue.get('code_snippet')

    cursor.execute("""
        INSERT INTO tickets (difficulty, status, title, description, code_snippet)
        VALUES (?, 'open', ?, ?, ?)
    """, (difficulty, title, description, code_snippet))

    conn.commit()

    cursor.execute("SELECT * FROM tickets WHERE id = last_insert_rowid()")
    row = cursor.fetchone()
    conn.close()

    return dict(row)


def get_current_ticket() -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM tickets LIMIT 1")
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        row = None

    conn.close()

    if row:
        return dict(row)

    # Auto-initialize on first run if missing
    return reset_database()

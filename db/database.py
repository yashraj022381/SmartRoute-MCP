import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "smartroute.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS routing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            agent TEXT,
            query TEXT,
            tier_used TEXT NOT NULL,
            model_used TEXT NOT NULL,
            complexity_score REAL,
            fallback_triggered INTEGER NOT NULL DEFAULT 0,
            latency_seconds REAL,
            input_tokens INTEGER,
            output_tokens INTEGER,
            estimated_cost_usd REAL
        )
    """)

    # A simple key-value table for things the system needs to remember
    # between runs - right now just the current classifier threshold,
    # but this is a natural place to store other learned settings later.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = None) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default
 
 
def set_setting(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    conn.commit()
    conn.close()
 
 
def get_recent_weak_tier_stats(limit: int = 50) -> dict:
    """
    Look at the most recent N decisions that used the WEAK (cheap) model,
    and report how often they needed a fallback. This is the raw
    ingredient for calibration - "how well has the cheap model actually
    been doing lately?"
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT fallback_triggered FROM routing_log
        WHERE tier_used = 'weak' OR fallback_triggered = 1
        ORDER BY id DESC LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
 
    if not rows:
        return {"sample_size": 0, "fallback_rate": None}
 
    fallback_count = sum(r[0] for r in rows)
    return {
        "sample_size": len(rows),
        "fallback_rate": round(fallback_count / len(rows), 3),
    }



def log_decision(query: str, result: dict, agent: str = None):
    try:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO routing_log (
                timestamp, agent, query, tier_used, model_used,
                complexity_score, fallback_triggered, latency_seconds,
                input_tokens, output_tokens, estimated_cost_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                agent,
                query[:500],
                result["tier_used"],
                result["model_used"],
                result["complexity_score"],
                int(result["fallback_triggered"]),
                result["latency_seconds"],
                result["input_tokens"],
                result["output_tokens"],
                result["estimated_cost_usd"],
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[warning] failed to log routing decision to databases: {e}")


def get_summary_stats() -> dict:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM routing_log")
    total_queries = cursor.fetchone()[0]

    if total_queries == 0:
        conn.close()
        return {"total_queries": 0}

    cursor.execute("SELECT SUM(estimated_cost_usd) FROM routing_log")
    total_cost = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT tier_used, COUNT(*) FROM routing_log GROUP BY tier_used")
    tier_counts = dict(cursor.fetchall())

    cursor.execute("SELECT SUM(fallback_triggered) FROM routing_log")
    total_fallbacks = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(latency_seconds) FROM routing_log WHERE tier_used = 'weak'")
    avg_latency_weak = cursor.fetchone()[0]
 
    cursor.execute("SELECT AVG(latency_seconds) FROM routing_log WHERE tier_used = 'strong'")
    avg_latency_strong = cursor.fetchone()[0]

    conn.close()

    return {
        "total_queries": total_queries,
        "total_cost_usd": round(total_cost, 8),
        "tier_counts": tier_counts,
        "total_fallbacks": total_fallbacks,
        "fallback_rate": round(total_fallbacks / total_queries, 3),
        "avg_latency_weak": round(avg_latency_weak, 2) if avg_latency_weak else None,
        "avg_latency_strong": round(avg_latency_strong, 2) if avg_latency_strong else None,
    }     
        
 

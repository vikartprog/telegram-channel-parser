import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "telegram.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        username TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        subscriber_count INTEGER,
        last_updated TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER,
        channel_username TEXT,
        text TEXT,
        date TEXT,
        comments INTEGER,
        PRIMARY KEY (id, channel_username),
        FOREIGN KEY (channel_username) REFERENCES channels(username)
    )
    """)

    conn.commit()
    conn.close()

def save_channel(channel):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO channels (username, title, description, subscriber_count, last_updated)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(username) DO UPDATE SET
        title=excluded.title,
        description=excluded.description,
        subscriber_count=excluded.subscriber_count,
        last_updated=excluded.last_updated
    """, (
        channel["username"],
        channel["title"],
        channel["description"],
        channel["subscriber_count"],
        channel["last_updated"]
    ))
    conn.commit()
    conn.close()

def save_posts(posts):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    data = [
        (int(p["id"]), p["channel_username"], p["text"], p["date"], p["comments"])
        for p in posts
    ]
    cur.executemany("""
    INSERT INTO posts (id, channel_username, text, date, comments)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id, channel_username) DO UPDATE SET
        text=excluded.text,
        date=excluded.date,
        comments=excluded.comments
    """, data)
    conn.commit()
    conn.close()
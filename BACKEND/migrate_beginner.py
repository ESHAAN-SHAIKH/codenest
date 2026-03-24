"""Migration script: add beginner mode columns to existing SQLite database."""
from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    statements = [
        "ALTER TABLE users ADD COLUMN is_beginner_mode BOOLEAN DEFAULT 1",
        "ALTER TABLE users ADD COLUMN beginner_phase VARCHAR(20) DEFAULT 'scaffolded'",
        "ALTER TABLE challenges ADD COLUMN challenge_mode VARCHAR(20) DEFAULT 'freeform'",
        "ALTER TABLE challenges ADD COLUMN scaffold_data JSON",
    ]
    for stmt in statements:
        try:
            db.session.execute(text(stmt))
            db.session.commit()
            print(f"OK: {stmt[:60]}")
        except Exception as e:
            db.session.rollback()
            print(f"SKIP: {str(e)[:80]}")
    print("Migration complete.")

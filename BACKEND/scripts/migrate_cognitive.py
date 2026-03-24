"""
Database Migration for Cognitive Training
Creates all new tables for the cognitive modeling engine
"""

from app import create_app
from app.extensions import db
from app.cognitive_models.cognitive import Concept, ConceptMastery, MisconceptionTag
from app.cognitive_models.learning import CodeIteration, DebuggingSession
from app.cognitive_models.progression import ArchetypeProgress
from app.cognitive_models.arena import ArenaMatch, ArenaRating

def create_tables():
    """Create all new cognitive training tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating cognitive training database tables...")
        
        try:
            # Create all tables defined in models
            db.create_all()
            
            print("✅ Successfully created all tables:")
            print("  - concepts")
            print("  - concept_mastery")
            print("  - misconception_tags")
            print("  - code_iterations")
            print("  - debugging_sessions")
            print("  - archetype_progress")
            print("  - arena_matches")
            print("  - arena_ratings")
            
            print("\n📦 Database migration complete!")
            print("Next step: Run the concept seeding script:")
            print("  python -m scripts.seed_concepts")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise

if __name__ == '__main__':
    create_tables()

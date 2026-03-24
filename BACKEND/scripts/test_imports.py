"""
Simple test script to verify model imports and database setup
"""

import sys
import traceback

print("=" * 60)
print("CODENEST Model Import Test")
print("=" * 60)

# Test 1: Import extensions
print("\n[1/6] Testing extensions import...")
try:
    from app.extensions import db
    print("✅ Extensions imported successfully")
except Exception as e:
    print(f"❌ Extensions import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Import main models
print("\n[2/6] Testing main models import...")
try:
    from app.models import User, Lesson, Challenge, Progress, Badge, Analytics
    print(f"✅ Main models imported successfully")
    print(f"   - User, Lesson, Challenge, Progress, Badge, Analytics")
except Exception as e:
    print(f"❌ Main models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Import cognitive models
print("\n[3/6] Testing cognitive models import...")
try:
    from app.cognitive_models.cognitive import Concept, ConceptMastery, MisconceptionTag
    print(f"✅ Cognitive models imported successfully")
    print(f"   - Concept, ConceptMastery, MisconceptionTag")
except Exception as e:
    print(f"❌ Cognitive models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Import learning models
print("\n[4/6] Testing learning models import...")
try:
    from app.cognitive_models.learning import CodeIteration, DebuggingSession
    print(f"✅ Learning models imported successfully")
    print(f"   -CodeIteration, DebuggingSession")
except Exception as e:
    print(f"❌ Learning models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Import progression models
print("\n[5/6] Testing progression models import...")
try:
    from app.cognitive_models.progression import ArchetypeProgress
    print(f"✅ Progression models imported successfully")
    print(f"   - ArchetypeProgress")
except Exception as e:
    print(f"❌ Progression models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Import arena models
print("\n[6/6] Testing arena models import...")
try:
    from app.cognitive_models.arena import ArenaMatch, ArenaRating
    print(f"✅ Arena models imported successfully")
    print(f"   - ArenaMatch, ArenaRating")
except Exception as e:
    print(f"❌ Arena models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL MODEL IMPORTS SUCCESSFUL!")
print("=" * 60)

# Test app creation
print("\n[Bonus] Testing Flask app creation...")
try:
    from app import create_app
    app = create_app()
    print(f"✅ Flask app created successfully")
    print(f"   App name: {app.name}")
    print(f"   Debug mode: {app.debug}")
except Exception as e:
    print(f"❌ App creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test database context
print("\n[Bonus] Testing database context...")
try:
    with app.app_context():
        # Try to access db metadata
        print(f"✅ Database context works")
        print(f"   Tables will be created via db.create_all()")
except Exception as e:
    print(f"❌ Database context failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nNext steps:")
print("1. Run database migration: python -m scripts.migrate_cognitive")
print("2. Seed concepts: python -m scripts.seed_concepts")
print("3. Start backend: python run.py")

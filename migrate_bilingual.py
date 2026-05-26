"""
Database migration script to add bilingual support.

This script adds _pt and _en columns to existing tables and migrates
existing data to the new columns.

Usage: python migrate_bilingual.py
"""
import sqlite3
from pathlib import Path

# Path to database
DB_PATH = Path(__file__).parent / "test.db"


def migrate_database():
    """Add bilingual columns and migrate existing data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting bilingual migration...")
    
    try:
        # 1. Add columns to portfolios table
        print("\n1. Migrating portfolios table...")
        
        # Add new columns
        cursor.execute("ALTER TABLE portfolios ADD COLUMN name_pt TEXT")
        cursor.execute("ALTER TABLE portfolios ADD COLUMN name_en TEXT")
        cursor.execute("ALTER TABLE portfolios ADD COLUMN description_pt TEXT")
        cursor.execute("ALTER TABLE portfolios ADD COLUMN description_en TEXT")
        cursor.execute("ALTER TABLE portfolios ADD COLUMN location_pt TEXT")
        cursor.execute("ALTER TABLE portfolios ADD COLUMN location_en TEXT")
        print("   - Added bilingual columns")
        
        # Migrate existing data to Portuguese columns (default language)
        cursor.execute("""
            UPDATE portfolios 
            SET name_pt = name,
                description_pt = description,
                location_pt = location
            WHERE name IS NOT NULL OR description IS NOT NULL OR location IS NOT NULL
        """)
        print("   - Migrated existing data to Portuguese columns")
        
        # 2. Add columns to hero_images table
        print("\n2. Migrating hero_images table...")
        
        cursor.execute("ALTER TABLE hero_images ADD COLUMN caption_pt TEXT")
        cursor.execute("ALTER TABLE hero_images ADD COLUMN caption_en TEXT")
        print("   - Added bilingual columns")
        
        # Migrate existing captions to Portuguese
        cursor.execute("""
            UPDATE hero_images 
            SET caption_pt = caption
            WHERE caption IS NOT NULL
        """)
        print("   - Migrated existing captions to Portuguese")
        
        # 3. Add columns to portfolio_images table
        print("\n3. Migrating portfolio_images table...")
        
        cursor.execute("ALTER TABLE portfolio_images ADD COLUMN caption_pt TEXT")
        cursor.execute("ALTER TABLE portfolio_images ADD COLUMN caption_en TEXT")
        print("   - Added bilingual columns")
        
        # Migrate existing captions to Portuguese
        cursor.execute("""
            UPDATE portfolio_images 
            SET caption_pt = caption
            WHERE caption IS NOT NULL
        """)
        print("   - Migrated existing captions to Portuguese")
        
        # 4. Add columns to technical_images table (if it exists)
        print("\n4. Migrating technical_images table...")
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='technical_images'
        """)
        
        if cursor.fetchone():
            cursor.execute("ALTER TABLE technical_images ADD COLUMN caption_pt TEXT")
            cursor.execute("ALTER TABLE technical_images ADD COLUMN caption_en TEXT")
            print("   - Added bilingual columns")
            
            # Migrate existing captions to Portuguese
            cursor.execute("""
                UPDATE technical_images 
                SET caption_pt = caption
                WHERE caption IS NOT NULL
            """)
            print("   - Migrated existing captions to Portuguese")
        else:
            print("   - Table does not exist, skipping")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM portfolios WHERE name_pt IS NOT NULL")
        portfolio_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hero_images WHERE caption_pt IS NOT NULL")
        hero_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM portfolio_images WHERE caption_pt IS NOT NULL")
        image_count = cursor.fetchone()[0]
        
        print(f"\nMigration summary:")
        print(f"  - Portfolios migrated: {portfolio_count}")
        print(f"  - Hero images migrated: {hero_count}")
        print(f"  - Portfolio images migrated: {image_count}")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"\n⚠️  Warning: {e}")
            print("   Columns may already exist. Skipping column creation.")
            conn.rollback()
        else:
            print(f"\n❌ Error during migration: {e}")
            conn.rollback()
            raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    print(f"Database path: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Please check the database path.")
        exit(1)
    
    # Check for --yes flag to skip confirmation
    if "--yes" in sys.argv or "-y" in sys.argv:
        migrate_database()
    else:
        # Confirm before running
        response = input("\nThis will modify the database. Continue? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            migrate_database()
        else:
            print("Migration cancelled.")

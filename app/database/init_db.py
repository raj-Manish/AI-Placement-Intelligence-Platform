"""
Database initialization and seeding script:
1. Enables the PostgreSQL `vector` extension.
2. Creates tables: documents, document_chunks, companies.
3. Seeds benchmark company hiring data from data/companies.csv.
"""

import os
import csv
from sqlalchemy import text
from app.database.connection import get_engine, get_session_factory, Base
from app.database.models import Document, DocumentChunk, Company


def init_database():
    """Initializes the database schema and seeds benchmark company data."""
    print("=" * 60)
    print("AI Placement Intelligence Platform - Database Initializer")
    print("=" * 60)

    try:
        engine = get_engine()
        print("Connecting to PostgreSQL database...")

        with engine.connect() as conn:
            # 1. Enable pgvector extension
            print("Step 1: Enabling 'vector' extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("   -> 'vector' extension enabled successfully.")

        # 2. Create tables
        print("Step 2: Creating database tables (documents, document_chunks, companies)...")
        Base.metadata.create_all(bind=engine)
        print("   -> All tables created or verified successfully.")

        # 3. Seed benchmark companies if table is empty
        Session = get_session_factory()
        with Session() as session:
            existing_count = session.query(Company).count()
            if existing_count == 0:
                print("Step 3: Seeding benchmark company dataset...")
                csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "companies.csv")
                csv_path = os.path.abspath(csv_path)

                if os.path.exists(csv_path):
                    with open(csv_path, mode="r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        companies_to_add = []
                        for row in reader:
                            company = Company(
                                company_name=row["company_name"].strip(),
                                role=row["role"].strip(),
                                required_skills=row["required_skills"].strip(),
                                min_salary=float(row["min_salary"]),
                                max_salary=float(row["max_salary"]),
                                hiring_history=row["hiring_history"].strip()
                            )
                            companies_to_add.append(company)

                        session.bulk_save_objects(companies_to_add)
                        session.commit()
                        print(f"   -> Successfully seeded {len(companies_to_add)} benchmark company records.")
                else:
                    print(f"   -> Warning: {csv_path} not found. Skipping seeding.")
            else:
                print(f"Step 3: Companies table already contains {existing_count} records. Skipping seeding.")

        print("=" * 60)
        print("Database initialization complete! Ready for RAG and matching.")
        print("=" * 60)
        return True

    except Exception as e:
        print("\n[ERROR] Database initialization failed:")
        print(f"   Detail: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check that PostgreSQL is running.")
        print("2. Check DATABASE_URL in your .env file.")
        print("3. Ensure the 'vector' extension is installed in PostgreSQL.")
        return False


if __name__ == "__main__":
    init_database()

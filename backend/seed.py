"""Seed a few HCPs so the 'Search or select HCP' field has data to work with.

Run:  python seed.py
"""

from app.database import Base, SessionLocal, engine
from app import models

HCPS = [
    {"name": "Dr. Smith", "specialty": "Cardiology", "institution": "City General Hospital"},
    {"name": "Dr. John", "specialty": "Endocrinology", "institution": "Metro Medical Center"},
    {"name": "Dr. Emily Chen", "specialty": "Oncology", "institution": "Riverside Cancer Institute"},
    {"name": "Dr. Rajesh Kumar", "specialty": "Neurology", "institution": "Apollo Clinic"},
    {"name": "Dr. Maria Garcia", "specialty": "Pediatrics", "institution": "Children's Health Network"},
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.HCP).count() == 0:
            db.add_all([models.HCP(**h) for h in HCPS])
            db.commit()
            print(f"Seeded {len(HCPS)} HCPs.")
        else:
            print("HCPs already present, skipping.")
    finally:
        db.close()


if __name__ == "__main__":
    run()

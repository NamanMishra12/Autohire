from app.database.session import SessionLocal
from app.models.resume import Resume

db = SessionLocal()
resumes = db.query(Resume).all()

for r in resumes:
    print(r.id, r.original_filename, r.checksum, r.version, r.is_active)

db.close()
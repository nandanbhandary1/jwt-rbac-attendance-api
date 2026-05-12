import datetime
import random
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import User, RoleEnum, Batch, Session as DBSession, Attendance, AttendanceStatusEnum, batch_students, batch_trainers
from .auth import get_password_hash

def seed_db():
    print("Creating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded.")
            return

        print("Seeding database...")
        # Password for all: "password123"
        hashed_password = get_password_hash("password123")

        # Create Roles
        print("Creating Programme Manager & Monitoring Officer...")
        pm = User(name="Program Manager", email="pm@example.com", hashed_password=hashed_password, role=RoleEnum.programme_manager)
        mo = User(name="Monitoring Officer", email="mo@example.com", hashed_password=hashed_password, role=RoleEnum.monitoring_officer)
        db.add_all([pm, mo])
        db.commit()

        # 2 Institutions
        print("Creating Institutions...")
        inst1 = User(name="Tech Institute", email="inst1@example.com", hashed_password=hashed_password, role=RoleEnum.institution)
        inst2 = User(name="Business Academy", email="inst2@example.com", hashed_password=hashed_password, role=RoleEnum.institution)
        db.add_all([inst1, inst2])
        db.commit()

        # 4 Trainers
        print("Creating Trainers...")
        trainers = []
        for i in range(1, 5):
            trainer = User(name=f"Trainer {i}", email=f"trainer{i}@example.com", hashed_password=hashed_password, role=RoleEnum.trainer)
            db.add(trainer)
            trainers.append(trainer)
        db.commit()

        # 15 Students
        print("Creating Students...")
        students = []
        for i in range(1, 16):
            student = User(name=f"Student {i}", email=f"student{i}@example.com", hashed_password=hashed_password, role=RoleEnum.student)
            db.add(student)
            students.append(student)
        db.commit()

        # 3 Batches
        print("Creating Batches...")
        b1 = Batch(name="Python Cohort 1", institution_id=inst1.id)
        b2 = Batch(name="Data Science Cohort 1", institution_id=inst1.id)
        b3 = Batch(name="Management Basics", institution_id=inst2.id)
        db.add_all([b1, b2, b3])
        db.commit()

        # Assign Trainers and Students to Batches
        db.execute(batch_trainers.insert().values(batch_id=b1.id, trainer_id=trainers[0].id))
        db.execute(batch_trainers.insert().values(batch_id=b2.id, trainer_id=trainers[1].id))
        db.execute(batch_trainers.insert().values(batch_id=b3.id, trainer_id=trainers[2].id))
        db.execute(batch_trainers.insert().values(batch_id=b3.id, trainer_id=trainers[3].id))

        # Students: 5 per batch
        for i in range(5):
            db.execute(batch_students.insert().values(batch_id=b1.id, student_id=students[i].id))
            db.execute(batch_students.insert().values(batch_id=b2.id, student_id=students[i+5].id))
            db.execute(batch_students.insert().values(batch_id=b3.id, student_id=students[i+10].id))
        db.commit()

        # 8 Sessions
        print("Creating Sessions...")
        sessions = []
        for i in range(1, 9):
            batch_id = b1.id if i <= 3 else (b2.id if i <= 6 else b3.id)
            trainer_id = trainers[0].id if batch_id == b1.id else (trainers[1].id if batch_id == b2.id else trainers[2].id)
            session = DBSession(
                batch_id=batch_id,
                trainer_id=trainer_id,
                title=f"Session {i}",
                date=datetime.date.today() - datetime.timedelta(days=10-i),
                start_time=datetime.time(10, 0),
                end_time=datetime.time(12, 0)
            )
            db.add(session)
            sessions.append(session)
        db.commit()

        # Attendance Records
        print("Creating Attendance...")
        statuses = [AttendanceStatusEnum.present, AttendanceStatusEnum.absent, AttendanceStatusEnum.late]
        for session in sessions:
            if session.batch_id == b1.id:
                batch_students_list = students[0:5]
            elif session.batch_id == b2.id:
                batch_students_list = students[5:10]
            else:
                batch_students_list = students[10:15]
            
            for student in batch_students_list:
                att = Attendance(
                    session_id=session.id,
                    student_id=student.id,
                    status=random.choice(statuses)
                )
                db.add(att)
        db.commit()

        print("Seeding complete.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

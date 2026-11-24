import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "ai_health_prediction.db"
)


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            blood_group TEXT,
            phone TEXT,
            date_of_birth TEXT,
            email TEXT,
            glucose REAL,
            haemoglobin REAL,
            cholesterol REAL,
            remarks TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blood_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            report_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """
    )

    conn.commit()
    conn.close()


def _normalize_patient_row(row):
    patient = dict(row)
    patient["patient_id"] = patient.get("patient_id", patient.get("id"))
    return patient


def is_patient_name_duplicate(full_name, exclude_patient_id=None):
    normalized_name = full_name.strip().lower()
    if not normalized_name:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    if exclude_patient_id is None:
        cursor.execute(
            """
            SELECT 1
            FROM patients
            WHERE lower(trim(full_name)) = ?
            LIMIT 1
            """,
            (normalized_name,),
        )
    else:
        cursor.execute(
            """
            SELECT 1
            FROM patients
            WHERE lower(trim(full_name)) = ?
              AND id != ?
            LIMIT 1
            """,
            (normalized_name, exclude_patient_id),
        )

    duplicate = cursor.fetchone() is not None
    conn.close()
    return duplicate


def add_patient(full_name, *args, **kwargs):
    if is_patient_name_duplicate(full_name):
        return None

    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if args and isinstance(args[0], (int, float)):
        age = kwargs.get("age", args[0])
        gender = kwargs.get("gender", args[1] if len(args) >= 2 else "Other")
        height = kwargs.get("height", args[2] if len(args) >= 3 else 0.0)
        weight = kwargs.get("weight", args[3] if len(args) >= 4 else 0.0)
        blood_group = kwargs.get("blood_group", args[4] if len(args) >= 5 else "")
        phone = kwargs.get("phone", args[5] if len(args) >= 6 else "")
        date_of_birth = kwargs.get("date_of_birth", "")
        email = kwargs.get("email", "")
        glucose = kwargs.get("glucose")
        haemoglobin = kwargs.get("haemoglobin")
        cholesterol = kwargs.get("cholesterol")
        remarks = kwargs.get("remarks", "")
    else:
        legacy_args = args[:6]
        if len(legacy_args) < 6:
            raise ValueError("Legacy patient data requires date_of_birth, email, glucose, haemoglobin, cholesterol, and remarks.")

        date_of_birth, email, glucose, haemoglobin, cholesterol, remarks = legacy_args
        age = kwargs.get("age")
        gender = kwargs.get("gender", "Other")
        height = kwargs.get("height", 0.0)
        weight = kwargs.get("weight", 0.0)
        blood_group = kwargs.get("blood_group", "")
        phone = kwargs.get("phone", "")

    cursor.execute(
        """
        INSERT INTO patients (
            full_name,
            age,
            gender,
            height,
            weight,
            blood_group,
            phone,
            date_of_birth,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            full_name,
            age,
            gender,
            height,
            weight,
            blood_group,
            phone,
            date_of_birth,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks,
            current_time,
            current_time,
        ),
    )

    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return patient_id


def get_all_patients():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *, id AS patient_id
        FROM patients
        ORDER BY id ASC
        """
    )

    patients = [_normalize_patient_row(dict(row)) for row in cursor.fetchall()]
    conn.close()
    return patients


def get_patient_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def search_patient(search_term):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    term = f"%{search_term.strip()}%"
    cursor.execute(
        """
        SELECT *, id AS patient_id
        FROM patients
        WHERE lower(full_name) LIKE lower(?)
           OR CAST(id AS TEXT) LIKE ?
        ORDER BY id ASC
        """,
        (term, term),
    )

    patients = [_normalize_patient_row(dict(row)) for row in cursor.fetchall()]
    conn.close()
    return patients


def save_blood_report(patient_id, file_name, processed_df):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS blood_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            report_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """
    )

    report_payload = json.dumps(processed_df.to_dict(orient="records"))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO blood_reports (patient_id, file_name, report_data, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (patient_id, file_name, report_payload, current_time),
    )

    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id

def update_patient(
    patient_id,
    full_name,
    date_of_birth,
    email,
    glucose,
    haemoglobin,
    cholesterol,
    remarks
):

    if is_patient_name_duplicate(full_name, exclude_patient_id=patient_id):
        return False

    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE patients
        SET
            full_name = ?,
            date_of_birth = ?,
            email = ?,
            glucose = ?,
            haemoglobin = ?,
            cholesterol = ?,
            remarks = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        full_name,
        date_of_birth,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks,
        current_time,
        patient_id
    ))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated


def delete_patient(patient_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("BEGIN")

        cursor.execute(
            "DELETE FROM patients WHERE id = ?",
            (patient_id,),
        )
        deleted = cursor.rowcount > 0

        if deleted:
            cursor.execute(
                "DELETE FROM blood_reports WHERE patient_id = ?",
                (patient_id,),
            )

            cursor.execute(
                """
                CREATE TEMP TABLE patient_id_renumber_map (
                    old_id INTEGER PRIMARY KEY,
                    shifted_id INTEGER NOT NULL,
                    new_id INTEGER NOT NULL
                )
                """
            )

            max_id = cursor.execute(
                "SELECT COALESCE(MAX(id), 0) FROM patients"
            ).fetchone()[0]
            offset = max_id + 1

            cursor.execute(
                """
                INSERT INTO patient_id_renumber_map (old_id, shifted_id, new_id)
                SELECT id, id + ?, ROW_NUMBER() OVER (ORDER BY id ASC)
                FROM patients
                """,
                (offset,),
            )

            cursor.execute(
                """
                UPDATE blood_reports
                SET patient_id = patient_id + ?
                WHERE patient_id IN (
                    SELECT old_id FROM patient_id_renumber_map
                )
                """,
                (offset,),
            )
            cursor.execute(
                "UPDATE patients SET id = id + ?",
                (offset,),
            )
            cursor.execute(
                """
                UPDATE patients
                SET id = (
                    SELECT new_id
                    FROM patient_id_renumber_map
                    WHERE shifted_id = patients.id
                )
                """
            )
            cursor.execute(
                """
                UPDATE blood_reports
                SET patient_id = (
                    SELECT new_id
                    FROM patient_id_renumber_map
                    WHERE shifted_id = blood_reports.patient_id
                )
                WHERE patient_id IN (
                    SELECT shifted_id FROM patient_id_renumber_map
                )
                """
            )
            cursor.execute(
                """
                UPDATE sqlite_sequence
                SET seq = (SELECT COALESCE(MAX(id), 0) FROM patients)
                WHERE name = 'patients'
                """
            )

        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_patient_by_id(patient_id):

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    patient = cursor.fetchone()

    conn.close()

    return dict(patient) if patient else None

import psycopg2
from pathlib import Path
#from credentials import DB_CONFIG
from settings import DB_CONFIG

CSV_FILES = {
    'records_group': 'records_group.csv',
    'records_record': 'records_record.csv',
    'records_image': 'records_image.csv'
}

def import_csv_to_table(cursor, table_name, csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        cursor.copy_expert(
            f"COPY {table_name} FROM STDIN WITH CSV",
            f
        )
        print(f"Imported {csv_path} → {table_name}")

def main(csv_dir):
    csv_dir = Path(csv_dir)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        for table, csv_file in CSV_FILES.items():
            full_path = csv_dir / csv_file
            if full_path.exists():
                import_csv_to_table(cursor, table, full_path)
            else:
                print(f"⚠️ File not found: {full_path}")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during import: {e}")
    finally:
        cursor.close()
        conn.close()
        print("✅ Done.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python update_db.py /path/to/csv_folder")
    else:
        main(sys.argv[1])

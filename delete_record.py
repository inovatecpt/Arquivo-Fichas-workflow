import psycopg2
from credentials import DB_CONFIG

def delete_record_by_id(record_id):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            try:
                # ✅ Check if record exists
                cur.execute("SELECT 1 FROM records_record WHERE id = %s", (record_id,))
                if cur.fetchone() is None:
                    print(f"❌ Record ID {record_id} does not exist.")
                    return

                # ✅ Check how many images are linked to this record
                cur.execute("SELECT COUNT(*) FROM records_image WHERE record_id = %s", (record_id,))
                image_count = cur.fetchone()[0]

                if image_count > 0:
                    print(f"🖼️  This record has {image_count} image(s) associated.")
                    confirm = input("Are you sure you want to delete this record and all its images? (yes/no): ")
                    if confirm.strip().lower() != 'yes':
                        print("❎ Aborting deletion.")
                        return

                print(f"🔍 Deleting record ID: {record_id} and associated images...")

                # ✅ Delete associated images first
                cur.execute("DELETE FROM records_image WHERE record_id = %s", (record_id,))
                print("🗑️  Deleted associated images")

                # ✅ Then delete the record
                cur.execute("DELETE FROM records_record WHERE id = %s", (record_id,))
                print("🗑️  Deleted record")

                print("✅ Record and images deleted successfully.")

            except Exception as e:
                conn.rollback()
                print(f"❌ Error during deletion: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python delete_record.py <record_id>")
        sys.exit(1)

    try:
        record_id = int(sys.argv[1])
    except ValueError:
        print("Record ID must be an integer.")
        sys.exit(1)

    delete_record_by_id(record_id)


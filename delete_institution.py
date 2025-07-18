import psycopg2
from credentials import DB_CONFIG

def delete_institution_by_id(institution_id):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            try:
                # ✅ Check if institution exists
                cur.execute("SELECT name FROM records_institution WHERE id = %s", (institution_id,))
                row = cur.fetchone()
                if row is None:
                    print(f"❌ Institution ID {institution_id} does not exist.")
                    return

                institution_name = row[0]
                print(f"🏛️  Found institution: {institution_name} (ID: {institution_id})")

                # ✅ Check for associated collections
                cur.execute("SELECT id FROM records_collection WHERE institution_id = %s", (institution_id,))
                collection_ids = [row[0] for row in cur.fetchall()]

                if collection_ids:
                    print(f"⚠️  This institution is linked to {len(collection_ids)} collection(s).")
                    confirm = input("Do you want to delete the institution and ALL related collections, groups, records, and images? (yes/no): ")
                    if confirm.strip().lower() != 'yes':
                        print("❎ Aborting deletion.")
                        return

                    print("🔄 Performing cascading deletion...")

                    for collection_id in collection_ids:
                        # Delete images linked to records in this collection
                        cur.execute("""
                            DELETE FROM records_image
                            WHERE record_id IN (
                                SELECT rr.id
                                FROM records_record rr
                                JOIN records_group rg ON rr.group_id = rg.id
                                WHERE rg.collection_id = %s
                            )
                        """, (collection_id,))

                        # Delete records
                        cur.execute("""
                            DELETE FROM records_record
                            WHERE group_id IN (
                                SELECT id FROM records_group WHERE collection_id = %s
                            )
                        """, (collection_id,))

                        # Delete groups
                        cur.execute("DELETE FROM records_group WHERE collection_id = %s", (collection_id,))

                        # Delete collection
                        cur.execute("DELETE FROM records_collection WHERE id = %s", (collection_id,))

                    print(f"🗑️  Deleted {len(collection_ids)} collection(s) and all nested data.")

                # ✅ Delete institution
                cur.execute("DELETE FROM records_institution WHERE id = %s", (institution_id,))
                print("✅ Institution deleted successfully.")

            except Exception as e:
                conn.rollback()
                print(f"❌ Error during deletion: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python delete_institution.py <institution_id>")
        sys.exit(1)

    try:
        institution_id = int(sys.argv[1])
    except ValueError:
        print("Institution ID must be an integer.")
        sys.exit(1)

    delete_institution_by_id(institution_id)

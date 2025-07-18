import psycopg2
from credentials import DB_CONFIG


def delete_group(group_id):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            try:
                # Check if group exists
                cur.execute("SELECT name FROM records_group WHERE id = %s", (group_id,))
                result = cur.fetchone()
                if not result:
                    print(f"❌ Group ID {group_id} does not exist.")
                    return

                group_name = result[0]
                print(f"📦 Found group: {group_name} (ID: {group_id})")

                # Check if there are records in the group
                cur.execute("SELECT COUNT(*) FROM records_record WHERE group_id = %s", (group_id,))
                record_count = cur.fetchone()[0]

                if record_count > 0:
                    print(f"⚠️  This group contains {record_count} record(s).")
                    confirm = input("Are you sure you want to delete this group and all its data? (yes/no): ")
                    if confirm.strip().lower() != 'yes':
                        print("❎ Aborting deletion.")
                        return

                print(f"🔍 Deleting group: {group_id}")

                # Delete images
                cur.execute("""
                    DELETE FROM records_image
                    WHERE record_id IN (
                        SELECT id FROM records_record
                        WHERE group_id = %s
                    )
                """, (group_id,))
                print("🗑️  Deleted related images")

                # Delete records
                cur.execute("""
                    DELETE FROM records_record
                    WHERE group_id = %s
                """, (group_id,))
                print("🗑️  Deleted related records")

                # Delete group
                cur.execute("""
                    DELETE FROM records_group
                    WHERE id = %s
                """, (group_id,))
                print("🗑️  Deleted group")

                print("✅ Deletion complete.")
            except Exception as e:
                conn.rollback()
                print(f"❌ Error during deletion: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python delete_group.py <group_id>")
        sys.exit(1)

    group_id = sys.argv[1]
    delete_group(group_id)

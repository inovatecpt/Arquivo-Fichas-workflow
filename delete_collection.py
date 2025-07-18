import psycopg2
#from credentials import DB_CONFIG
from settings import DB_CONFIG


def delete_collection_by_id(collection_id):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            try:
                # Check if the collection exists
                cur.execute("SELECT name FROM records_collection WHERE id = %s", (collection_id,))
                result = cur.fetchone()
                if not result:
                    print(f"Collection ID {collection_id} does not exist.")
                    return

                collection_name = result[0]
                print(f"Collection found: {collection_name}")

                # Check if there are any groups in the collection
                cur.execute("SELECT COUNT(*) FROM records_group WHERE collection_id = %s", (collection_id,))
                group_count = cur.fetchone()[0]

                if group_count > 0:
                    print(f"There are {group_count} group(s) in collection ID {collection_id}.")
                    confirm = input("Are you sure you want to delete this collection and all related data? (yes/no): ")
                    if confirm.strip().lower() != 'yes':
                        print("Aborting deletion.")
                        return

                print(f"Deleting data for collection ID: {collection_id}")

                # Delete in dependency order
                cur.execute("""
                    DELETE FROM records_image
                    WHERE record_id IN (
                        SELECT rr.id
                        FROM records_record rr
                        JOIN records_group rg ON rr.group_id = rg.id
                        WHERE rg.collection_id = %s
                    )
                """, (collection_id,))

                cur.execute("""
                    DELETE FROM records_record
                    WHERE group_id IN (
                        SELECT id FROM records_group WHERE collection_id = %s
                    )
                """, (collection_id,))

                cur.execute("DELETE FROM records_group WHERE collection_id = %s", (collection_id,))
                cur.execute("DELETE FROM records_collection WHERE id = %s", (collection_id,))

                print("Deletion completed successfully.")

            except Exception as e:
                conn.rollback()
                print(f"Error during deletion: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python delete_collection.py <collection_id>")
        sys.exit(1)

    try:
        collection_id = int(sys.argv[1])
    except ValueError:
        print("Collection ID must be an integer.")
        sys.exit(1)

    delete_collection_by_id(collection_id)
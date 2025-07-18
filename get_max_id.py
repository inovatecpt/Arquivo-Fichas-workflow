import psycopg2
import sys
from credentials import DB_CONFIG


def get_highest_ids(table):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = f"SELECT MAX(id) FROM {table};"
        cur.execute(query)
        max_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return max_id
    except Exception as e:
        print(f"Error: {e}")
        return None

def collection_exists(collection_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = "SELECT EXISTS (SELECT 1 FROM records_collection WHERE id = %s);"
        cur.execute(query, (collection_id,))
        exists = cur.fetchone()[0]
        cur.close()
        conn.close()
        return exists
    except Exception as e:
        print(f"Error checking collection existence: {e}")
        return False

# Allow optional CLI test
if __name__ == "__main__":
    if len(sys.argv) == 2:
        table_name = sys.argv[1]
        max_id = get_highest_ids(table_name)
        if max_id is not None:
            print(f"Highest ID in table '{table_name}': {max_id}")
        else:
            print(f"Could not retrieve highest ID for table '{table_name}'.")
    elif len(sys.argv) == 3 and sys.argv[1] == "--check-collection":
        try:
            collection_id = int(sys.argv[2])
            if collection_exists(collection_id):
                print(f"Collection with ID {collection_id} exists.")
            else:
                print(f"Collection with ID {collection_id} does NOT exist.")
        except ValueError:
            print("Collection ID must be an integer.")
    else:
        print("Usage:")
        print("  python get_max_id.py <table_name>")
        print("  python get_max_id.py --check-collection <collection_id>")
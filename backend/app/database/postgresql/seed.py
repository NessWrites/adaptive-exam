import psycopg2
import os
import re
from io import StringIO

def run_seed():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.autocommit = True  # each statement runs independently
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]

    if count == 0:
        print("Seeding database...")
        with open("quiz_database.sql", "r") as f:
            sql = f.read()

        # extract COPY blocks before anything else
        copy_pattern = re.compile(
            r"COPY\s+\S+\s+\([^)]+\)\s+FROM stdin;\n(.*?)\\\.",
            re.DOTALL
        )
        copy_headers = re.compile(
            r"(COPY\s+\S+\s+\([^)]+\)\s+FROM stdin;)\n(.*?)\\\.",
            re.DOTALL
        )

        copy_blocks = copy_headers.findall(sql)

        # remove COPY blocks from sql
        remaining_sql = copy_pattern.sub('', sql)

        # remove comment lines
        lines = remaining_sql.splitlines()
        clean_lines = [
            line for line in lines
            if not line.strip().startswith('--')
            and line.strip() != ''
        ]
        remaining_sql = '\n'.join(clean_lines)

        # only run setval statements
        for line in remaining_sql.splitlines():
            line = line.strip()
            if line.lower().startswith('select pg_catalog.setval'):
                try:
                    cursor.execute(line)
                except Exception as e:
                    print(f"setval error: {e}")

        # run COPY blocks
        for header, data in copy_blocks:
            try:
                cursor.copy_expert(header, StringIO(data))
                print(f"Loaded: {header[:60]}")
            except Exception as e:
                print(f"COPY error: {e}")

        print("Seeding complete.")
    else:
        print("Database already seeded, skipping.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_seed()
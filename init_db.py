import sqlite3


def main():
    with open("schema.sql", "r") as f:
        schema = f.read()

    conn = sqlite3.connect("hw13.db")
    conn.executescript(schema)
    conn.commit()
    conn.close()

    print("hw13.db created successfully.")


if __name__ == "__main__":
    main()
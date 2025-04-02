from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Get the absolute path of the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "users.db")

mcp = FastMCP("User Management")

@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect(db_path)
    try:
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table'"
        ).fetchall()
        return "\n".join(sql[0] for sql in schema if sql[0])
    except Exception as e:
        print(f"Schema error: {e}")
        return f"Error retrieving schema: {e}"
    finally:
        conn.close()

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect(db_path)
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

@mcp.tool()
def add_user(name: str, city: str) -> str:
    """Insert a new user with name and city"""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO users (name, city) VALUES (?, ?)",
            (name, city)
        )
        conn.commit()
        return f"User '{name}' from '{city}' added successfully."
    except Exception as e:
        return f"Error adding user: {str(e)}"
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting server")
    # Create the database and table if needed
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT
        )
    """)
    conn.close()

    mcp.run()

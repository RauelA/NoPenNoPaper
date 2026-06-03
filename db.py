import sqlite3
import os
import re

DB_FILE = os.path.join(os.path.dirname(__file__), 'game.db')

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Abilities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Abilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        health REAL DEFAULT 100.0,
        strength REAL DEFAULT 10.0,
        agility REAL DEFAULT 10.0,
        dexterity REAL DEFAULT 10.0,
        charisma REAL DEFAULT 10.0,
        focus REAL DEFAULT 10.0
    );
    """)
    
    # 2. Extras Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Extras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        languages TEXT DEFAULT 'Deutsch'
    );
    """)
    
    # 3. Inventory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT
    );
    """)
    
    # 4. Appearance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Appearance (
        id INTEGER PRIMARY KEY AUTOINCREMENT
    );
    """)
    
    # 5. Characters Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        abilities_id INTEGER UNIQUE NOT NULL,
        extras_id INTEGER UNIQUE NOT NULL,
        inventory_id INTEGER UNIQUE NOT NULL,
        appearance_id INTEGER UNIQUE NOT NULL,
        FOREIGN KEY (abilities_id) REFERENCES Abilities(id) ON DELETE CASCADE,
        FOREIGN KEY (extras_id) REFERENCES Extras(id) ON DELETE CASCADE,
        FOREIGN KEY (inventory_id) REFERENCES Inventory(id) ON DELETE CASCADE,
        FOREIGN KEY (appearance_id) REFERENCES Appearance(id) ON DELETE CASCADE
    );
    """)
    
    # 6. Locations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        biome TEXT DEFAULT 'Forest',
        population INTEGER DEFAULT 0,
        politics TEXT DEFAULT 'None',
        appearance TEXT DEFAULT ''
    );
    """)
    
    # 7. Objects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Objects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        durability REAL DEFAULT 100.0,
        owner TEXT DEFAULT 'None',
        appearance TEXT DEFAULT '',
        contents_id INTEGER,
        FOREIGN KEY (contents_id) REFERENCES Objects(id) ON DELETE SET NULL
    );
    """)
    
    # 8. World Local Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS World_Local (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weather TEXT DEFAULT 'Sunny',
        inventory_id INTEGER,
        appearance TEXT DEFAULT '',
        FOREIGN KEY (inventory_id) REFERENCES Inventory(id) ON DELETE SET NULL
    );
    """)
    
    # 9. World Global Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS World_Global (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        physics TEXT DEFAULT 'Standard Earth Physics',
        magic TEXT DEFAULT 'None',
        appearance TEXT DEFAULT ''
    );
    """)
    
    conn.commit()
    conn.close()

def add_column_to_table(table_name, column_name, column_type="TEXT"):
    """
    Dynamically adds a column to Extras, Inventory, or Appearance.
    Uses strict sanitization to prevent SQL Injection.
    """
    allowed_tables = ["Extras", "Inventory", "Appearance"]
    if table_name not in allowed_tables:
        raise ValueError(f"Tabelle '{table_name}' kann nicht dynamisch erweitert werden.")
    
    # Validate column name: alphanumeric and underscores only
    if not re.match(r"^[a-zA-Z0-9_]+$", column_name):
        raise ValueError("Ungültiger Spaltenname. Nur alphanumerische Zeichen und Unterstriche erlaubt.")
        
    allowed_types = ["TEXT", "INTEGER", "REAL"]
    if column_type not in allowed_types:
        raise ValueError(f"Ungültiger Datentyp: {column_type}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_cols = [row[1].lower() for row in cursor.fetchall()]
    
    if column_name.lower() in existing_cols:
        conn.close()
        raise ValueError(f"Spalte '{column_name}' existiert bereits in der Tabelle '{table_name}'.")
    
    # SQLite ALTER TABLE is safe with validated identifiers
    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
    conn.commit()
    conn.close()
    return True

def get_tables_schema():
    """
    Returns lists of columns and their types for all tables in the database.
    """
    tables = [
        "Characters", "Abilities", "Extras", "Inventory", "Appearance",
        "Locations", "Objects", "World_Local", "World_Global"
    ]
    schema = {}
    conn = get_connection()
    cursor = conn.cursor()
    
    for t in tables:
        cursor.execute(f"PRAGMA table_info({t})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[1],
                "type": row[2],
                "pk": bool(row[5])
            })
        schema[t] = columns
        
    conn.close()
    return schema

def get_table_data(table_name):
    """
    Fetches all records from a table.
    """
    # Strict validation of table name
    allowed_tables = [
        "Characters", "Abilities", "Extras", "Inventory", "Appearance",
        "Locations", "Objects", "World_Local", "World_Global"
    ]
    if table_name not in allowed_tables:
        raise ValueError("Ungültige Tabelle.")
        
    conn = get_connection()
    cursor = conn.cursor()
    
    if table_name == 'Characters':
        # Join character sub-tables for a rich complete view
        cursor.execute("""
            SELECT 
                c.id, c.name,
                a.health, a.strength, a.agility, a.dexterity, a.charisma, a.focus,
                e.languages,
                c.abilities_id, c.extras_id, c.inventory_id, c.appearance_id
            FROM Characters c
            JOIN Abilities a ON c.abilities_id = a.id
            JOIN Extras e ON c.extras_id = e.id
        """)
        # We also need to fetch extras, inventory, appearance row data dynamically
        # because those columns are extendable!
        # To make it simple, we retrieve characters normally, then query dynamic values.
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def insert_row(table_name, data):
    """
    Inserts a row into table_name.
    For complex entities like Characters, handles the auto-creation of nested tables.
    """
    allowed_tables = [
        "Characters", "Abilities", "Extras", "Inventory", "Appearance",
        "Locations", "Objects", "World_Local", "World_Global"
    ]
    if table_name not in allowed_tables:
        raise ValueError("Ungültige Tabelle.")
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if table_name == "Characters":
            # 1. Insert Abilities
            ab_data = data.get('abilities', {})
            cursor.execute("""
                INSERT INTO Abilities (health, strength, agility, dexterity, charisma, focus)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ab_data.get('health', 100.0),
                ab_data.get('strength', 10.0),
                ab_data.get('agility', 10.0),
                ab_data.get('dexterity', 10.0),
                ab_data.get('charisma', 10.0),
                ab_data.get('focus', 10.0)
            ))
            abilities_id = cursor.lastrowid
            
            # 2. Insert Extras (with dynamic columns)
            ex_data = data.get('extras', {})
            # Find current columns of Extras
            cursor.execute("PRAGMA table_info(Extras)")
            ex_cols = [row[1] for row in cursor.fetchall() if row[1] != 'id']
            
            ex_keys = []
            ex_vals = []
            for col in ex_cols:
                if col in ex_data:
                    ex_keys.append(col)
                    ex_vals.append(ex_data[col])
            
            if ex_keys:
                placeholders = ', '.join(['?'] * len(ex_keys))
                cursor.execute(f"""
                    INSERT INTO Extras ({', '.join(ex_keys)})
                    VALUES ({placeholders})
                """, ex_vals)
            else:
                cursor.execute("INSERT INTO Extras DEFAULT VALUES")
            extras_id = cursor.lastrowid
            
            # 3. Insert Inventory (with dynamic columns)
            inv_data = data.get('inventory', {})
            cursor.execute("PRAGMA table_info(Inventory)")
            inv_cols = [row[1] for row in cursor.fetchall() if row[1] != 'id']
            
            inv_keys = []
            inv_vals = []
            for col in inv_cols:
                if col in inv_data:
                    inv_keys.append(col)
                    inv_vals.append(inv_data[col])
            
            if inv_keys:
                placeholders = ', '.join(['?'] * len(inv_keys))
                cursor.execute(f"""
                    INSERT INTO Inventory ({', '.join(inv_keys)})
                    VALUES ({placeholders})
                """, inv_vals)
            else:
                cursor.execute("INSERT INTO Inventory DEFAULT VALUES")
            inventory_id = cursor.lastrowid
            
            # 4. Insert Appearance (with dynamic columns)
            app_data = data.get('appearance', {})
            cursor.execute("PRAGMA table_info(Appearance)")
            app_cols = [row[1] for row in cursor.fetchall() if row[1] != 'id']
            
            app_keys = []
            app_vals = []
            for col in app_cols:
                if col in app_data:
                    app_keys.append(col)
                    app_vals.append(app_data[col])
            
            if app_keys:
                placeholders = ', '.join(['?'] * len(app_keys))
                cursor.execute(f"""
                    INSERT INTO Appearance ({', '.join(app_keys)})
                    VALUES ({placeholders})
                """, app_vals)
            else:
                cursor.execute("INSERT INTO Appearance DEFAULT VALUES")
            appearance_id = cursor.lastrowid
            
            # 5. Insert Character
            cursor.execute("""
                INSERT INTO Characters (name, abilities_id, extras_id, inventory_id, appearance_id)
                VALUES (?, ?, ?, ?, ?)
            """, (data.get('name', 'Unbenannter Charakter'), abilities_id, extras_id, inventory_id, appearance_id))
            
        else:
            # Standard single table insertion
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols = [row[1] for row in cursor.fetchall() if row[1] != 'id']
            
            keys = []
            vals = []
            for col in cols:
                if col in data:
                    keys.append(col)
                    vals.append(data[col])
            
            if keys:
                placeholders = ', '.join(['?'] * len(keys))
                query = f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({placeholders})"
                cursor.execute(query, vals)
            else:
                cursor.execute(f"INSERT INTO {table_name} DEFAULT VALUES")
                
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

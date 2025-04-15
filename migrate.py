import sqlite3
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite database file
SQLITE_DB_PATH = 'database.db'

# PostgreSQL connection parameters
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST', 'localhost')


def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_postgres_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn


def migrate_data():
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()

    try:
        sqlite_cursor = sqlite_conn.cursor()
        postgres_cursor = postgres_conn.cursor()

        # Start a transaction
        postgres_conn.autocommit = False

        # Migrate data in order respecting foreign key constraints

        # Migrate 'cuisine' table
        print("Migrating 'cuisine' table...")
        sqlite_cursor.execute('SELECT * FROM "cuisine";')
        cuisines = sqlite_cursor.fetchall()
        for cuisine in cuisines:
            postgres_cursor.execute('''
                INSERT INTO "cuisine" ("Cuisine_ID")
                VALUES (%s)
                ON CONFLICT DO NOTHING
            ''', (cuisine['Cuisine_ID'],))

        # Migrate 'account' table
        print("Migrating 'account' table...")
        sqlite_cursor.execute('SELECT * FROM "account";')
        accounts = sqlite_cursor.fetchall()
        for account in accounts:
            postgres_cursor.execute('''
                INSERT INTO "account" ("id", "username", "email", "password")
                VALUES (%s, %s, %s, %s)
            ''', (account['id'], account['username'], account['email'], account['password']))

        # Migrate 'users' table
        print("Migrating 'users' table...")
        sqlite_cursor.execute('SELECT * FROM "users";')
        users = sqlite_cursor.fetchall()
        for user in users:
            postgres_cursor.execute('''
                INSERT INTO "users" ("Account_ID")
                VALUES (%s)
            ''', (user['Account_ID'],))

        # Migrate 'admin' table
        print("Migrating 'admin' table...")
        sqlite_cursor.execute('SELECT * FROM "admin";')
        admins = sqlite_cursor.fetchall()
        for admin in admins:
            postgres_cursor.execute('''
                INSERT INTO "admin" ("Account_ID", "admin_name")
                VALUES (%s, %s)
            ''', (admin['Account_ID'], admin['admin_name']))

        # Migrate 'regional_cuisine' table
        print("Migrating 'regional_cuisine' table...")
        sqlite_cursor.execute('SELECT * FROM "regional_cuisine";')
        regional_cuisines = sqlite_cursor.fetchall()
        for rc in regional_cuisines:
            postgres_cursor.execute('''
                INSERT INTO "regional_cuisine" ("region_desc", "Cuisine_ID")
                VALUES (%s, %s)
            ''', (rc['region_desc'], rc['Cuisine_ID']))

        # Migrate 'cuisine_type' table
        print("Migrating 'cuisine_type' table...")
        sqlite_cursor.execute('SELECT * FROM "cuisine_type";')
        cuisine_types = sqlite_cursor.fetchall()
        for ct in cuisine_types:
            postgres_cursor.execute('''
                INSERT INTO "cuisine_type" ("type_description", "Cuisine_ID")
                VALUES (%s, %s)
            ''', (ct['type_description'], ct['Cuisine_ID']))

        # Migrate 'recipe' table
        print("Migrating 'recipe' table...")
        sqlite_cursor.execute('SELECT * FROM "recipe";')
        recipes = sqlite_cursor.fetchall()
        for recipe in recipes:
            postgres_cursor.execute('''
                INSERT INTO "recipe" ("recipe_id", "recipe_name", "Cuisine_ID", "UserID", "recipe_description",
                                      "prep_time", "cook_time", "recipe_image", "instructions")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                recipe['recipe_id'], recipe['recipe_name'], recipe['Cuisine_ID'], recipe['UserID'],
                recipe['recipe_description'], recipe['prep_time'], recipe['cook_time'],
                recipe['recipe_image'], recipe['instructions']
            ))

        # Migrate 'recipe_restrictions' table
        print("Migrating 'recipe_restrictions' table...")
        sqlite_cursor.execute('SELECT * FROM "recipe_restrictions";')
        recipe_restrictions = sqlite_cursor.fetchall()
        for rr in recipe_restrictions:
            postgres_cursor.execute('''
                INSERT INTO "recipe_restrictions" ("recipe_name", "RecRestriction")
                VALUES (%s, %s)
            ''', (rr['recipe_name'], rr['RecRestriction']))

        # Migrate 'ingredients' table
        print("Migrating 'ingredients' table...")
        sqlite_cursor.execute('SELECT * FROM "ingredients";')
        ingredients = sqlite_cursor.fetchall()
        for ingredient in ingredients:
            postgres_cursor.execute('''
                INSERT INTO "ingredients" ("recipe_name", "ingredient_name")
                VALUES (%s, %s)
            ''', (ingredient['recipe_name'], ingredient['ingredient_name']))

        # Migrate 'user_restrictions' table
        print("Migrating 'user_restrictions' table...")
        sqlite_cursor.execute('SELECT * FROM "user_restrictions";')
        user_restrictions = sqlite_cursor.fetchall()
        for ur in user_restrictions:
            postgres_cursor.execute('''
                INSERT INTO "user_restrictions" ("User_ID", "UserRestriction")
                VALUES (%s, %s)
            ''', (ur['User_ID'], ur['UserRestriction']))

        # Migrate 'cookbook' table
        print("Migrating 'cookbook' table...")
        sqlite_cursor.execute('SELECT * FROM "cookbook";')
        cookbooks = sqlite_cursor.fetchall()
        for cookbook in cookbooks:
            postgres_cursor.execute('''
                INSERT INTO "cookbook" ("CookBook_ID")
                VALUES (%s)
            ''', (cookbook['CookBook_ID'],))

        # Migrate 'contains' table
        print("Migrating 'contains' table...")
        sqlite_cursor.execute('SELECT * FROM "contains";')
        contains = sqlite_cursor.fetchall()
        for c in contains:
            postgres_cursor.execute('''
                INSERT INTO "contains" ("CookBook_ID", "recipe_name")
                VALUES (%s, %s)
            ''', (c['CookBook_ID'], c['recipe_name']))

        # Migrate 'rates' table
        print("Migrating 'rates' table...")
        sqlite_cursor.execute('SELECT * FROM "rates";')
        rates = sqlite_cursor.fetchall()
        for rate in rates:
            postgres_cursor.execute('''
                INSERT INTO "rates" ("User_ID", "recipe_name", "user_rating")
                VALUES (%s, %s, %s)
            ''', (rate['User_ID'], rate['recipe_name'], rate['user_rating']))

        # Commit all changes
        postgres_conn.commit()
        print("Data migration completed successfully!")

    except Exception as e:
        postgres_conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        sqlite_conn.close()
        postgres_conn.close()


if __name__ == '__main__':
    migrate_data()

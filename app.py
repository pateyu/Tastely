from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import psycopg2
import psycopg2.extras
import os
import urllib.parse
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
# need to update spoonacular api
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/images'

# PostgreSQL connection parameters
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST', 'localhost')

ALL_TAGS = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free']

if not all([DB_NAME, DB_USER, DB_PASS, DB_HOST]):
    raise Exception("Database configuration not fully set in environment variables")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn


def init_db():
    print(f"DB_NAME: {DB_NAME}")
    print(f"DB_USER: {DB_USER}")
    print(f"DB_PASS: {DB_PASS}")
    print(f"DB_HOST: {DB_HOST}")

    with app.app_context():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            with open('setup.sql', 'r') as f:
                sql = f.read()
                statements = sql.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
            conn.commit()

            # Reset sequences to prevent primary key conflicts
            cursor.execute('''
                SELECT setval(pg_get_serial_sequence('"account"', 'id'), COALESCE(MAX("id"), 1), false) FROM "account";
                SELECT setval(pg_get_serial_sequence('"recipe"', 'recipe_id'), COALESCE(MAX("recipe_id"), 1), false) FROM "recipe";
            ''')
            conn.commit()
        conn.close()


def slugify(text):
    return urllib.parse.quote_plus(text.lower().replace(" ", "-"))


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        email = data['email']
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if username or email already exists
                cursor.execute('SELECT 1 FROM "account" WHERE "username" = %s OR "email" = %s', (username, email))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Username or email already exists'}), 409

                # Insert into account table
                cursor.execute('INSERT INTO "account" ("username", "email", "password") VALUES (%s, %s, %s) RETURNING "id"',
                               (username, email, password))
                account_id = cursor.fetchone()[0]

                # Insert into users table
                cursor.execute('INSERT INTO "users" ("Account_ID") VALUES (%s)', (account_id,))
                conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            # Log the error message for debugging
            print(f"Database error during signup: {e}")
            return jsonify({'success': False, 'message': 'An error occurred during signup'}), 500
        finally:
            conn.close()
        return jsonify({'success': True, 'message': 'User created successfully'})
    return render_template('signup.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                'SELECT * FROM "account" WHERE "username" = %s AND "password" = %s', (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['id']
                cursor.execute(
                    'SELECT * FROM "admin" WHERE "Account_ID" = %s', (user['id'],))
                admin_check = cursor.fetchone()
                session['is_admin'] = bool(admin_check)
                return jsonify({'message': 'Login successful', 'redirect': url_for('dashboard')}), 200
            else:
                return jsonify({'message': 'Login failed'}), 401
    except psycopg2.Error as e:
        print(f"Database error during login: {e}")
        return jsonify({'message': 'An error occurred during login'}), 500
    finally:
        conn.close()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    search_query = request.args.get('search', '')
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            if search_query:
                cursor.execute(
                    'SELECT * FROM "recipe" WHERE "recipe_name" ILIKE %s', ('%' + search_query + '%',))
            else:
                cursor.execute('SELECT * FROM "recipe"')
            recipes = cursor.fetchall()
            return render_template('dashboard.html', recipes=recipes)
    except psycopg2.Error as e:
        print(f"Database error during dashboard retrieval: {e}")
        return 'An error occurred', 500
    finally:
        conn.close()


@app.route('/create-recipe', methods=['GET', 'POST'])
def create_recipe():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        if request.method == 'POST':
            recipe_name = request.form['recipe_name']
            description = request.form['description']
            prep_time = request.form['prep_time']
            cook_time = request.form['cook_time']
            ingredients = request.form['ingredients']
            instructions = request.form['instructions']
            cuisine_type = request.form['cuisine_type']
            user_id = session.get('user_id', 1)
            tags = request.form.getlist('tags[]')

            file = request.files['recipe_image']
            filename = secure_filename(file.filename) if file else None
            if filename and allowed_file(filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            else:
                file_path = None

            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO "recipe" ("recipe_name", "recipe_description", "Cuisine_ID", "UserID", "prep_time", "cook_time", "recipe_image", "instructions")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (recipe_name, description, cuisine_type, user_id, prep_time, cook_time, file_path, instructions))

                ingredient_list = ingredients.split(',')
                for ingredient in ingredient_list:
                    cursor.execute('''
                        INSERT INTO "ingredients" ("recipe_name", "ingredient_name")
                        VALUES (%s, %s)
                    ''', (recipe_name, ingredient.strip()))

                for tag in tags:
                    cursor.execute('''
                        INSERT INTO "recipe_restrictions" ("recipe_name", "RecRestriction")
                        VALUES (%s, %s)
                    ''', (recipe_name, tag))

                conn.commit()
            return redirect(url_for('view_recipe', slug=slugify(recipe_name)))
        else:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('SELECT * FROM "cuisine"')
                cuisines = cursor.fetchall()
                return render_template('create_recipe.html', cuisines=cuisines)
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during recipe creation: {e}")
        return jsonify({'error': 'Failed to insert recipe into database', 'details': str(e)}), 500
    finally:
        conn.close()


@app.route('/recipe/<slug>')
def view_recipe(slug):
    conn = get_db_connection()
    try:
        recipe_title = slug.replace("-", " ")
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                'SELECT * FROM "recipe" WHERE "recipe_name" = %s', (recipe_title,))
            recipe = cursor.fetchone()
            if recipe:
                cursor.execute(
                    'SELECT "ingredient_name" FROM "ingredients" WHERE "recipe_name" = %s', (recipe_title,))
                ingredients = cursor.fetchall()

                cursor.execute(
                    'SELECT "RecRestriction" FROM "recipe_restrictions" WHERE "recipe_name" = %s', (recipe_title,))
                tags = cursor.fetchall()

                cursor.execute('SELECT AVG("user_rating") AS avg_rating, COUNT(*) AS rating_count FROM "rates" WHERE "recipe_name" = %s',
                               (recipe_title,))
                rating_result = cursor.fetchone()
                avg_rating = float(
                    rating_result['avg_rating']) if rating_result['avg_rating'] is not None else 0
                rating_count = rating_result['rating_count']

                return render_template('recipe.html', recipe=recipe, ingredients=ingredients, tags=tags, avg_rating=avg_rating, rating_count=rating_count)
            else:
                return 'Recipe not found', 404
    except psycopg2.Error as e:
        print(f"Database error during recipe retrieval: {e}")
        return 'An error occurred', 500
    finally:
        conn.close()


@app.route('/edit-recipe/<slug>', methods=['GET', 'POST'])
def edit_recipe(slug):
    conn = get_db_connection()
    try:
        recipe_title = slug.replace("-", " ")
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                'SELECT * FROM "recipe" WHERE "recipe_name" = %s', (recipe_title,))
            recipe = cursor.fetchone()
            if not recipe:
                return 'Recipe not found', 404

            cursor.execute('SELECT * FROM "cuisine"')
            cuisines = cursor.fetchall()
            cursor.execute(
                'SELECT "RecRestriction" FROM "recipe_restrictions" WHERE "recipe_name" = %s', (recipe_title,))
            recipe_tags = cursor.fetchall()
            recipe_tags = [tag['RecRestriction'] for tag in recipe_tags]

            if 'user_id' not in session or (session['user_id'] != recipe['UserID'] and not session.get('is_admin')):
                return redirect(url_for('index'))

            if request.method == 'POST':
                description = request.form['description']
                prep_time = request.form['prep_time']
                cook_time = request.form['cook_time']
                ingredients = request.form['ingredients']
                instructions = request.form['instructions']
                cuisine_type = request.form['cuisine_type']
                tags = request.form.getlist('tags[]')

                file = request.files['recipe_image']
                filename = secure_filename(file.filename) if file else None
                file_path = recipe['recipe_image']
                if filename and allowed_file(filename):
                    file_path = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                with conn.cursor() as cursor:
                    cursor.execute('''
                        UPDATE "recipe" SET
                        "recipe_description" = %s,
                        "Cuisine_ID" = %s,
                        "prep_time" = %s,
                        "cook_time" = %s,
                        "recipe_image" = %s,
                        "instructions" = %s
                        WHERE "recipe_name" = %s
                    ''', (description, cuisine_type, prep_time, cook_time, file_path, instructions, recipe_title))

                    cursor.execute(
                        'DELETE FROM "recipe_restrictions" WHERE "recipe_name" = %s', (recipe_title,))
                    for tag in tags:
                        cursor.execute('INSERT INTO "recipe_restrictions" ("recipe_name", "RecRestriction") VALUES (%s, %s)',
                                       (recipe_title, tag))

                    conn.commit()

                return redirect(url_for('view_recipe', slug=slugify(recipe_title)))
            else:
                cursor.execute(
                    'SELECT "ingredient_name" FROM "ingredients" WHERE "recipe_name" = %s', (recipe_title,))
                ingredients = [ingredient['ingredient_name']
                               for ingredient in cursor.fetchall()]
                return render_template('edit_recipe.html', recipe=recipe, ingredients=ingredients, cuisines=cuisines, all_tags=ALL_TAGS, recipe_tags=recipe_tags)
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during recipe editing: {e}")
        return 'An error occurred', 500
    finally:
        conn.close()


@app.route('/delete-recipe/<recipe_name>', methods=['DELETE'])
def delete_recipe(recipe_name):
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                'SELECT * FROM "recipe" WHERE "recipe_name" = %s', (recipe_name,))
            recipe = cursor.fetchone()

            if recipe is None:
                return jsonify({'message': 'Recipe not found'}), 404

            if session['user_id'] == recipe['UserID'] or session.get('is_admin'):
                cursor.execute(
                    'DELETE FROM "recipe" WHERE "recipe_name" = %s', (recipe_name,))
                cursor.execute(
                    'DELETE FROM "recipe_restrictions" WHERE "recipe_name" = %s', (recipe_name,))
                cursor.execute(
                    'DELETE FROM "rates" WHERE "recipe_name" = %s', (recipe_name,))
                cursor.execute(
                    'DELETE FROM "contains" WHERE "recipe_name" = %s', (recipe_name,))
                cursor.execute(
                    'DELETE FROM "ingredients" WHERE "recipe_name" = %s', (recipe_name,))
                conn.commit()
                response = {'message': 'Recipe deleted successfully'}
                status_code = 200
            else:
                response = {'message': 'Unauthorized'}
                status_code = 401
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during recipe deletion: {e}")
        response = {'message': 'Failed to delete recipe', 'error': str(e)}
        status_code = 500
    finally:
        conn.close()
    return jsonify(response), status_code


@app.route('/save-to-cookbook/<recipe_name>', methods=['POST'])
def save_to_cookbook(recipe_name):
    if 'user_id' not in session:
        return jsonify({'message': 'You must be logged in to save recipes.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "cookbook" ("CookBook_ID") VALUES (%s) ON CONFLICT ("CookBook_ID") DO NOTHING', (user_id,))

            cursor.execute('SELECT 1 FROM "contains" WHERE "CookBook_ID" = %s AND "recipe_name" = %s',
                           (user_id, recipe_name))
            if cursor.fetchone():
                return jsonify({'message': 'Recipe already in cookbook.'}), 409

            cursor.execute('INSERT INTO "contains" ("CookBook_ID", "recipe_name") VALUES (%s, %s)',
                           (user_id, recipe_name))
            conn.commit()
            return jsonify({'message': 'Recipe saved to your cookbook!'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during saving to cookbook: {e}")
        return jsonify({'message': 'Failed to save recipe.', 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/cookbook')
def cookbook():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('''
                SELECT r.* FROM "recipe" r
                WHERE r."UserID" = %s 
                UNION
                SELECT r.* FROM "recipe" r
                JOIN "contains" fr ON fr."recipe_name" = r."recipe_name"
                JOIN "cookbook" c ON fr."CookBook_ID" = c."CookBook_ID"
                WHERE c."CookBook_ID" = %s
            ''', (user_id, user_id))
            recipes = cursor.fetchall()
            return render_template('cookbook.html', recipes=recipes)
    except psycopg2.Error as e:
        print(f"Database error during cookbook retrieval: {e}")
        return 'An error occurred', 500
    finally:
        conn.close()


@app.route('/toggle-cookbook/<recipe_name>', methods=['POST'])
def toggle_cookbook(recipe_name):
    if 'user_id' not in session:
        return jsonify({'message': 'You must be logged in to manage recipes.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "cookbook" ("CookBook_ID") VALUES (%s) ON CONFLICT ("CookBook_ID") DO NOTHING', (user_id,))

            cursor.execute('SELECT 1 FROM "contains" WHERE "CookBook_ID" = %s AND "recipe_name" = %s',
                           (user_id, recipe_name))
            if cursor.fetchone():
                cursor.execute(
                    'DELETE FROM "contains" WHERE "CookBook_ID" = %s AND "recipe_name" = %s', (user_id, recipe_name))
                message = 'Recipe removed from your cookbook.'
            else:
                cursor.execute('INSERT INTO "contains" ("CookBook_ID", "recipe_name") VALUES (%s, %s)',
                               (user_id, recipe_name))
                message = 'Recipe saved to your cookbook!'

            conn.commit()
            return jsonify({'message': message}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during toggling cookbook: {e}")
        return jsonify({'message': 'Failed to update cookbook.', 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/check-cookbook/<recipe_name>')
def check_cookbook(recipe_name):
    if 'user_id' not in session:
        return jsonify({'in_cookbook': False}), 200

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM "contains" WHERE "CookBook_ID" = %s AND "recipe_name" = %s',
                           (user_id, recipe_name))
            exists = cursor.fetchone()
            return jsonify({'in_cookbook': bool(exists)}), 200
    except psycopg2.Error as e:
        print(f"Database error during checking cookbook: {e}")
        return jsonify({'in_cookbook': False}), 500
    finally:
        conn.close()


@app.route('/rate-recipe', methods=['POST'])
def rate_recipe():
    if 'user_id' not in session:
        return jsonify({'error': 'You must be logged in to rate recipes.'}), 401

    data = request.get_json()
    recipe_name = data['recipe_name']
    rating = data['rating']

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO "rates" ("User_ID", "recipe_name", "user_rating")
                VALUES (%s, %s, %s)
                ON CONFLICT ("User_ID", "recipe_name") DO UPDATE SET "user_rating" = EXCLUDED."user_rating"
            ''', (session['user_id'], recipe_name, rating))
            conn.commit()
        return jsonify({'message': 'Rating updated successfully'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error during rating recipe: {e}")
        return jsonify({'error': 'Failed to rate recipe', 'details': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/recommended')
def recommended_recipes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'You must be logged in to view recommendations.'}), 401

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                'SELECT "UserRestriction" FROM "user_restrictions" WHERE "User_ID" = %s', (user_id,))
            user_restrictions = [
                row['UserRestriction'] for row in cursor.fetchall()]

            if 'None' in user_restrictions or not user_restrictions:
                cursor.execute('''
                    SELECT r.*, COALESCE(AVG(ra."user_rating"), 0) as avg_rating
                    FROM "recipe" r
                    LEFT JOIN "rates" ra ON ra."recipe_name" = r."recipe_name"
                    GROUP BY r."recipe_id"
                    ORDER BY avg_rating DESC
                ''')
            else:
                placeholders = ','.join(['%s'] * len(user_restrictions))
                cursor.execute(f'''
                    SELECT DISTINCT r.*, COALESCE(AVG(ra."user_rating"), 0) as avg_rating
                    FROM "recipe" r
                    JOIN "recipe_restrictions" rr ON r."recipe_name" = rr."recipe_name"
                    LEFT JOIN "rates" ra ON ra."recipe_name" = r."recipe_name"
                    WHERE rr."RecRestriction" IN ({placeholders})
                    AND r."recipe_name" IN (
                        SELECT r2."recipe_name"
                        FROM "recipe" r2
                        JOIN "recipe_restrictions" rr2 ON r2."recipe_name" = rr2."recipe_name"
                        WHERE rr2."RecRestriction" IN ({placeholders})
                        GROUP BY r2."recipe_name"
                        HAVING COUNT(*) = %s
                    )
                    GROUP BY r."recipe_id"
                    ORDER BY avg_rating DESC
                ''', user_restrictions + user_restrictions + [len(user_restrictions)])
            recipes = cursor.fetchall()
            return jsonify({'recipes': recipes})
    except psycopg2.Error as e:
        print(f"Database error during fetching recommendations: {e}")
        return jsonify({'error': 'An error occurred while fetching recommendations'}), 500
    finally:
        conn.close()


@app.route('/recommended')
def recommended():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('recommended.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

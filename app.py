from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import os
import subprocess
import urllib.parse
from werkzeug.utils import secure_filename
from tests.test_runner import run_all_tests
app = Flask(__name__)
app.secret_key = os.urandom(24)  
app.config['UPLOAD_FOLDER'] = 'static/images'
DATABASE = 'database.db'
ALL_TAGS = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        with open('setup.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()

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
            conn.execute('INSERT INTO account (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()

            # Get the account ID of the newly created account
            account_id = conn.execute('SELECT id FROM account WHERE username = ?', (username,)).fetchone()[0]

            # Insert the account ID into the users table
            conn.execute('INSERT INTO users (Account_ID) VALUES (?)', (account_id,))
            conn.commit()

        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 409
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
        user = conn.execute('SELECT * FROM account WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            # Check if the user is an admin
            admin_check = conn.execute('SELECT * FROM admin WHERE Account_ID = ?', (user['id'],)).fetchone()
            session['is_admin'] = bool(admin_check)
            return jsonify({'message': 'Login successful', 'redirect': url_for('dashboard')}), 200
        else:
            return jsonify({'message': 'Login failed'}), 401
    finally:
        conn.close()


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/recipes')
def get_recipes():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    try:
        if search_query:
            recipes = conn.execute('''
                SELECT r.*, COALESCE(AVG(rates.user_rating), 0) as avg_rating
                FROM recipe r
                LEFT JOIN rates ON rates.recipe_name = r.recipe_name
                WHERE r.recipe_name LIKE ?
                GROUP BY r.recipe_name
            ''', ('%' + search_query + '%',)).fetchall()
        else:
            recipes = conn.execute('''
                SELECT r.*, COALESCE(AVG(rates.user_rating), 0) as avg_rating
                FROM recipe r
                LEFT JOIN rates ON rates.recipe_name = r.recipe_name
                GROUP BY r.recipe_name
            ''').fetchall()
        recipes = [dict(recipe) for recipe in recipes]
        return jsonify({'recipes': recipes})
    finally:
        conn.close()



@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to login page if user is not logged in

    search_query = request.args.get('search', '')
    conn = get_db_connection()
    try:
        if search_query:
            # Use SQL LIKE to filter recipes by name
            recipes = conn.execute('SELECT * FROM recipe WHERE recipe_name LIKE ?', ('%' + search_query + '%',)).fetchall()
        else:
            recipes = conn.execute('SELECT * FROM recipe').fetchall()
        return render_template('dashboard.html', recipes=recipes)
    finally:
        conn.close()


@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('settings.html')


@app.route('/change_username', methods=['POST'])
def change_username():
    new_username = request.form['username']
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 403
    
    conn = get_db_connection()
    try:
        # Update account table
        conn.execute('UPDATE account SET username = ? WHERE id = ?', (new_username, user_id))
        conn.commit()
        
        # Check if the user is an admin and update the admin table
        if conn.execute('SELECT Account_ID FROM admin WHERE Account_ID = ?', (user_id,)).fetchone():
            conn.execute('UPDATE admin SET admin_name = ? WHERE Account_ID = ?', (new_username, user_id))
            conn.commit()

        response = {'message': 'Username successfully updated'}
        status_code = 200
    except Exception as e:
        conn.rollback()
        response = {'message': 'Failed to update username', 'error': str(e)}
        status_code = 500
    finally:
        conn.close()

    return jsonify(response), status_code



@app.route('/change_password', methods=['POST'])
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 403

    conn = get_db_connection()
    try:
        user = conn.execute('SELECT * FROM account WHERE id = ? AND password = ?', (user_id, current_password)).fetchone()
        if user:
            conn.execute('UPDATE account SET password = ? WHERE id = ?', (new_password, user_id))
            conn.commit()
            response = {'message': 'Password successfully updated'}
            status_code = 200
        else:
            response = {'message': 'Current password is incorrect'}
            status_code = 401
    except Exception as e:
        conn.rollback()
        response = {'message': 'Failed to update password', 'error': str(e)}
        status_code = 500
    finally:
        conn.close()

    return jsonify(response), status_code

@app.route('/change_email', methods=['POST'])
def change_email():
    email = request.form['email']
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 403

    conn = get_db_connection()
    try:
        conn.execute('UPDATE account SET email = ? WHERE id = ?', (email, user_id))
        conn.commit()
        response = {'message': 'Email successfully updated'}
        status_code = 200
    except Exception as e:
        conn.rollback()
        response = {'message': 'Failed to update email', 'error': str(e)}
        status_code = 500
    finally:
        conn.close()

    return jsonify(response), status_code

@app.route('/update_security_key', methods=['POST'])
def update_security_key():
    security_key = request.form['security_key']
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 403

    if security_key == 'admin':
        conn = get_db_connection()
        try:
            # First check if the user is already an admin
            admin_check = conn.execute('SELECT Account_ID FROM admin WHERE Account_ID = ?', (user_id,)).fetchone()
            if not admin_check:
                # Fetch username from the account table
                user_info = conn.execute('SELECT username FROM account WHERE id = ?', (user_id,)).fetchone()
                if user_info:
                    username = user_info['username']
                    # Insert into admin table including username
                    conn.execute('INSERT INTO admin (Account_ID, admin_name) VALUES (?, ?)', (user_id, username))
                    conn.commit()

                    # Remove the account from the users table
                    conn.execute('DELETE FROM users WHERE Account_ID = ?', (user_id,))
                    conn.commit()

                    response = {'message': 'User granted admin privileges. Sign in to view changes.'}
                else:
                    response = {'message': 'User not found'}
                    status_code = 404
                    return jsonify(response), status_code
            else:
                response = {'message': 'User already has admin privileges'}
            status_code = 200
        except Exception as e:
            conn.rollback()
            response = {'message': 'Failed to grant admin privileges', 'error': str(e)}
            status_code = 500
        finally:
            conn.close()
    else:
        response = {'message': 'Invalid security key'}
        status_code = 400

    return jsonify(response), status_code


@app.route('/update_diet_restrictions', methods=['POST'])
def update_diet_restrictions():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 403

    restrictions = request.form.getlist('diet[]')  # This captures all checked boxes
    conn = get_db_connection()
    try:
        # Clear existing restrictions for simplicity, or check and update
        conn.execute('DELETE FROM user_restrictions WHERE User_ID = ?', (user_id,))
        for restriction in restrictions:
            conn.execute('INSERT INTO user_restrictions (User_ID, UserRestriction) VALUES (?, ?)', (user_id, restriction))
        conn.commit()
        response = {'message': 'Dietary restrictions updated successfully'}
        status_code = 200
    except Exception as e:
        conn.rollback()
        response = {'message': 'Failed to update dietary restrictions', 'error': str(e)}
        status_code = 500
    finally:
        conn.close()

    return jsonify(response), status_code

@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'User not logged in'}), 403

    conn = get_db_connection()
    try:
        # Delete account from admin table (if it exists)
        conn.execute('DELETE FROM admin WHERE Account_ID = ?', (user_id,))
        
        # Delete account from users table
        conn.execute('DELETE FROM users WHERE Account_ID = ?', (user_id,))
        
        # Delete corresponding rows from user_restrictions table
        conn.execute('DELETE FROM user_restrictions WHERE User_ID = ?', (user_id,))
        
        #Delete Cookbook
        conn.execute('DELETE FROM cookbook WHERE CookBook_ID = ?', (user_id,))

        # Delete account from account table
        conn.execute('DELETE FROM account WHERE id = ?', (user_id,))

        
        conn.commit()
        
        response = {'message': 'Account deleted successfully'}
        status_code = 200
    except Exception as e:
        conn.rollback()
        response = {'message': 'Failed to delete account', 'error': str(e)}
        status_code = 500
    finally:
        conn.close()

    return jsonify(response), status_code


def slugify(text):
    """Create a URL slug from the recipe name."""
    return urllib.parse.quote_plus(text.lower().replace(" ", "-"))
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
            user_id = session.get('user_id', 1)  # Default to user ID 1 if not logged in
            tags = request.form.getlist('tags[]')

            file = request.files['recipe_image']
            filename = secure_filename(file.filename) if file else None
            if filename and allowed_file(filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            else:
                file_path = None  

            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recipe (recipe_name, recipe_description, Cuisine_ID, UserID, prep_time, cook_time, recipe_image, instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (recipe_name, description, cuisine_type, user_id, prep_time, cook_time, file_path, instructions))

            ingredient_list = ingredients.split(',')
            for ingredient in ingredient_list:
                cursor.execute('''
                    INSERT INTO ingredients (recipe_name, ingredient_name)
                    VALUES (?, ?)
                ''', (recipe_name, ingredient.strip()))

            for tag in tags:
                cursor.execute('''
                    INSERT INTO recipe_restrictions (recipe_name, RecRestriction)
                    VALUES (?, ?)
                ''', (recipe_name, tag))

            conn.commit()
            return redirect(url_for('view_recipe', slug=recipe_name))  # Redirect to the view recipe page
        else:
            # Fetch all available cuisines to populate the dropdown
            cuisines = conn.execute('SELECT * FROM cuisine').fetchall()
            return render_template('create_recipe.html', cuisines=cuisines)
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({'error': 'Failed to insert recipe into database', 'details': str(e)}), 500
    finally:
        conn.close()
@app.route('/recipe/<slug>')
def view_recipe(slug):
    conn = get_db_connection()
    try:
        recipe_title = slug.replace("-", " ")
        recipe = conn.execute('SELECT * FROM recipe WHERE recipe_name = ?', (recipe_title,)).fetchone()
        ingredients = conn.execute('SELECT ingredient_name FROM ingredients WHERE recipe_name = ?', (recipe_title,)).fetchall()
        tags = conn.execute('SELECT RecRestriction FROM recipe_restrictions WHERE recipe_name = ?', (recipe_title,)).fetchall()

        # Fetch average rating and count of ratings, ensuring avg_rating is treated as a float
        rating_result = conn.execute('SELECT AVG(user_rating) AS avg_rating, COUNT(*) AS rating_count FROM rates WHERE recipe_name = ?', (recipe_title,)).fetchone()
        avg_rating = float(rating_result['avg_rating']) if rating_result['avg_rating'] is not None else 0
        rating_count = rating_result['rating_count']

        if recipe:
            return render_template('recipe.html', recipe=recipe, ingredients=ingredients, tags=tags, avg_rating=avg_rating, rating_count=rating_count)
        else:
            return 'Recipe not found', 404
    finally:
        conn.close()


@app.route('/delete-recipe/<recipe_name>', methods=['DELETE'])
def delete_recipe(recipe_name):
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 403

    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipe WHERE recipe_name = ?', (recipe_name,)).fetchone()

    # Check if the user is the recipe creator or an admin
    if session['user_id'] == recipe['UserID'] or session.get('is_admin'):
        try:
            conn.execute('DELETE FROM recipe WHERE recipe_name = ?', (recipe_name,))
            conn.commit()
            conn.execute('DELETE FROM recipe_restrictions WHERE recipe_name = ?', (recipe_name,))
            conn.commit()

            conn.execute('DELETE FROM rates WHERE recipe_name = ?', (recipe_name,))
            conn.commit()
            conn.execute('DELETE FROM contains WHERE recipe_name = ?', (recipe_name,))
            conn.commit()
            conn.execute('DELETE FROM ingredients WHERE recipe_name = ?', (recipe_name,))
            conn.commit()
            conn.execute('DELETE FROM rates WHERE recipe_name = ?', (recipe_name,))
            conn.commit()
            response = {'message': 'Recipe deleted successfully'}
            status_code = 200
        except Exception as e:
            conn.rollback()
            response = {'message': 'Failed to delete recipe', 'error': str(e)}
            status_code = 500
        finally:
            conn.close()
        return jsonify(response), status_code
    else:
        conn.close()
        return jsonify({'message': 'Unauthorized'}), 401

@app.route('/edit-recipe/<slug>', methods=['GET', 'POST'])
def edit_recipe(slug):
    conn = get_db_connection()
    try:
        recipe = conn.execute('SELECT * FROM recipe WHERE recipe_name = ?', (slug.replace("-", " "),)).fetchone()
        if not recipe:
            return 'Recipe not found', 404

        # Fetch all cuisines and tags
        cuisines = conn.execute('SELECT * FROM cuisine').fetchall()
        recipe_tags = conn.execute('SELECT RecRestriction FROM recipe_restrictions WHERE recipe_name = ?', (slug.replace("-", " "),)).fetchall()
        recipe_tags = [tag['RecRestriction'] for tag in recipe_tags]

        if 'user_id' not in session or (session['user_id'] != recipe['UserID'] and not session.get('is_admin')):
            return redirect(url_for('index'))

        if request.method == 'POST':
            # Gather form data including the selected cuisine from dropdown
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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

            # Update the database
            conn.execute('''
                UPDATE recipe SET
                recipe_description = ?,
                Cuisine_ID = ?,
                prep_time = ?,
                cook_time = ?,
                recipe_image = ?,
                instructions = ?
                WHERE recipe_name = ?
            ''', (description, cuisine_type, prep_time, cook_time, file_path, instructions, slug.replace("-", " ")))

            conn.execute('DELETE FROM recipe_restrictions WHERE recipe_name = ?', (slug.replace("-", " "),))
            for tag in tags:
                conn.execute('INSERT INTO recipe_restrictions (recipe_name, RecRestriction) VALUES (?, ?)', (slug.replace("-", " "), tag))

            conn.commit()

            # Redirect to the view recipe page
            return redirect(url_for('view_recipe', slug=slug.replace(" ", "-")))
        else:
            ingredients = [ingredient['ingredient_name'] for ingredient in conn.execute('SELECT ingredient_name FROM ingredients WHERE recipe_name = ?', (slug.replace("-", " "),)).fetchall()]
            return render_template('edit_recipe.html', recipe=recipe, ingredients=ingredients, cuisines=cuisines, all_tags=ALL_TAGS, recipe_tags=recipe_tags)
    finally:
        conn.close()


@app.route('/save-to-cookbook/<recipe_name>', methods=['POST'])
def save_to_cookbook(recipe_name):
    if 'user_id' not in session:
        return jsonify({'message': 'You must be logged in to save recipes.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # Check if the user already has a cookbook entry
        cookbook_id = conn.execute('SELECT CookBook_ID FROM cookbook WHERE CookBook_ID = ?', (user_id,)).fetchone()
        if not cookbook_id:
            # Create a cookbook entry if it does not exist
            conn.execute('INSERT INTO cookbook (CookBook_ID) VALUES (?)', (user_id,))

        # Check if the recipe is already saved
        exists = conn.execute('SELECT 1 FROM contains WHERE CookBook_ID = ? AND recipe_name = ?', (user_id, recipe_name)).fetchone()
        if exists:
            return jsonify({'message': 'Recipe already in cookbook.'}), 409

        # Save the recipe into the contains table
        conn.execute('INSERT INTO contains (CookBook_ID, recipe_name) VALUES (?, ?)', (user_id, recipe_name))
        conn.commit()
        return jsonify({'message': 'Recipe saved to your cookbook!'}), 200
    except sqlite3.IntegrityError as e:
        conn.rollback()
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
        recipes = conn.execute('''
            SELECT r.* FROM recipe r
            WHERE r.UserID = ? 
            UNION
            SELECT r.* FROM recipe r
            JOIN contains fr ON REPLACE(fr.recipe_name, '-', ' ') = r.recipe_name
            JOIN cookbook c ON fr.CookBook_ID = c.CookBook_ID
            WHERE c.CookBook_ID = ?
        ''', (user_id, user_id)).fetchall()
    finally:
        conn.close()

    return render_template('cookbook.html', recipes=recipes)





@app.route('/toggle-cookbook/<recipe_name>', methods=['POST'])
def toggle_cookbook(recipe_name):
    if 'user_id' not in session:
        return jsonify({'message': 'You must be logged in to manage recipes.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # Ensure the user has a cookbook entry
        conn.execute('INSERT OR IGNORE INTO cookbook (CookBook_ID) VALUES (?)', (user_id,))

        # Check if the recipe is already saved
        exists = conn.execute('SELECT 1 FROM contains WHERE CookBook_ID = ? AND recipe_name = ?', (user_id, recipe_name)).fetchone()
        if exists:
            # Delete the recipe from the cookbook
            conn.execute('DELETE FROM contains WHERE CookBook_ID = ? AND recipe_name = ?', (user_id, recipe_name))
            message = 'Recipe removed from your cookbook.'
        else:
            # Save the recipe into the cookbook
            conn.execute('INSERT INTO contains (CookBook_ID, recipe_name) VALUES (?, ?)', (user_id, recipe_name))
            message = 'Recipe saved to your cookbook!'

        conn.commit()
        return jsonify({'message': message}), 200
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({'message': 'Failed to update cookbook.', 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/check-cookbook/<recipe_name>')
def check_cookbook(recipe_name):
    if 'user_id' not in session:
        return jsonify({'in_cookbook': False}), 200

    user_id = session['user_id']
    conn = get_db_connection()
    exists = conn.execute('SELECT 1 FROM contains WHERE CookBook_ID = ? AND recipe_name = ?', (user_id, recipe_name)).fetchone()
    conn.close()
    return jsonify({'in_cookbook': bool(exists)}), 200


@app.route('/rate-recipe', methods=['POST'])
def rate_recipe():
    if 'user_id' not in session:
        return jsonify({'error': 'You must be logged in to rate recipes.'}), 401
    
    data = request.get_json()
    recipe_name = data['recipe_name']
    rating = data['rating']
    
    try:
        conn = get_db_connection()
        conn.execute('INSERT OR REPLACE INTO rates (User_ID, recipe_name, user_rating) VALUES (?, ?, ?)', 
                     (session['user_id'], recipe_name, rating))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Failed to rate recipe', 'details': str(e)}), 500
    finally:
        conn.close()
    return jsonify({'message': 'Rating updated successfully'}), 200


@app.route('/api/recommended')
def recommended_recipes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'You must be logged in to view recommendations.'}), 401

    conn = get_db_connection()
    try:
        user_restrictions = conn.execute('SELECT UserRestriction FROM user_restrictions WHERE User_ID = ?', (user_id,)).fetchall()
        user_restrictions = [row['UserRestriction'] for row in user_restrictions]

        if 'None' in user_restrictions:
            # If 'None' is among user restrictions, return all recipes
            recipes = conn.execute('''
                SELECT r.*, COALESCE(AVG(ra.user_rating), 0) as avg_rating
                FROM recipe r
                LEFT JOIN rates ra ON ra.recipe_name = r.recipe_name
                GROUP BY r.recipe_name
                ORDER BY avg_rating DESC
            ''').fetchall()
        elif user_restrictions:
            placeholders = ','.join('?' for _ in user_restrictions)
            query = f'''
                SELECT DISTINCT r.*, COALESCE(AVG(ra.user_rating), 0) as avg_rating
                FROM recipe r
                JOIN recipe_restrictions rr ON r.recipe_name = rr.recipe_name
                LEFT JOIN rates ra ON ra.recipe_name = r.recipe_name
                WHERE rr.RecRestriction IN ({placeholders})
                AND r.recipe_name IN (
                    SELECT r2.recipe_name
                    FROM recipe r2
                    JOIN recipe_restrictions rr2 ON r2.recipe_name = rr2.recipe_name
                    WHERE rr2.RecRestriction IN ({placeholders})
                    GROUP BY r2.recipe_name
                    HAVING COUNT(*) = {len(user_restrictions)}
                )
                GROUP BY r.recipe_name
                ORDER BY avg_rating DESC
            '''
            recipes = conn.execute(query, user_restrictions + user_restrictions).fetchall()
        else:
            recipes = conn.execute('''
                SELECT r.*, COALESCE(AVG(ra.user_rating), 0) as avg_rating
                FROM recipe r
                LEFT JOIN rates ra ON ra.recipe_name = r.recipe_name
                GROUP BY r.recipe_name
                ORDER BY avg_rating DESC
            ''').fetchall()

        recipes = [dict(recipe) for recipe in recipes]
        return jsonify({'recipes': recipes})
    finally:
        conn.close()





@app.route('/recommended')
def recommended():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('recommended.html')


@app.route('/run-tests')
def run_tests():
    code = run_all_tests()
    return jsonify({
        "status": "done",
        "passed": code == 0,
        "exit_code": code
    })

if __name__ == '__main__':
    init_db()  
    app.run(debug=True)

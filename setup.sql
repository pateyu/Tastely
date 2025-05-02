PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin (
    Account_ID INTEGER PRIMARY KEY,
    admin_name TEXT UNIQUE NOT NULL,
    FOREIGN KEY(Account_ID) REFERENCES account(id) ON DELETE CASCADE,
    FOREIGN KEY(admin_name) REFERENCES account(username) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    Account_ID INTEGER PRIMARY KEY,
    FOREIGN KEY(Account_ID) REFERENCES account(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cuisine (
    Cuisine_ID TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS regional_cuisine (
    region_desc TEXT,
    Cuisine_ID TEXT PRIMARY KEY,
    FOREIGN KEY(Cuisine_ID) REFERENCES cuisine(Cuisine_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cuisine_type (
    type_description TEXT,
    Cuisine_ID TEXT PRIMARY KEY,
    FOREIGN KEY(Cuisine_ID) REFERENCES cuisine(Cuisine_ID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT UNIQUE,
    Cuisine_ID TEXT,
    UserID INTEGER,
    recipe_description TEXT,
    prep_time INTEGER,  
    cook_time INTEGER,  
    recipe_image TEXT,  
    instructions TEXT,
    FOREIGN KEY(Cuisine_ID) REFERENCES cuisine(Cuisine_ID) ON DELETE SET NULL,
    FOREIGN KEY(UserID) REFERENCES account(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_restrictions (
    recipe_name VARCHAR(80),
    RecRestriction VARCHAR(30),
    FOREIGN KEY(recipe_name) REFERENCES recipe(recipe_name) ON DELETE CASCADE,
    PRIMARY KEY (recipe_name, RecRestriction)
);

CREATE TABLE IF NOT EXISTS ingredients (
    recipe_name VARCHAR(80),
    ingredient_name VARCHAR(80),
    FOREIGN KEY(recipe_name) REFERENCES recipe(recipe_name) ON DELETE CASCADE,
    PRIMARY KEY (recipe_name, ingredient_name)
);

CREATE TABLE IF NOT EXISTS user_restrictions (
    User_ID INTEGER,
    UserRestriction VARCHAR(30),
    FOREIGN KEY(User_ID) REFERENCES account(id) ON DELETE CASCADE,
    PRIMARY KEY (User_ID, UserRestriction)
);

CREATE TABLE IF NOT EXISTS cookbook (
    CookBook_ID INTEGER PRIMARY KEY,
    FOREIGN KEY(CookBook_ID) REFERENCES account(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS contains (
    CookBook_ID INTEGER,
    recipe_name TEXT,
    FOREIGN KEY(CookBook_ID) REFERENCES cookbook(CookBook_ID) ON DELETE CASCADE,
    FOREIGN KEY(recipe_name) REFERENCES recipe(recipe_name) ON DELETE CASCADE,
    PRIMARY KEY (CookBook_ID, recipe_name)
);


CREATE TABLE IF NOT EXISTS rates (
    User_ID INTEGER NOT NULL,
    recipe_name VARCHAR(80) NOT NULL,
    user_rating INTEGER CHECK (user_rating BETWEEN 0 AND 5),
    FOREIGN KEY(User_ID) REFERENCES account(id) ON DELETE CASCADE,
    FOREIGN KEY(recipe_name) REFERENCES recipe(recipe_name) ON DELETE CASCADE,
    PRIMARY KEY (User_ID, recipe_name)
);

-- Insert into 'cuisine' only if the cuisine does not already exist
INSERT OR IGNORE INTO cuisine (Cuisine_ID) VALUES
('American'),
('Mexican'),
('Indian'),
('Italian'),
('Greek'),
('Chinese'),
('Breakfast'),
('Salad'),
('Soup'),
('Dessert');

-- Insert into 'regional_cuisine' only if the cuisine does not already exist
INSERT OR IGNORE INTO regional_cuisine (region_desc, Cuisine_ID) VALUES
('North American cuisine includes foods like burgers and barbecue', 'American'),
('Mexican cuisine features staples like tacos and enchiladas', 'Mexican'),
('Indian cuisine tantalizes taste buds with its vibrant array of aromatic spices, rich flavors, and diverse regional specialties, reflecting a culinary heritage steeped in tradition and innovation.', 'Indian'),
('Italian cuisine is a harmonious fusion of fresh, high-quality ingredients and simple cooking techniques, celebrated for its rich flavors and regional diversity.', 'Italian'),
('Greek cuisine shows the vibrant flavors of the Mediterranean with its emphasis on fresh vegetables, olive oil, herbs, and grilled meats, reflecting a balance of tradition and innovation.', 'Greek'),
('Chinese cuisine captivates the palate with its diverse range of flavors, from savory and spicy to sweet and sour, all expertly balanced with fresh ingredients and centuries-old cooking techniques.', 'Chinese');




-- Insert into 'cuisine_type' only if the cuisine does not already exist
INSERT OR IGNORE INTO cuisine_type (type_description, Cuisine_ID) VALUES
('Foods eaten first thing in the morning', 'Breakfast'),
('Stuff in a bowl.', 'Salad'),
('Stuff in water.', 'Soup'),
('Sweet treats.', 'Dessert');

CREATE TABLE IF NOT EXISTS "account" (
    "id" SERIAL PRIMARY KEY,
    "username" TEXT UNIQUE NOT NULL,
    "email" TEXT UNIQUE NOT NULL,
    "password" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "admin" (
    "Account_ID" INTEGER PRIMARY KEY,
    "admin_name" TEXT UNIQUE NOT NULL,
    FOREIGN KEY("Account_ID") REFERENCES "account"("id") ON DELETE CASCADE,
    FOREIGN KEY("admin_name") REFERENCES "account"("username") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "users" (
    "Account_ID" INTEGER PRIMARY KEY,
    FOREIGN KEY("Account_ID") REFERENCES "account"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "cuisine" (
    "Cuisine_ID" TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS "regional_cuisine" (
    "region_desc" TEXT,
    "Cuisine_ID" TEXT PRIMARY KEY,
    FOREIGN KEY("Cuisine_ID") REFERENCES "cuisine"("Cuisine_ID") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "cuisine_type" (
    "type_description" TEXT,
    "Cuisine_ID" TEXT PRIMARY KEY,
    FOREIGN KEY("Cuisine_ID") REFERENCES "cuisine"("Cuisine_ID") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "recipe" (
    "recipe_id" SERIAL PRIMARY KEY,
    "recipe_name" TEXT UNIQUE,
    "Cuisine_ID" TEXT,
    "UserID" INTEGER,
    "recipe_description" TEXT,
    "prep_time" INTEGER,  
    "cook_time" INTEGER,  
    "recipe_image" TEXT,  
    "instructions" TEXT,
    FOREIGN KEY("Cuisine_ID") REFERENCES "cuisine"("Cuisine_ID") ON DELETE SET NULL,
    FOREIGN KEY("UserID") REFERENCES "account"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "recipe_restrictions" (
    "recipe_name" VARCHAR(80),
    "RecRestriction" VARCHAR(30),
    FOREIGN KEY("recipe_name") REFERENCES "recipe"("recipe_name") ON DELETE CASCADE,
    PRIMARY KEY ("recipe_name", "RecRestriction")
);

CREATE TABLE IF NOT EXISTS "ingredients" (
    "recipe_name" VARCHAR(80),
    "ingredient_name" VARCHAR(80),
    FOREIGN KEY("recipe_name") REFERENCES "recipe"("recipe_name") ON DELETE CASCADE,
    PRIMARY KEY ("recipe_name", "ingredient_name")
);

CREATE TABLE IF NOT EXISTS "user_restrictions" (
    "User_ID" INTEGER,
    "UserRestriction" VARCHAR(30),
    FOREIGN KEY("User_ID") REFERENCES "account"("id") ON DELETE CASCADE,
    PRIMARY KEY ("User_ID", "UserRestriction")
);

CREATE TABLE IF NOT EXISTS "cookbook" (
    "CookBook_ID" INTEGER PRIMARY KEY,
    FOREIGN KEY("CookBook_ID") REFERENCES "account"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "contains" (
    "CookBook_ID" INTEGER,
    "recipe_name" TEXT,
    FOREIGN KEY("CookBook_ID") REFERENCES "cookbook"("CookBook_ID") ON DELETE CASCADE,
    FOREIGN KEY("recipe_name") REFERENCES "recipe"("recipe_name") ON DELETE CASCADE,
    PRIMARY KEY ("CookBook_ID", "recipe_name")
);

CREATE TABLE IF NOT EXISTS "rates" (
    "User_ID" INTEGER NOT NULL,
    "recipe_name" VARCHAR(80) NOT NULL,
    "user_rating" INTEGER CHECK ("user_rating" BETWEEN 0 AND 5),
    FOREIGN KEY("User_ID") REFERENCES "account"("id") ON DELETE CASCADE,
    FOREIGN KEY("recipe_name") REFERENCES "recipe"("recipe_name") ON DELETE CASCADE,
    PRIMARY KEY ("User_ID", "recipe_name")
);




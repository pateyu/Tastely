# Global Food Library

### Old Demo Video

[Watch the demo video](https://www.youtube.com/watch?v=Vz9PjqHPAEE)

## Introduction

The Global Food Library is a web application that allows users to browse, create, and share recipes from around the world. Users can sign up, log in, create their own recipes, save recipes to their personal cookbook, and receive personalized recommendations.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Setting Up PostgreSQL Locally](#setting-up-postgresql-locally)
    - [Linux / macOS](#linux--macos)
    - [Windows](#windows)
  - [Cloning the Repository](#cloning-the-repository)
  - [Installing Python Dependencies](#installing-python-dependencies)
    - [Using the Bash Script (Linux/macOS)](#using-the-bash-script-linuxmacos)
    - [Manual Installation (Windows)](#manual-installation-windows)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- User authentication (signup, login, logout)
- Create, edit, and delete recipes
- Upload images for recipes
- Save recipes to a personal cookbook
- Rate recipes
- Personalized recipe recommendations
- Search for recipes

## Prerequisites

- **Python 3.6+**
- **PostgreSQL** database
- **Git** (for cloning the repository)
- **pip** (Python package installer)

## Installation

### Setting Up PostgreSQL Locally

#### Linux / macOS

1. **Install PostgreSQL**

   - **Ubuntu/Debian**:

     ```bash
     sudo apt update
     sudo apt install postgresql postgresql-contrib -y
     ```

   - **macOS** (using Homebrew):

     ```bash
     brew update
     brew install postgresql
     ```

2. **Start PostgreSQL Service**

   - **Ubuntu/Debian**:

     ```bash
     sudo service postgresql start
     ```

   - **macOS**:

     ```bash
     brew services start postgresql
     ```

3. **Create a PostgreSQL User and Database**

   ```bash
   sudo -u postgres psql
   ```

   In the `psql` shell, run:

   ```sql
   CREATE USER your_username WITH PASSWORD 'your_password';
   CREATE DATABASE your_database_name;
   GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
   \q
   ```

   Replace `your_username`, `your_password`, and `your_database_name` with your desired PostgreSQL username, password, and database name.

4. **Set Environment Variables**

   Create a `.env` file in the root directory of the project with the following content:

   ```ini
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASS=your_password
   DB_HOST=localhost
   ```

#### Windows

1. **Install PostgreSQL**

   Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/windows/).

2. **Create a PostgreSQL User and Database**

   - During installation, you will set up a superuser (default is `postgres`) and a password.
   - Use the **SQL Shell (psql)** or **pgAdmin** to create a new user and database.

   Using **SQL Shell (psql)**:

   ```bash
   psql -U postgres
   ```

   In the `psql` shell, run:

   ```sql
   CREATE USER your_username WITH PASSWORD 'your_password';
   CREATE DATABASE your_database_name;
   GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
   \q
   ```

3. **Set Environment Variables**

   Create a `.env` file in the root directory of the project with the following content:

   ```ini
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASS=your_password
   DB_HOST=localhost
   ```

### Cloning the Repository

```bash
git clone https://github.com/yourusername/global-food-library.git
cd global-food-library
```

Replace `yourusername` with your GitHub username or the appropriate repository owner.

### Installing Python Dependencies

#### Using the Bash Script (Linux/macOS)

If you're on a compatible system (Linux/macOS), you can use the provided bash script to automate the setup.

1. **Make the Script Executable**

   ```bash
   chmod +x setup.sh
   ```

2. **Run the Script**

   ```bash
   ./setup.sh
   ```

   This script will:

   - Check for Python 3 and pip
   - Install required Python packages
   - Initialize the database
   - Start the application

#### Manual Installation (Windows)

Since bash scripts are not natively supported on Windows, you can perform the steps manually.

1. **Ensure Python and pip are Installed**

   - Download Python from the [official website](https://www.python.org/downloads/windows/).
   - During installation, make sure to check the option to add Python to your system PATH.

2. **Create a Virtual Environment** (optional but recommended)

   Open Command Prompt and navigate to your project directory:

   ```cmd
   cd path	o\global-food-library
   ```

   Create a virtual environment:

   ```cmd
   python -m venv venv
   ```

   Activate the virtual environment:

   ```cmd
   venv\Scriptsctivate
   ```

3. **Install Required Packages**

   ```cmd
   pip install -r requirements.txt
   ```

4. **Initialize the Database**

   If your application requires initializing the database (e.g., running `setup.sql`), you can do it manually:

   - Open **SQL Shell (psql)** and connect to your database:

     ```cmd
     psql -U your_username -d your_database_name
     ```

   - Run the SQL commands in `setup.sql`:

     ```sql
     \i setup.sql
     ```

   - Exit the `psql` shell:

     ```sql
     \q
     ```

5. **Run the Application**

   ```cmd
   python app.py
   ```

### Initialize the Database

If not already done during the installation:

1. **Manually Initialize the Database**

   - Connect to your PostgreSQL database using `psql`:

     ```bash
     psql -U your_username -d your_database_name
     ```

   - Run the commands in `setup.sql`:

     ```sql
     \i setup.sql
     ```

   - Exit the `psql` shell:

     ```sql
     \q
     ```

## Usage

After starting the application, open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

- **Sign Up**: Create a new user account.
- **Log In**: Access your account using your credentials.
- **Create Recipes**: Add new recipes to the library.
- **Browse Recipes**: Explore recipes added by other users.
- **Save to Cookbook**: Save your favorite recipes to your personal cookbook.
- **Rate Recipes**: Provide ratings for recipes you've tried.
- **Get Recommendations**: Receive personalized recipe recommendations based on your preferences.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

   Click the "Fork" button at the top right of the repository page.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/yourusername/global-food-library.git
   cd global-food-library
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**

5. **Commit and Push**

   ```bash
   git add .
   git commit -m "Add your commit message here"
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

   Go to your forked repository on GitHub and click "New pull request".

## License

This project is licensed under the MIT License.

---

**Note:** Ensure that you replace placeholders like `your_username`, `your_password`, `your_database_name`, and repository URLs with the actual values relevant to your setup.

**Additional Tips:**

- **Environment Variables:** Remember to keep your `.env` file secure and never commit it to version control.
- **Database Migrations:** If you plan to make changes to the database schema, consider using a migration tool like Alembic.
- **Testing:** Before deploying or sharing your application, test all functionalities to ensure everything works as expected.

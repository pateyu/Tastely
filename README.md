# Tastely

## Introduction

**Tastely** is a web application that allows users to browse, create, and share recipes from around the world. Users can sign up, log in, create their own recipes, save favorites, and receive personalized recommendations.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- User authentication (signup, login, logout)
- Create, edit, and delete recipes
- Upload images for recipes
- Save recipes to a personal cookbook
- Rate and review recipes
- Personalized recipe recommendations
- Search and explore global cuisine

## Prerequisites

- **Python 3.6+**
- **Git** (for cloning the repository)
- **pip** (Python package installer)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/global-food-library.git
cd global-food-library
```

Replace `yourusername` with your GitHub username or the repo owner.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

- **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```
- **Windows**:
  ```cmd
  venv\Scripts\activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The app should now be running at:

```
http://127.0.0.1:5000/
```

> **Note**: Tastely uses **SQLite** as the default database. No additional setup is required — the database file (`tastely.db`) will be created automatically on first run.

## Usage

- **Sign Up**: Register for a new account.
- **Log In**: Access your dashboard.
- **Create Recipes**: Share your culinary ideas.
- **Browse Recipes**: Discover meals from others.
- **Save Recipes**: Keep track of your favorites.
- **Rate Recipes**: Provide feedback and improve suggestions.

## Contributing

### How to Contribute

1. **Fork the Repository**
2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/global-food-library.git
   cd global-food-library
   ```
3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make Changes and Commit**
   ```bash
   git add .
   git commit -m "Add your feature"
   ```
5. **Push and Create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## License

This project is licensed under the [MIT License](LICENSE).

---

### ⚠️ Notes

- The `.env` file is no longer required for SQLite.
- Do **not** commit your `venv/` folder or `__pycache__/` directories.
- For deployment, consider switching to a more robust DB like PostgreSQL or MySQL with environment-specific configurations.

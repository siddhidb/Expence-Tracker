<<<<<<< HEAD
# Expense Tracker

A simple web-based expense tracking application built with Flask and SQLite.

## 🚀 Deployment Options

### Option 1: Deploy to Render (Recommended)

1. Push your code to a GitHub repository
2. Go to [Render](https://render.com/) and sign up/log in
3. Click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure your app:
   - **Name**: expense-tracker (or your preferred name)
   - **Region**: Choose the closest to you
   - **Branch**: main (or your main branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click "Create Web Service"

### Option 2: Deploy to Railway.app

1. Push your code to a GitHub repository
2. Go to [Railway](https://railway.app/) and sign up/log in
3. Click "New Project" and select "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python app and deploy it
6. After deployment, your app will be available at `https://your-project-name.railway.app`

### Option 3: Deploy to PythonAnywhere (Free Tier Available)

1. Sign up at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Go to the "Web" tab and click "Add a new web app"
3. Choose "Flask" and Python 3.9
4. In the "Code" section, clone your GitHub repository
5. Go to the "Web" tab and click on the virtualenv link
6. Install requirements: `pip install -r requirements.txt`
7. Configure the WSGI file to point to your app
8. Reload your web app

## Features

- Add expenses with amount, category, and description
- View all expenses in a clean, responsive interface
- Delete expenses
- See the total amount spent
- Responsive design that works on mobile and desktop

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository or download the source code
2. Navigate to the project directory
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and go to `http://127.0.0.1:5000/`

## Project Structure

- `app.py` - Main application file with Flask routes and database models
- `templates/` - HTML templates for the web interface
  - `base.html` - Base template with common layout
  - `index.html` - Main page with expense form and list
- `requirements.txt` - Python dependencies
- `expenses.db` - SQLite database file (created automatically)

## Customization

You can customize the expense categories by modifying the `select` element in `templates/index.html`.

## License

This project is open source and available under the [MIT License](LICENSE).
=======
# Expence-Tracker
>>>>>>> 833fe15f4093e7f8bf8e7b0479172b19829a43c1

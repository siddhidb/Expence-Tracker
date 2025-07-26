from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import os
import json
from collections import defaultdict

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Database Models
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Expense {self.amount} - {self.category}>'

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False, unique=True)
    limit = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Budget {self.category} - {self.limit}>'

# Initialize default budgets if they don't exist
def init_budgets():
    default_budgets = {
        'Food': 3000,
        'Transportation': 2000,
        'Housing': 10000,
        'Entertainment': 1500,
        'Shopping': 2000,
        'Utilities': 3000,
        'Healthcare': 2000,
        'Education': 2500,
        'Other': 1000
    }
    
    for category, limit in default_budgets.items():
        if not Budget.query.filter_by(category=category).first():
            budget = Budget(category=category, limit=limit)
            db.session.add(budget)
    db.session.commit()

# Create database and tables
with app.app_context():
    db.create_all()
    init_budgets()

# Helper functions for enhanced UI
def get_daily_average():
    # Calculate daily average spending for the current month
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    
    # Get total expenses for the month
    monthly_total = db.session.query(db.func.sum(Expense.amount))\
        .filter(Expense.date >= first_day, Expense.date <= today)\
        .scalar() or 0
    
    # Calculate number of days passed in the month
    days_passed = (today - first_day).days + 1
    
    return monthly_total / days_passed if days_passed > 0 else 0

def get_days_remaining():
    # Calculate days remaining in the current month
    today = datetime.utcnow()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)
    return (last_day - today).days

# Routes
def get_monthly_totals():
    # Get the last 6 months of data
    today = datetime.utcnow()
    months = []
    monthly_totals = []
    
    for i in range(5, -1, -1):
        # Calculate start and end of the month
        month_date = today - relativedelta(months=i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + relativedelta(months=1, days=-1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get total expenses for the month
        total = db.session.query(db.func.sum(Expense.amount))\
            .filter(Expense.date >= month_start, Expense.date <= month_end)\
            .scalar() or 0
            
        months.append(month_start.strftime('%b %Y'))
        monthly_totals.append(float(total))
    
    return months, monthly_totals

@app.route('/')
def index():
    # Calculate total expenses
    total = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    # Get all expenses for the current month
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)
    
    # Get monthly expenses by category
    monthly_expenses = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= first_day,
        Expense.date <= last_day
    ).group_by(Expense.category).all()
    
    # Convert to dictionary for easier access in template
    monthly_expenses_dict = {category: float(total) for category, total in monthly_expenses}
    
    # Get all budgets
    budgets = {b.category: float(b.limit) for b in Budget.query.all()}
    
    # Calculate remaining budgets
    remaining_budgets = {}
    for category, budget in budgets.items():
        spent = monthly_expenses_dict.get(category, 0)
        remaining_budgets[category] = budget - spent
    
    # Get recent expenses (last 10)
    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(10).all()
    
    # Calculate stats for the dashboard
    daily_average = get_daily_average()
    days_remaining = get_days_remaining()
    
    # Get monthly trend data
    months, monthly_totals = get_monthly_totals()
    
    return render_template(
        'index.html',
        total=total,
        monthly_expenses=monthly_expenses_dict,
        budgets=budgets,
        remaining_budgets=remaining_budgets,
        expenses=recent_expenses,
        current_month=today.strftime('%B %Y'),
        daily_average=daily_average,
        days_remaining_in_month=days_remaining,
        total_expenses=Expense.query.count(),
        months=json.dumps(months),  # Pass as JSON for JavaScript
        monthly_totals=json.dumps(monthly_totals)  # Pass as JSON for JavaScript
    )

@app.route('/add', methods=['POST'])
def add_expense():
    try:
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        
        if not amount or not category:
            flash('Amount and category are required!', 'error')
            return redirect(url_for('index'))
            
        new_expense = Expense(
            amount=amount,
            category=category,
            description=description
        )
        
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
    except ValueError:
        flash('Please enter a valid amount!', 'error')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the expense.', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/update_budget', methods=['POST'])
def update_budget():
    data = request.get_json()
    category = data.get('category')
    limit = float(data.get('limit', 0))
    
    budget = Budget.query.filter_by(category=category).first()
    if budget:
        budget.limit = limit
    else:
        budget = Budget(category=category, limit=limit)
        db.session.add(budget)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/get_expense_data')
def get_expense_data():
    # Get category-wise expenses for the current month
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)
    
    expenses = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= first_day,
        Expense.date <= last_day
    ).group_by(Expense.category).all()
    
    # Get budget limits
    budgets = {b.category: b.limit for b in Budget.query.all()}
    
    # Format data for charts
    categories = []
    spent = []
    limits = []
    
    for category, amount in expenses:
        categories.append(category)
        spent.append(float(amount))
        limits.append(float(budgets.get(category, 0)))
    
    return jsonify({
        'categories': categories,
        'spent': spent,
        'limits': limits
    })

@app.route('/get_monthly_category_data')
def get_monthly_category_data():
    # Get current month's expenses by category
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)
    
    monthly_expenses = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= first_day,
        Expense.date <= last_day
    ).group_by(Expense.category).all()
    
    categories = []
    amounts = []
    
    for category, amount in monthly_expenses:
        categories.append(category)
        amounts.append(float(amount))
    
    return jsonify({
        'categories': categories,
        'amounts': amounts
    })

@app.route('/get_savings_suggestions')
def get_savings_suggestions():
    # Get current month's expenses by category
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)
    
    monthly_expenses = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= first_day,
        Expense.date <= last_day
    ).group_by(Expense.category).all()
    
    # Get budget limits
    budgets = {b.category: b.limit for b in Budget.query.all()}
    
    suggestions = []
    
    for category, spent in monthly_expenses:
        budget = budgets.get(category, 0)
        if spent > budget:
            overspend = spent - budget
            suggestions.append({
                'category': category,
                'message': f'You\'ve overspent ₹{overspend:.2f} on {category}. Try to reduce expenses in this category next month.'
            })
    
    # Add general savings tips
    if not suggestions:
        suggestions.append({
            'category': 'Good job!',
            'message': 'You\'re staying within your budget. Keep it up!'
        })
    else:
        suggestions.append({
            'category': 'Tip',
            'message': 'Consider setting aside 20% of your income for savings before spending on other categories.'
        })
    
    return jsonify({'suggestions': suggestions})

# Add template filters
@app.template_filter('get_category_color')
def get_category_color(category):
    """Return a color for the category"""
    colors = {
        'Food': '#FF6384',
        'Transportation': '#36A2EB',
        'Housing': '#FFCE56',
        'Utilities': '#4BC0C0',
        'Entertainment': '#9966FF',
        'Healthcare': '#FF9F40',
        'Shopping': '#C9CBCF',
        'Other': '#28A745'
    }
    return colors.get(category, '#6C757D')

@app.template_filter('get_category_icon')
def get_category_icon(category):
    """Return a Font Awesome icon for the category"""
    icons = {
        'Food': 'fas fa-utensils',
        'Transportation': 'fas fa-car',
        'Housing': 'fas fa-home',
        'Utilities': 'fas fa-bolt',
        'Entertainment': 'fas fa-film',
        'Healthcare': 'fas fa-heartbeat',
        'Shopping': 'fas fa-shopping-bag',
        'Other': 'fas fa-ellipsis-h'
    }
    return icons.get(category, 'fas fa-tag')

def init_budgets():
    if Budget.query.count() == 0:
        default_budgets = [
            Budget(category='Food', limit=10000),
            Budget(category='Transportation', limit=5000),
            Budget(category='Housing', limit=15000),
            Budget(category='Utilities', limit=5000),
            Budget(category='Entertainment', limit=3000),
            Budget(category='Healthcare', limit=2000),
            Budget(category='Shopping', limit=5000),
            Budget(category='Other', limit=3000)
        ]
        db.session.bulk_save_objects(default_budgets)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_budgets()
    
    # For production
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

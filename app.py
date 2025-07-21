from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

app = Flask(__name__)
#app.secret_key = 'secret-key-here'  # Change this in production

# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['survey_db']
collection = db['participant_data']

@app.route('/')
def index():
    return render_template('survey.html')

@app.route('/submit', methods=['POST'])
def submit_survey():
    try:
        # Extract form data
        age = request.form.get('age', type=int)
        gender = request.form.get('gender')
        total_income = request.form.get('total_income', type=float)
        
        # Validate required fields
        if not all([age, gender, total_income]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('index'))
        
        # Extract expense data
        expenses = {}
        expense_categories = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
        
        for category in expense_categories:
            if request.form.get(f'{category}_checkbox'):
                amount = request.form.get(f'{category}_amount', type=float)
                if amount and amount > 0:
                    expenses[category] = amount
        
        # Calculate total expenses
        total_expenses = sum(expenses.values())
        
        # Prepare document for MongoDB
        participant_data = {
            'age': age,
            'gender': gender,
            'total_income': total_income,
            'expenses': expenses,
            'total_expenses': total_expenses,
            'savings': total_income - total_expenses,
            'submission_date': datetime.now()
        }
        
        # Insert into MongoDB
        result = collection.insert_one(participant_data)
        
        if result.inserted_id:
            flash('Survey submitted successfully! Thank you for your participation.', 'success')
        else:
            flash('There was an error submitting your survey. Please try again.', 'error')
            
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Simple dashboard to view collected data"""
    try:
        # Get all survey data
        surveys = list(collection.find().sort('submission_date', -1))
        
        # Convert ObjectId to string for JSON serialization
        for survey in surveys:
            survey['_id'] = str(survey['_id'])
            survey['submission_date'] = survey['submission_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate basic statistics
        if surveys:
            total_participants = len(surveys)
            avg_income = sum(s['total_income'] for s in surveys) / total_participants
            avg_expenses = sum(s['total_expenses'] for s in surveys) / total_participants
            avg_savings = sum(s['savings'] for s in surveys) / total_participants
            
            stats = {
                'total_participants': total_participants,
                'avg_income': round(avg_income, 2),
                'avg_expenses': round(avg_expenses, 2),
                'avg_savings': round(avg_savings, 2)
            }
        else:
            stats = None
        
        return render_template('dashboard.html', surveys=surveys, stats=stats)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/data')
def api_data():
    """API endpoint to get survey data in JSON format"""
    try:
        surveys = list(collection.find())
        
        # Convert ObjectId and datetime for JSON serialization
        for survey in surveys:
            survey['_id'] = str(survey['_id'])
            survey['submission_date'] = survey['submission_date'].isoformat()
        
        return jsonify(surveys)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
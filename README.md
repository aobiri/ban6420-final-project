# ban6420-final-project
Nexford - Programming in R and Python - Final Project

# Healthcare Survey Tool - Flask Application

## Project Structure
```
healthcare-survey/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── survey.html       # Main survey form
│   └── dashboard.html    # Data dashboard
├── static/               # (Optional) CSS/JS files
└── README.md            # This file
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. MongoDB Setup
Make sure MongoDB is installed and running on your system:

**Option A: Local MongoDB**
- Install MongoDB from https://www.mongodb.com/try/download/community
- Start MongoDB service:
  ```bash
  # On Windows
  net start MongoDB
  
  # On macOS
  brew services start mongodb/brew/mongodb-community
  
  # On Linux
  sudo systemctl start mongod
  ```

**Option B: MongoDB Atlas (Cloud)**
- Create a free cluster at https://www.mongodb.com/cloud/atlas
- Get your connection string and set the MONGO_URI environment variable:
  ```bash
  export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/survey_database"
  ```
  or, when running locally:
  ```bash
  export MONGO_URI="mongodb://localhost:27017/survey_db"
  ```

### 3. Environment Variables
Create a `.env` file (optional):
```
MONGO_URI=mongodb://localhost:27017/
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. Run the Application
```bash
python app.py
```

The application will be available at: http://localhost:5000
But remotely on AWS at: http://52.22.160.93:5000/


## Features

### Survey Form (`/`)
- Collects participant demographics (age, gender)
- Records total monthly income
- Captures expense data across 5 categories:
  - Utilities (electricity, water, gas, internet)
  - Entertainment (movies, dining, hobbies)
  - School Fees (tuition, education costs)
  - Shopping (clothing, groceries, household items)
  - Healthcare (medical, insurance, medications)
- Client-side validation and expense vs income checking
- Responsive design for mobile and desktop

### Dashboard (`/dashboard`) # (Additional)
- Summary statistics (total participants, averages)
- Detailed participant data table
- Expense breakdown per participant
- Real-time data updates


## MongoDB Schema

Each survey submission creates a document with this structure:
```json
{
  "_id": "ObjectId",
  "age": 35,
  "gender": "Female",
  "total_income": 5000.00,
  "expenses": {
    "utilities": 400.00,
    "healthcare": 300.00,
    "shopping": 800.00
  },
  "total_expenses": 1500.00,
  "savings": 3500.00,
  "submission_date": "2025-07-21T10:30:00.000Z"
}
```

## 5. Enter the fields in the survey and click on the submit button to save some data

## 6. Run the User python file to collect the saved data into a .csv file
```bash
python User.py
```
## Data Analysis Integration

### For Python Users
```python
import requests
import pandas as pd

# Fetch data from API
self.client = MongoClient(self.mongo_uri)
self.db = self.client['survey_db']
self.collection = self.db['participant_data']
# Fetch all documents from MongoDB
documents = list(self.collection.find())

# Loop and write to Csv
for user in self.users:
    writer.writerow(user.to_dict())
```

## 6. Run the jupyer-notebook-analysis python file to convert the data in the .csv file into data visualization
```bash
python jupyer-notebook-analysis.py
```

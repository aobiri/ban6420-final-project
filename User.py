import csv
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class User:
    """
    User class to represent survey participants and handle data operations.
    """
    
    def __init__(self, age: int, gender: str, total_income: float, 
                 expenses: Dict[str, float], submission_date: Optional[datetime] = None,
                 user_id: Optional[str] = None):
        """
        Initialize a User object with survey data.
        
        Args:
            age (int): User's age
            gender (str): User's gender
            total_income (float): User's total monthly income
            expenses (Dict[str, float]): Dictionary of expense categories and amounts
            submission_date (datetime, optional): When the survey was submitted
            user_id (str, optional): Unique identifier for the user
        """
        self.user_id = user_id
        self.age = age
        self.gender = gender
        self.total_income = total_income
        self.expenses = expenses if expenses else {}
        self.submission_date = submission_date if submission_date else datetime.now()
        
        # Calculate derived fields
        self.total_expenses = sum(self.expenses.values())
        self.savings = self.total_income - self.total_expenses
        self.savings_rate = (self.savings / self.total_income) * 100 if self.total_income > 0 else 0
    """
    Below functions are only Useful for CRUD operations on User objects, such as adding, removing, or updating expenses.
    """
    def get_expense_by_category(self, category: str) -> float:
        """Get expense amount for a specific category."""
        return self.expenses.get(category, 0.0)
    
    def add_expense(self, category: str, amount: float):
        """Add or update an expense category."""
        self.expenses[category] = amount
        self._recalculate_totals()
    
    def remove_expense(self, category: str):
        """Remove an expense category."""
        if category in self.expenses:
            del self.expenses[category]
            self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalculate total expenses and savings after expense changes."""
        self.total_expenses = sum(self.expenses.values())
        self.savings = self.total_income - self.total_expenses
        self.savings_rate = (self.savings / self.total_income) * 100 if self.total_income > 0 else 0
    
    def to_dict(self) -> Dict:
        """Convert User object to dictionary for easy serialization."""
        return {
            'user_id': self.user_id,
            'age': self.age,
            'gender': self.gender,
            'total_income': self.total_income,
            'total_expenses': self.total_expenses,
            'savings': self.savings,
            'savings_rate': round(self.savings_rate, 2),
            'utilities': self.get_expense_by_category('utilities'),
            'entertainment': self.get_expense_by_category('entertainment'),
            'school_fees': self.get_expense_by_category('school_fees'),
            'shopping': self.get_expense_by_category('shopping'),
            'healthcare': self.get_expense_by_category('healthcare'),
            'submission_date': self.submission_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __str__(self) -> str:
        """String representation of User object."""
        return f"User(ID: {self.user_id}, Age: {self.age}, Income: ${self.total_income}, Savings: ${self.savings:.2f})"
    
    def __repr__(self) -> str:
        """Detailed representation of User object."""
        return f"User(user_id='{self.user_id}', age={self.age}, gender='{self.gender}', total_income={self.total_income})"


class SurveyDataManager:
    """
    Class to manage survey data operations including MongoDB connection and CSV export.
    """
    
    def __init__(self, mongo_uri: str = None):
        """
        Initialize the SurveyDataManager with MongoDB connection.
        
        Args:
            mongo_uri (str): MongoDB connection string
        """
        self.mongo_uri = mongo_uri or os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = None
        self.db = None
        self.collection = None
        self.users = []
        
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client['survey_db']
            self.collection = self.db['participant_data']
            print(f"✅ Connected to MongoDB successfully")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
    
    def load_data_from_mongodb(self) -> List[User]:
        """
        Load all survey data from MongoDB and convert to User objects.
        
        Returns:
            List[User]: List of User objects
        """
        try:
            #if not self.collection:
            #    raise Exception("MongoDB connection not established")
            
            # Fetch all documents from MongoDB
            documents = list(self.collection.find())
            self.users = []
            
            print(f"📊 Found {len(documents)} survey responses in MongoDB")
            
            for doc in documents:
                # Convert MongoDB document to User object
                user = User(
                    user_id=str(doc.get('_id')),
                    age=doc.get('age'),
                    gender=doc.get('gender'),
                    total_income=doc.get('total_income'),
                    expenses=doc.get('expenses', {}),
                    submission_date=doc.get('submission_date')
                )
                self.users.append(user)
            
            print(f"✅ Successfully loaded {len(self.users)} User objects")
            return self.users
            
        except Exception as e:
            print(f"❌ Error loading data from MongoDB: {str(e)}")
            return []
    
    def add_sample_data(self):
        """Add sample data for testing purposes."""
        sample_users = [
            User(25, "Female", 4500, {"utilities": 300, "healthcare": 200, "shopping": 600}),
            User(32, "Male", 6000, {"utilities": 400, "entertainment": 500, "healthcare": 300, "shopping": 800}),
            User(28, "Female", 5200, {"utilities": 350, "school_fees": 1200, "healthcare": 250, "shopping": 500}),
            User(35, "Male", 7500, {"utilities": 450, "entertainment": 600, "healthcare": 400, "shopping": 1000}),
            User(29, "Other", 4800, {"utilities": 320, "entertainment": 400, "healthcare": 180, "shopping": 650})
        ]
        
        for i, user in enumerate(sample_users):
            user.user_id = f"sample_{i+1}"
        
        self.users.extend(sample_users)
        print(f"✅ Added {len(sample_users)} sample users for testing")
    
    def export_to_csv(self, filename: str = "survey_data.csv") -> bool:
        """
        Export User objects to CSV file.
        
        Args:
            filename (str): Output CSV filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.users:
                print("⚠️ No user data available. Loading from MongoDB...")
                self.load_data_from_mongodb()
                
                if not self.users:
                    print("⚠️ Still no data. Adding sample data for demonstration...")
                    self.add_sample_data()
            
            # Define CSV headers
            headers = [
                'user_id', 'age', 'gender', 'total_income', 'total_expenses', 
                'savings', 'savings_rate', 'utilities', 'entertainment', 
                'school_fees', 'shopping', 'healthcare', 'submission_date'
            ]
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for user in self.users:
                    writer.writerow(user.to_dict())
            
            print(f"✅ Successfully exported {len(self.users)} records to '{filename}'")
            print(f"📁 File location: {os.path.abspath(filename)}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {str(e)}")
            return False
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of the survey data."""
        if not self.users:
            return {}
        
        ages = [user.age for user in self.users]
        incomes = [user.total_income for user in self.users]
        expenses = [user.total_expenses for user in self.users]
        savings = [user.savings for user in self.users]
        
        return {
            'total_participants': len(self.users),
            'avg_age': sum(ages) / len(ages),
            'avg_income': sum(incomes) / len(incomes),
            'avg_expenses': sum(expenses) / len(expenses),
            'avg_savings': sum(savings) / len(savings),
            'gender_distribution': self._get_gender_distribution(),
            'expense_categories': self._get_expense_category_stats()
        }
    
    def _get_gender_distribution(self) -> Dict[str, int]:
        """Get gender distribution statistics."""
        gender_count = {}
        for user in self.users:
            gender_count[user.gender] = gender_count.get(user.gender, 0) + 1
        return gender_count
    
    def _get_expense_category_stats(self) -> Dict[str, float]:
        """Get average expenses by category."""
        categories = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
        category_totals = {cat: 0 for cat in categories}
        category_counts = {cat: 0 for cat in categories}
        
        for user in self.users:
            for category in categories:
                amount = user.get_expense_by_category(category)
                if amount > 0:
                    category_totals[category] += amount
                    category_counts[category] += 1
        
        return {
            cat: (category_totals[cat] / category_counts[cat]) if category_counts[cat] > 0 else 0
            for cat in categories
        }
    
    def close_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")


def main():
    """
    Main function to demonstrate the User class and data export functionality.
    """
    print("🚀 Starting Survey Data Export Process...")
    print("=" * 50)
    
    # Initialize the data manager
    data_manager = SurveyDataManager()
    
    # Load data from MongoDB (or add sample data if no MongoDB data exists)
    users = data_manager.load_data_from_mongodb()
    
    # If no data in MongoDB, add sample data for demonstration
    if not users:
        print("📝 No data found in MongoDB. Adding sample data...")
        data_manager.add_sample_data()
    
    # Display summary statistics
    print("\n📈 Survey Data Summary:")
    print("-" * 30)
    stats = data_manager.get_summary_statistics()
    if stats:
        print(f"Total Participants: {stats['total_participants']}")
        print(f"Average Age: {stats['avg_age']:.1f} years")
        print(f"Average Income: ${stats['avg_income']:.2f}")
        print(f"Average Expenses: ${stats['avg_expenses']:.2f}")
        print(f"Average Savings: ${stats['avg_savings']:.2f}")
        print(f"Gender Distribution: {stats['gender_distribution']}")
    
    # Export to CSV
    print(f"\n💾 Exporting data to CSV...")
    success = data_manager.export_to_csv("healthcare_survey_data.csv")
    
    if success:
        print("\n✅ Export completed successfully!")
        print("🔍 You can now load 'healthcare_survey_data.csv' into your Jupyter notebook")
        print("\n📋 Next steps:")
        print("1. Open Jupyter Notebook")
        print("2. Use: df = pd.read_csv('healthcare_survey_data.csv')")
        print("3. Start your data analysis!")
    
    # Close connections
    data_manager.close_connection()
    print("\n🏁 Process completed!")


if __name__ == "__main__":
    main()

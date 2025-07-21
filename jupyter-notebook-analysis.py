# Healthcare Survey Data Analysis
# Jupyter Notebook for analyzing survey data exported from MongoDB

import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("🔬 Healthcare Survey Data Analysis")
print("=" * 50)

# =============================================================================
# STEP 1: Load and Explore the Data
# =============================================================================

def load_survey_data(filename='healthcare_survey_data.csv'):
    """Load the CSV file exported from the Flask application."""
    try:
        df = pd.read_csv(filename)
        print(f"✅ Successfully loaded {len(df)} survey responses")
        print(f"📊 Dataset shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found. Please run the export script first.")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None

# Load the data
df = load_survey_data()

if df is not None:
    print("\n📋 Dataset Overview:")
    print("-" * 30)
    print(df.info())
    
    print("\n📈 Basic Statistics:")
    print("-" * 30)
    print(df.describe())
    
    print("\n👥 First 5 Survey Responses:")
    print("-" * 30)
    print(df.head())

# =============================================================================
# STEP 2: Data Cleaning and Preprocessing
# =============================================================================

def clean_and_preprocess_data(df):
    """Clean and preprocess the survey data."""
    if df is None:
        return None
    
    print("\n🧹 Data Cleaning and Preprocessing...")
    print("-" * 40)
    
    # Convert submission_date to datetime
    df['submission_date'] = pd.to_datetime(df['submission_date'])
    
    # Check for missing values
    missing_values = df.isnull().sum()
    print("Missing Values:")
    print(missing_values[missing_values > 0])
    
    # Fill missing expense categories with 0
    expense_columns = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
    df[expense_columns] = df[expense_columns].fillna(0)
    
    # Create age groups
    df['age_group'] = pd.cut(df['age'], bins=[17, 25, 35, 45, 100], 
                            labels=['18-25', '26-35', '36-45', '46+'])
    
    # Create income groups
    income_quartiles = df['total_income'].quantile([0.25, 0.5, 0.75])
    df['income_group'] = pd.cut(df['total_income'], 
                               bins=[0, income_quartiles[0.25], income_quartiles[0.5], 
                                    income_quartiles[0.75], float('inf')],
                               labels=['Low', 'Medium-Low', 'Medium-High', 'High'])
    
    # Create savings status
    df['savings_status'] = df['savings'].apply(lambda x: 'Positive' if x > 0 else 'Negative' if x < 0 else 'Break-even')
    
    print(f"✅ Data cleaning completed. Final shape: {df.shape}")
    return df

# Clean the data
df_clean = clean_and_preprocess_data(df)

# =============================================================================
# STEP 3: Exploratory Data Analysis (EDA)
# =============================================================================

def perform_eda(df):
    """Perform comprehensive exploratory data analysis."""
    if df is None:
        return
    
    print("\n🔍 Exploratory Data Analysis")
    print("=" * 40)
    
    # Set up the plotting area
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Healthcare Survey Data Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Age Distribution
    axes[0, 0].hist(df['age'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_title('Age Distribution')
    axes[0, 0].set_xlabel('Age')
    axes[0, 0].set_ylabel('Frequency')

    # 2. Ages with the highest income
    highest_income_age = df.loc[df['total_income'] == df['total_income'].max(), 'age']
    axes[0, 1].set_title('Highest Income by Age')
    axes[0, 1].axvline(highest_income_age.mean(), color='green', linestyle='dashed', linewidth=2, label='Highest Income Age')
    axes[0, 1].legend()
    
    # 3. Gender Distribution
    gender_counts = df['gender'].value_counts()
    axes[0, 2].pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 2].set_title('Gender Distribution')
    
    # 4. Income Distribution
    axes[1, 0].hist(df['total_income'], bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[1, 0].set_title('Income Distribution')
    axes[1, 0].set_xlabel('Total Income ($)')
    axes[1, 0].set_ylabel('Frequency')
    
    # 5. Expense Categories Comparison
    expense_cols = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
    expense_means = df[expense_cols].mean()
    axes[1, 1].bar(expense_means.index, expense_means.values, color='coral')
    axes[1, 1].set_title('Average Expenses by Category')
    axes[1, 1].set_xlabel('Expense Category')
    axes[1, 1].set_ylabel('Average Amount ($)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # 6. Healthcare Spending by Age Group
    if 'age_group' in df.columns:
        healthcare_by_age = df.groupby('age_group')['healthcare'].mean()
        axes[1, 2].bar(healthcare_by_age.index, healthcare_by_age.values, color='lightcoral')
        axes[1, 2].set_title('Average Healthcare Spending by Age Group')
        axes[1, 2].set_xlabel('Age Group')
        axes[1, 2].set_ylabel('Healthcare Spending ($)')
    
    
    plt.tight_layout()
    plt.show()
    
    return fig

# Perform EDA
if df_clean is not None:
    eda_fig = perform_eda(df_clean)


# =============================================================================
# STEP 6: Export Results
# =============================================================================

def export_analysis_results(df, filename_prefix='healthcare_analysis'):
    """Export analysis results to various formats."""
    if df is None:
        return
    
    print(f"\n💾 Exporting Analysis Results...")
    print("-" * 35)
    
    # Export cleaned data
    df.to_csv(f'{filename_prefix}_cleaned.csv', index=False)
    print(f"✅")
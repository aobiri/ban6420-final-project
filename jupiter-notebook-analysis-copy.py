# Healthcare Survey Data Analysis
# Jupyter Notebook for analyzing survey data exported from MongoDB

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
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
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Healthcare Survey Data Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Age Distribution
    axes[0, 0].hist(df['age'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].set_title('Age Distribution')
    axes[0, 0].set_xlabel('Age')
    axes[0, 0].set_ylabel('Frequency')
    
    # 2. Gender Distribution
    gender_counts = df['gender'].value_counts()
    axes[0, 1].pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Gender Distribution')
    
    # 3. Income Distribution
    axes[0, 2].hist(df['total_income'], bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0, 2].set_title('Income Distribution')
    axes[0, 2].set_xlabel('Total Income ($)')
    axes[0, 2].set_ylabel('Frequency')
    
    # 4. Expense Categories Comparison
    expense_cols = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
    expense_means = df[expense_cols].mean()
    axes[1, 0].bar(expense_means.index, expense_means.values, color='coral')
    axes[1, 0].set_title('Average Expenses by Category')
    axes[1, 0].set_xlabel('Expense Category')
    axes[1, 0].set_ylabel('Average Amount ($)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 5. Income vs Savings Scatter Plot
    
    colors = {'Male': 'blue', 'Female': 'red', 'Other': 'green', 'Prefer not to say': 'purple'}
    for gender in df['gender'].unique():
        gender_data = df[df['gender'] == gender]
        axes[1, 1].scatter(gender_data['total_income'], gender_data['savings'], 
                          label=gender, alpha=0.6, c=colors.get(gender, 'gray'))
    axes[1, 1].set_title('Income vs Savings by Gender')
    axes[1, 1].set_xlabel('Total Income ($)')
    axes[1, 1].set_ylabel('Savings ($)')
    axes[1, 1].legend()
    
    # 6. Savings Rate Distribution
    axes[1, 2].hist(df['savings_rate'], bins=15, alpha=0.7, color='gold', edgecolor='black')
    axes[1, 2].set_title('Savings Rate Distribution')
    axes[1, 2].set_xlabel('Savings Rate (%)')
    axes[1, 2].set_ylabel('Frequency')
    
    # 7. Healthcare Spending by Age Group
    if 'age_group' in df.columns:
        healthcare_by_age = df.groupby('age_group')['healthcare'].mean()
        axes[2, 0].bar(healthcare_by_age.index, healthcare_by_age.values, color='lightcoral')
        axes[2, 0].set_title('Average Healthcare Spending by Age Group')
        axes[2, 0].set_xlabel('Age Group')
        axes[2, 0].set_ylabel('Healthcare Spending ($)')
    
    # 8. Income Group Distribution
    if 'income_group' in df.columns:
        income_group_counts = df['income_group'].value_counts()
        axes[2, 1].bar(income_group_counts.index, income_group_counts.values, color='lightblue')
        axes[2, 1].set_title('Income Group Distribution')
        axes[2, 1].set_xlabel('Income Group')
        axes[2, 1].set_ylabel('Number of Participants')
    
    # 9. Savings Status
    if 'savings_status' in df.columns:
        savings_counts = df['savings_status'].value_counts()
        colors_savings = ['green', 'red', 'orange']
        axes[2, 2].pie(savings_counts.values, labels=savings_counts.index, autopct='%1.1f%%', 
                      colors=colors_savings, startangle=90)
        axes[2, 2].set_title('Savings Status Distribution')
    
    plt.tight_layout()
    plt.show()
    
    return fig

# Perform EDA
if df_clean is not None:
    eda_fig = perform_eda(df_clean)

# =============================================================================
# STEP 4: Statistical Analysis
# =============================================================================

def statistical_analysis(df):
    """Perform statistical tests and analysis."""
    if df is None:
        return
    
    print("\n📊 Statistical Analysis")
    print("=" * 30)
    
    # Correlation Analysis
    print("🔗 Correlation Analysis:")
    numeric_cols = ['age', 'total_income', 'total_expenses', 'savings', 'utilities', 
                   'entertainment', 'school_fees', 'shopping', 'healthcare']
    correlation_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, fmt='.2f')
    plt.title('Correlation Matrix of Survey Variables')
    plt.tight_layout()
    plt.show()
    
    # Gender-based Analysis
    print("\n👥 Gender-based Analysis:")
    print("-" * 25)
    gender_stats = df.groupby('gender')[['total_income', 'total_expenses', 'savings', 'healthcare']].agg(['mean', 'std'])
    print(gender_stats.round(2))
    
    # Healthcare Spending Analysis (Key for product launch)
    print("\n🏥 Healthcare Spending Analysis:")
    print("-" * 35)
    
    # Healthcare spending by income group
    if 'income_group' in df.columns:
        healthcare_by_income = df.groupby('income_group')['healthcare'].agg(['mean', 'median', 'std', 'count'])
        print("Healthcare Spending by Income Group:")
        print(healthcare_by_income.round(2))
    
    # Statistical tests
    print("\n📈 Statistical Tests:")
    print("-" * 20)
    
    # Test if healthcare spending differs by gender
    gender_groups = [group['healthcare'].values for name, group in df.groupby('gender') if len(group) > 1]
    if len(gender_groups) >= 2:
        f_stat, p_value = stats.f_oneway(*gender_groups)
        print(f"ANOVA - Healthcare spending by gender: F-stat={f_stat:.3f}, p-value={p_value:.3f}")
        print(f"Significant difference: {'Yes' if p_value < 0.05 else 'No'}")
    
    # Correlation between income and healthcare spending
    income_healthcare_corr, p_val = stats.pearsonr(df['total_income'], df['healthcare'])
    print(f"Income-Healthcare correlation: r={income_healthcare_corr:.3f}, p-value={p_val:.3f}")

# Perform statistical analysis
if df_clean is not None:
    statistical_analysis(df_clean)

# =============================================================================
# STEP 5: Healthcare Market Insights
# =============================================================================

def healthcare_market_insights(df):
    """Generate insights specifically for healthcare product launch."""
    if df is None:
        return
    
    print("\n🎯 Healthcare Market Insights for Product Launch")
    print("=" * 50)
    
    # Healthcare spending patterns
    total_participants = len(df)
    healthcare_spenders = len(df[df['healthcare'] > 0])
    avg_healthcare_spending = df[df['healthcare'] > 0]['healthcare'].mean()
    
    print(f"📊 Market Overview:")
    print(f"   • Total survey participants: {total_participants}")
    print(f"   • Participants spending on healthcare: {healthcare_spenders} ({healthcare_spenders/total_participants*100:.1f}%)")
    print(f"   • Average monthly healthcare spending: ${avg_healthcare_spending:.2f}")
    
    # Target segments
    print(f"\n🎯 Target Market Segments:")
    
    # High healthcare spenders
    high_healthcare = df[df['healthcare'] >= df['healthcare'].quantile(0.75)]
    print(f"   • High healthcare spenders (top 25%): {len(high_healthcare)} people")
    print(f"     - Average age: {high_healthcare['age'].mean():.1f} years")
    print(f"     - Average income: ${high_healthcare['total_income'].mean():.0f}")
    print(f"     - Average healthcare spending: ${high_healthcare['healthcare'].mean():.2f}")
    
    # Healthcare spending by demographics
    print(f"\n📈 Healthcare Spending by Demographics:")
    
    # By age group
    if 'age_group' in df.columns:
        age_healthcare = df.groupby('age_group')['healthcare'].agg(['mean', 'count'])
        print(f"\n   Age Group Analysis:")
        for age_group, data in age_healthcare.iterrows():
            print(f"     • {age_group}: ${data['mean']:.2f}/month ({data['count']} people)")
    
    # By income level
    if 'income_group' in df.columns:
        income_healthcare = df.groupby('income_group')['healthcare'].agg(['mean', 'count'])
        print(f"\n   Income Level Analysis:")
        for income_group, data in income_healthcare.iterrows():
            print(f"     • {income_group} income: ${data['mean']:.2f}/month ({data['count']} people)")
    
    # Market opportunity
    print(f"\n💰 Market Opportunity:")
    total_monthly_healthcare_market = df['healthcare'].sum()
    avg_disposable_income = df['savings'].mean()
    print(f"   • Total monthly healthcare market: ${total_monthly_healthcare_market:.0f}")
    print(f"   • Average disposable income (savings): ${avg_disposable_income:.2f}")
    print(f"   • Participants with positive savings: {len(df[df['savings'] > 0])}/{total_participants}")
    
    # Recommendations
    print(f"\n💡 Product Launch Recommendations:")
    print(f"   1. Primary target: {high_healthcare['age'].mode().iloc[0]:.0f}-year-olds with ${high_healthcare['total_income'].mean():.0f}+ income")
    print(f"   2. Price point: Consider ${avg_healthcare_spending*.10:.0f}-${avg_healthcare_spending*.25:.0f}/month range")
    print(f"   3. Market size: Focus on {healthcare_spenders} active healthcare consumers")
    
    # Healthcare spending visualization
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: Healthcare spending distribution
    plt.subplot(2, 2, 1)
    healthcare_data = df[df['healthcare'] > 0]['healthcare']
    plt.hist(healthcare_data, bins=15, alpha=0.7, color='lightcoral', edgecolor='black')
    plt.axvline(healthcare_data.mean(), color='red', linestyle='--', label=f'Mean: ${healthcare_data.mean():.2f}')
    plt.axvline(healthcare_data.median(), color='blue', linestyle='--', label=f'Median: ${healthcare_data.median():.2f}')
    plt.title('Healthcare Spending Distribution')
    plt.xlabel('Monthly Healthcare Spending ($)')
    plt.ylabel('Number of Participants')
    plt.legend()
    
    # Subplot 2: Healthcare spending by age
    plt.subplot(2, 2, 2)
    plt.scatter(df['age'], df['healthcare'], alpha=0.6, color='green')
    plt.title('Healthcare Spending by Age')
    plt.xlabel('Age (years)')
    plt.ylabel('Healthcare Spending ($)')
    
    # Subplot 3: Healthcare vs Income
    plt.subplot(2, 2, 3)
    plt.scatter(df['total_income'], df['healthcare'], alpha=0.6, color='purple')
    plt.title('Healthcare Spending vs Income')
    plt.xlabel('Total Income ($)')
    plt.ylabel('Healthcare Spending ($)')
    
    # Subplot 4: Healthcare spending as % of income
    plt.subplot(2, 2, 4)
    df['healthcare_pct'] = (df['healthcare'] / df['total_income']) * 100
    plt.hist(df[df['healthcare_pct'] < 50]['healthcare_pct'], bins=15, alpha=0.7, color='orange', edgecolor='black')
    plt.title('Healthcare Spending as % of Income')
    plt.xlabel('Healthcare Spending (% of Income)')
    plt.ylabel('Number of Participants')
    
    plt.tight_layout()
    plt.show()

# Generate healthcare market insights
if df_clean is not None:
    healthcare_market_insights(df_clean)

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
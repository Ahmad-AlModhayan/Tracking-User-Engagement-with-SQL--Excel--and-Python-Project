"""
User Engagement Analysis
Analyzes user engagement metrics across different subscription periods.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as scipy_stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# File paths
DATA_DIR = "../data"
DATA_FILES = {
    "q2_2021_paid_0": f"{DATA_DIR}/minutes_watched_2021_paid_0.csv",
    "q2_2021_paid_1": f"{DATA_DIR}/minutes_watched_2021_paid_1.csv",
    "q2_2022_paid_0": f"{DATA_DIR}/minutes_watched_2022_paid_0.csv",
    "q2_2022_paid_1": f"{DATA_DIR}/minutes_watched_2022_paid_1.csv",
    "certificates": f"{DATA_DIR}/minutes_and_certificates.csv"
}

def load_data():
    """Load all datasets with proper column names."""
    data = {}
    for key, path in DATA_FILES.items():
        if key == "certificates":
            columns = ["student_id", "minutes_watched", "certificates_issued"]
        else:
            columns = ["student_id", "minutes_watched", "paid_in_q2"]
        data[key] = pd.read_csv(path, names=columns)
    return data

def remove_outliers(df, column, threshold=0.99):
    """Remove outliers above the specified percentile."""
    limit = df[column].quantile(threshold)
    return df[df[column] < limit].copy()

def calculate_percentiles(df, column="minutes_watched"):
    """Calculate key percentiles for a given column."""
    percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]
    return pd.Series({f"{int(p*100)}th": df[column].quantile(p) for p in percentiles})

def export_to_excel(data, filename="../excel/engagement_analysis.xlsx"):
    """Export all analysis results to Excel."""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # 1. Summary Statistics Sheet
        summary_stats = []
        for key, df in data.items():
            if key != "certificates":
                stats = {
                    "Dataset": key,
                    "Mean Minutes": df["minutes_watched"].mean(),
                    "Median Minutes": df["minutes_watched"].median(),
                    "Std Dev": df["minutes_watched"].std(),
                    "Total Users": len(df),
                    "Total Hours": df["minutes_watched"].sum() / 60
                }
                percentiles = calculate_percentiles(df)
                stats.update(percentiles)
                summary_stats.append(stats)
        
        pd.DataFrame(summary_stats).to_excel(writer, sheet_name="Summary Stats", index=False)
        
        # 2. Year-over-Year Comparison
        yoy_comparison = pd.DataFrame({
            "Metric": [
                "Free Users Count", "Free Avg Minutes",
                "Paid Users Count", "Paid Avg Minutes"
            ],
            "Q2 2021": [
                len(data["q2_2021_paid_0"]),
                data["q2_2021_paid_0"]["minutes_watched"].mean(),
                len(data["q2_2021_paid_1"]),
                data["q2_2021_paid_1"]["minutes_watched"].mean()
            ],
            "Q2 2022": [
                len(data["q2_2022_paid_0"]),
                data["q2_2022_paid_0"]["minutes_watched"].mean(),
                len(data["q2_2022_paid_1"]),
                data["q2_2022_paid_1"]["minutes_watched"].mean()
            ]
        })
        yoy_comparison["YoY Change %"] = ((yoy_comparison["Q2 2022"] - yoy_comparison["Q2 2021"]) / 
                                        yoy_comparison["Q2 2021"] * 100)
        
        yoy_comparison.to_excel(writer, sheet_name="YoY Comparison", index=False)
        
        # 3. Engagement Buckets
        def create_engagement_buckets(df):
            buckets = pd.cut(df["minutes_watched"], 
                           bins=[0, 60, 180, 600, float('inf')],
                           labels=['0-1hr', '1-3hrs', '3-10hrs', '10+ hrs'])
            return buckets.value_counts().sort_index()
        
        engagement_buckets = pd.DataFrame({
            key: create_engagement_buckets(df)
            for key, df in data.items()
            if key != "certificates"
        })
        
        engagement_buckets.to_excel(writer, sheet_name="Engagement Buckets")
        
        # 4. Certificates Analysis
        cert_data = data["certificates"].copy()
        cert_data["engagement_level"] = pd.qcut(cert_data["minutes_watched"], q=4, 
                                              labels=["Low", "Medium", "High", "Very High"])
        
        cert_analysis = cert_data.groupby("engagement_level").agg({
            "certificates_issued": ["count", "mean", "sum"],
            "minutes_watched": ["mean", "median"]
        }).round(2)
        
        cert_analysis.to_excel(writer, sheet_name="Certificates Analysis")
        
        # 5. Raw Data (without outliers)
        for key, df in data.items():
            df.to_excel(writer, sheet_name=f"Raw_{key}", index=False)

def analyze_dependencies(data):
    """Analyze event dependencies between Q2 2021 and Q2 2022 engagement."""
    # Merge datasets to find students present in both periods
    free_2021 = set(data["q2_2021_paid_0"]["student_id"])
    free_2022 = set(data["q2_2022_paid_0"]["student_id"])
    paid_2021 = set(data["q2_2021_paid_1"]["student_id"])
    paid_2022 = set(data["q2_2022_paid_1"]["student_id"])
    
    # Calculate probabilities
    prob_free = {
        "P(2021)": len(free_2021) / (len(free_2021.union(free_2022))),
        "P(2022)": len(free_2022) / (len(free_2021.union(free_2022))),
        "P(2022|2021)": len(free_2021.intersection(free_2022)) / len(free_2021),
        "Independent?": False
    }
    
    prob_paid = {
        "P(2021)": len(paid_2021) / (len(paid_2021.union(paid_2022))),
        "P(2022)": len(paid_2022) / (len(paid_2021.union(paid_2022))),
        "P(2022|2021)": len(paid_2021.intersection(paid_2022)) / len(paid_2021),
        "Independent?": False
    }
    
    # Test for independence
    prob_free["Independent?"] = abs(prob_free["P(2022|2021)"] - prob_free["P(2022)"]) < 0.05
    prob_paid["Independent?"] = abs(prob_paid["P(2022|2021)"] - prob_paid["P(2022)"]) < 0.05
    
    return prob_free, prob_paid

def predict_certificates(data):
    """Predict certificates using linear regression."""
    X = data["certificates"][["minutes_watched"]]
    y = data["certificates"]["certificates_issued"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=365
    )
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Calculate metrics
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    
    # Predict certificates for 1200 minutes
    pred_1200 = model.predict([[1200]])[0]
    
    return {
        "coefficient": model.coef_[0],
        "intercept": model.intercept_,
        "r2_score": r2,
        "pred_1200_min": pred_1200
    }

def analyze_engagement():
    """Perform the complete engagement analysis."""
    # Load and clean data
    print("Loading and cleaning data...")
    data = load_data()
    
    # Remove outliers from engagement data
    for key in data:
        if key != "certificates":
            data[key] = remove_outliers(data[key], "minutes_watched")
    
    # Calculate statistics
    print("\nEngagement Statistics:")
    for key, df in data.items():
        if key != "certificates":
            stats = {
                "mean": df["minutes_watched"].mean(),
                "median": df["minutes_watched"].median(),
                "std": df["minutes_watched"].std(),
                "users": len(df)
            }
            print(f"\n{key}:")
            for stat_name, value in stats.items():
                print(f"{stat_name}: {value:.2f}")
    
    # Hypothesis Testing
    print("\nHypothesis Testing (2021 vs 2022):")
    
    # Test for free users
    t_stat_free, p_val_free = scipy_stats.ttest_ind(
        data["q2_2021_paid_0"]["minutes_watched"],
        data["q2_2022_paid_0"]["minutes_watched"]
    )
    
    # Test for paid users
    t_stat_paid, p_val_paid = scipy_stats.ttest_ind(
        data["q2_2021_paid_1"]["minutes_watched"],
        data["q2_2022_paid_1"]["minutes_watched"]
    )
    
    print(f"Free Users - p-value: {p_val_free:.4f}")
    print(f"Paid Users - p-value: {p_val_paid:.4f}")
    
    # Correlation Analysis
    correlation = data["certificates"][["minutes_watched", "certificates_issued"]].corr()
    print("\nCorrelation Analysis:")
    print(correlation)
    
    # Dependencies Analysis
    print("\nAnalyzing Dependencies...")
    prob_free, prob_paid = analyze_dependencies(data)
    print("\nFree Users Dependencies:")
    for k, v in prob_free.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
    print("\nPaid Users Dependencies:")
    for k, v in prob_paid.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
    
    # Prediction Analysis
    print("\nPredicting Certificates...")
    pred_results = predict_certificates(data)
    print(f"Linear Equation: y = {pred_results['coefficient']:.4f}x + {pred_results['intercept']:.4f}")
    print(f"R-squared: {pred_results['r2_score']:.4f}")
    print(f"Predicted certificates for 1200 minutes: {pred_results['pred_1200_min']:.2f}")
    
    # Export to Excel
    print("\nExporting results to Excel...")
    export_to_excel(data)
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Set style for better looking plots
    plt.style.use('seaborn')
    
    # 1. Distribution plots
    plt.figure(figsize=(15, 10))
    for i, (key, df) in enumerate(data.items(), 1):
        if key != "certificates":
            plt.subplot(2, 2, i)
            sns.histplot(data=df, x="minutes_watched", bins=50)
            plt.title(f"Minutes Watched Distribution - {key}")
            plt.xlabel("Minutes")
            plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("../excel/engagement_distributions.png")
    print("Saved engagement_distributions.png")
    plt.close()
    
    # 2. Correlation plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=data["certificates"], 
                   x="minutes_watched", 
                   y="certificates_issued",
                   alpha=0.5)
    plt.title("Minutes Watched vs Certificates")
    plt.xlabel("Minutes")
    plt.ylabel("Certificates")
    plt.savefig("../excel/certificates_correlation.png")
    print("Saved certificates_correlation.png")
    plt.close()
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_engagement()

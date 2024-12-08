## Project Overview
This project analyzes the effectiveness of platform additions (new courses, career tracks, and exams) on student engagement. By leveraging SQL, Python, and Excel, we explore subscription trends, minutes watched, and correlations between user behavior and issued certificates, leading to insights for improving engagement.

---

## Steps and Tasks

### 1. **Data Preparation with SQL**
#### I. Calculating a Subscription’s End Date
- **Objective**: Create a result set to calculate subscription end dates.
- **Steps**:
  1. Use `DATE_ADD` to calculate `date_end` for Monthly (`plan_id=0`), Quarterly (`plan_id=1`), and Annual (`plan_id=2`) subscriptions.
  2. Lifetime subscriptions (`plan_id=3`) have no end date.
  3. Rename `date_purchased` to `date_start` for consistency.
- **Sanity Check**: Ensure 18,207 rows in the result set.

#### II. Re-Calculating a Subscription’s End Date
- **Objective**: Update `date_end` to terminate at the refund date for refunded orders (`date_refunded`).
- **Sanity Check**: Ensure 18,207 rows in the updated result.

#### III. Creating `paid` Columns and a MySQL View
- **Objective**: Create a `purchases_info` view with:
  - `purchase_id`, `student_id`, `plan_id`, `date_start`, `date_end`, `paid_q2_2021`, `paid_q2_2022`.
  - `paid_q2_*` values indicate if a student had an active subscription in Q2.
- **Sanity Check**: Ensure the view is accurate and ready for analysis.

---

### 2. **Data Preparation with SQL – Splitting Into Periods**
#### I. Calculating Total Minutes Watched
- **Objective**: Retrieve total minutes watched during Q2 2021 and Q2 2022.
- **Steps**:
  1. Use the `student_video_watched` table.
  2. Return a table for each period with `student_id` and `minutes_watched`.
- **Sanity Check**:
  - Q2 2021: 7,639 rows.
  - Q2 2022: 8,841 rows.

#### II. Creating a `paid` Column
- **Objective**: Create result sets with `student_id`, `minutes_watched`, and `paid_in_q2`.
- **Output**:
  1. `minutes_watched_2021_paid_0.csv`
  2. `minutes_watched_2022_paid_0.csv`
  3. `minutes_watched_2021_paid_1.csv`
  4. `minutes_watched_2022_paid_1.csv`
- **Sanity Check**: Verify row counts:
  - 5,334, 6,055, 2,305, 2,786 respectively.

#### III. Certificates Issued
- **Objective**: Correlate minutes watched with certificates issued.
- **Output**:
  - `minutes_and_certificates.csv` containing `student_id`, `minutes_watched`, and `certificates_issued`.
- **Sanity Check**: Ensure 658 rows.

---

### 3. **Data Preprocessing with Python**
#### I. Plotting Distributions
- **Objective**: Visualize distributions of `minutes_watched`.
- **Tools**: Use `pandas` and `kdeplot()` to create subplots for clarity.
- **Task**: Identify skewness in the distributions.

#### II. Removing Outliers
- **Objective**: Remove outliers by retaining values below the 99th percentile.
- **Output**:
  - Save the cleaned datasets as:
    - `*_no_outliers.csv` for each original file.

---

### 4. **Data Analysis with Excel**
#### I. Calculating Mean and Median
- **Objective**: Compare the mean and median for each group.
- **Task**: Validate results against distribution plots.

#### II. Calculating Confidence Intervals
- **Objective**: Determine 95% confidence intervals for minutes watched.
- **Task**: Create a bar chart for visualization.

#### III. Hypothesis Testing
- **Objective**: Test if new features increased engagement.
- **Hypotheses**:
  - **Null**: Q2 2021 engagement ≥ Q2 2022.
  - **Alternative**: Q2 2021 engagement < Q2 2022.
- **Tests**:
  - Free-plan: Two-sample t-test (equal variances).
  - Paid: Two-sample t-test (unequal variances).
  - Optional: Two-sample f-test for variance assumptions.

#### IV. Correlation Coefficients
- **Objective**: Analyze the correlation between minutes watched and certificates issued.
- **Output**: Scatter plot to support findings.

---

### 5. **Dependencies and Probabilities**
#### I. Event Dependencies
- **Objective**: Determine if watching a lecture in Q2 2021 and Q2 2022 are dependent events.

#### II. Calculating Probabilities
- **Objective**: Calculate probabilities of:
  - Q2 2021 engagement given Q2 2022 engagement.

---

### 6. **Data Prediction with Python**
#### I. Linear Regression
- **Objective**: Predict `certificates_issued` using `minutes_watched`.
- **Tasks**:
  1. Split data (80% train, 20% test, `random_state=365`).
  2. Calculate:
     - Linear equation.
     - R-squared value.
     - Certificates predicted for 1200 minutes watched.
  3. Interpret results and validate the model.

---

## Deliverables
1. **SQL Outputs**:
   - `purchases_info` view.
   - CSV files: `minutes_watched_*`, `minutes_and_certificates.csv`.
2. **Python Outputs**:
   - Cleaned datasets without outliers.
   - Distribution plots for `minutes_watched`.
3. **Excel Outputs**:
   - Confidence intervals, hypothesis testing results, and correlation coefficients.
4. **Insights**:
   - User engagement trends.
   - Impact of platform features on minutes watched and certificates issued.

---

## Tools and Techniques
- **SQL**: Data preparation and query execution.
- **Python**: Data cleaning, visualization, and prediction.
- **Excel**: Statistical analysis, hypothesis testing, and visualization.

---

## Notes
- Ensure consistency in row counts at each step.
- Use appropriate statistical tests based on assumptions.
- Validate all outputs against sanity checks.


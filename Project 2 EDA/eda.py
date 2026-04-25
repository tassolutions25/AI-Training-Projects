import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import skew, kurtosis
from imblearn.over_sampling import SMOTE

# Loading Data
df = pd.read_csv("/content/cs-training.csv")

df.drop(columns=["Unnamed: 0"], inplace=True, errors="ignore")

print(df.head())

# ==========================================
# 1. DATA CLEANING (Column by Column)
# ==========================================
# A. Create Flags for Missing Data (Important for the model to know what was missing)
df["MonthlyIncome_was_missing"] = df["MonthlyIncome"].isnull().astype(int)
df["NumberOfDependents_was_missing"] = df["NumberOfDependents"].isnull().astype(int)

# B. Handling DebtRatio Logic Anomaly
# Logic: If MonthlyIncome is NA, DebtRatio actually represents the Monthly Debt amount.
# We will create a consistent 'MonthlyDebt' column and then recalculate a clean DebtRatio.
income_median = df["MonthlyIncome"].median()


def clean_debt_logic(row):
    # If Income is missing, DebtRatio is the actual Debt amount
    if row["MonthlyIncome_was_missing"] == 1:
        return row["DebtRatio"]
    # If Income is present, Debt = Ratio * Income
    else:
        return row["DebtRatio"] * row["MonthlyIncome"]


df["MonthlyDebt"] = df.apply(clean_debt_logic, axis=1)

# replace MonthlyIncome with Median (instead of deletion)
df["MonthlyIncome"] = df["MonthlyIncome"].fillna(income_median)

df["DebtRatio_Cleaned"] = df["MonthlyDebt"] / (df["MonthlyIncome"] + 1)

# C. Handling NumberOfDependents
# replace with Mode (0)
df["NumberOfDependents"] = df["NumberOfDependents"].fillna(
    df["NumberOfDependents"].mode()[0]
)

# D. Handling age outliers (replace 0 or unlikely ages with median)
age_median = df["age"].median()
df.loc[df["age"] < 18, "age"] = age_median

# E. Handling RevolvingUtilizationOfUnsecuredLines
# Ratios over 2.0 are often errors or extreme distress. Cap them to reduce outlier pull.
df["RevolvingUtilizationOfUnsecuredLines"] = df[
    "RevolvingUtilizationOfUnsecuredLines"
].clip(upper=2.0)

print("--- Cleaning Complete ---")
print(df[["MonthlyIncome", "MonthlyDebt", "DebtRatio_Cleaned"]].head(10))

# ==========================================
# 2. FEATURE ENGINEERING
# ==========================================
print("\n--- Performing Feature Engineering ---")
# A. (Grouping Past Due Behavior)
df["TotalTimesPastDue"] = (
    df["NumberOfTime30-59DaysPastDueNotWorse"]
    + df["NumberOfTime60-89DaysPastDueNotWorse"]
    + df["NumberOfTimes90DaysLate"]
)
# B. Income per Household Member
df["IncomePerPerson"] = df["MonthlyIncome"] / (df["NumberOfDependents"] + 1)

# C. Ratio of Late Payments to Open Lines (Risk Intensity)
df["LatePaymentIntensity"] = df["TotalTimesPastDue"] / (
    df["NumberOfOpenCreditLinesAndLoans"] + 1
)

# D. Retired Flag (Binary) - Risk profiles change significantly after 65
df["is_retired"] = (df["age"] > 65).astype(int)

# ==========================================
# 3. Univariate Analysis
# ==========================================

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
# Target Variable Distribution
sns.countplot(x="SeriousDlqin2yrs", data=df, ax=axes[0, 0], palette="viridis")
axes[0, 0].set_title("Distribution of Financial Distress (Target)")

# Age Distribution
sns.histplot(df["age"], bins=30, kde=True, ax=axes[0, 1], color="blue")
axes[0, 1].set_title("Borrower Age Distribution")

# Monthly Income Distribution (Log transformation method because of high variance)
sns.histplot(df["MonthlyIncome"], bins=50, kde=True, ax=axes[1, 0], color="green")
axes[1, 0].set_xscale("log")
axes[1, 0].set_title("Monthly Income Distribution (Log Scale)")

# Total Late Payments Distribution
sns.countplot(
    x="TotalTimesPastDue", data=df[df["TotalTimesPastDue"] < 10], ax=axes[1, 1]
)
axes[1, 1].set_title("Frequency of Total Late Payments (< 10)")

plt.tight_layout()
plt.show()

# ==========================================
# 4. KURTOSIS AND SKEWNESS
# ==========================================
print("\n--- Kurtosis Analysis (Outlier Tailedness) ---")
# Kurtosis > 3 indicates "Heavy Tails" (Leptokurtic) - high risk of outliers
numerical_cols = [
    "age",
    "MonthlyIncome",
    "DebtRatio_Cleaned",
    "RevolvingUtilizationOfUnsecuredLines",
]

for col in numerical_cols:
    sk_val = skew(df[col])
    kurt_val = kurtosis(df[col])
    print(f"Skewness of {col}: {sk_val:.2f}")
    print(f"Kurtosis of {col}: {kurt_val:.2f}")

    if sk_val > 1:
        print(
            "   -> Result: Highly Positively Skewed (Right Tail). Most values are low, few are very high."
        )
    elif sk_val < -1:
        print("   -> Result: Highly Negatively Skewed (Left Tail).")
    else:
        print("   -> Result: Fairly Symmetrical.")

    if kurt_val > 3:
        print(
            f"   -> Result: High Kurtosis. {col} is heavily influenced by extreme outliers."
        )


# ==========================================
# 5. Bivariate Analysis
# ==========================================

# 1. Utilization vs Financial Distress (Boxplot)
plt.figure(figsize=(10, 6))
sns.boxplot(x="SeriousDlqin2yrs", y="RevolvingUtilizationOfUnsecuredLines", data=df)
plt.title("Credit Utilization vs Financial Distress")
plt.show()

# 2. Relationship between Number of Dependents and Distress
plt.figure(figsize=(10, 6))
sns.barplot(x="NumberOfDependents", y="SeriousDlqin2yrs", data=df)
plt.title("Probability of Distress by Number of Dependents")
plt.show()

# 3. Recalculated DebtRatio vs Distress
plt.figure(figsize=(10, 6))
sns.boxplot(x="SeriousDlqin2yrs", y="DebtRatio_Cleaned", data=df)
plt.ylim(0, 2)  # Limiting Y-axis to see the bulk of the data
plt.title("Cleaned Debt Ratio vs Financial Distress")
plt.show()

# ==========================================
# 6. HYPOTHESIS TESTING
# ==========================================
print("\n--- STATISTICAL HYPOTHESIS TESTING RESULTS ---")

# Grouping the data for tests
distress_group = df[df["SeriousDlqin2yrs"] == 1]
no_distress_group = df[df["SeriousDlqin2yrs"] == 0]

# --- Test 1: Age (T-Test) --- To see if the average Age of people in distress is significantly different from those who are not.
# H0: There is no difference in mean age between the two groups.
# H1: Mean age is significantly different.

t_stat, p_val_age = stats.ttest_ind(distress_group["age"], no_distress_group["age"])

print(f"\n1. T-Test for Age:")
# print(f"\n1. T-stat: {t_stat}")
print(f"   P-Value: {p_val_age:.10f}")
if p_val_age < 0.05:
    print(
        "   Result: Reject Null Hypothesis. Age is a significant factor in financial distress.(Age actually matters in predicting risk.)"
    )
else:
    print("   Result: Fail to Reject Null Hypothesis.")

# Result analysis: If the P-value is less than 0.05, we reject the idea that they are the same. We conclude: "Age actually matters in predicting risk."

# --- Test 2: Monthly Income (Mann-Whitney U Test) --- used because income is not normally distributed
# We use this instead of a T-test because income is highly skewed.
# This doesn't look at the average. It ranks all incomes from smallest to largest and checks if one group consistently ranks lower than the other.
# H0: Distribution of income is the same for both groups.
u_stat, p_val_inc = stats.mannwhitneyu(
    distress_group["MonthlyIncome"], no_distress_group["MonthlyIncome"]
)

print(f"\n2. Mann-Whitney U Test for Monthly Income:")
# print(f"   U-stat: {u_stat}")
print(f"   P-Value: {p_val_inc:.10f}")
if p_val_inc < 0.05:  # in statistics, 0.05 is the standard "cut-off" (Alpha)
    print(
        "   Result: Reject Null Hypothesis. Income levels significantly differ between the two groups."
    )
else:
    print("   Result: Fail to Reject Null Hypothesis.")

# --- Test 3: Past Due Behavior (Chi-Square Test) --- To see if the presence of 90+ days late payments is statistically associated with the target variable.
# This test is for categorical data (Yes/No vs. Yes/No).
# We create a new column. If a borrower was late 90+ days even once, they get a 1. If they were never late, they get a 0. This turns a "count" into a "category."
df["Ever90DaysLate"] = df["NumberOfTimes90DaysLate"].apply(lambda x: 1 if x > 0 else 0)

# Create a contingency table -
# This creates a 2x2 "Frequency Table" (a grid). It counts:
# How many people were late AND had distress.
# How many were late AND HAD NO distress.
# How many were NOT late AND had distress.
# How many were NOT late AND HAD NO distress.
contingency_table = pd.crosstab(df["Ever90DaysLate"], df["SeriousDlqin2yrs"])
print(f"\n3. Contingency table \n {contingency_table}")
chi2, p_val_chi, dof, ex = stats.chi2_contingency(contingency_table)

print(f"\n3. Chi-Square Test for 90+ Days Late Behavior:")
print(f"   P-Value: {p_val_chi:.10f}")
if p_val_chi < 0.05:
    print(
        "   Result: Reject Null Hypothesis. There is a strong statistical association between past late payments and future distress."
    )
else:
    print("   Result: Fail to Reject Null Hypothesis.")

# ==========================================
# 8. Correlation Matrix & Multicollinearity Analysis
# ==========================================
plt.figure(figsize=(15, 10))

# 1. Filter out the binary "flag" columns to keep the map clean
cols_to_drop = [
    "MonthlyIncome_was_missing",
    "NumberOfDependents_was_missing",
    "is_retired",
    "Ever90DaysLate",
]
corr_df = df.drop(columns=cols_to_drop)

# 2. Calculate the Correlation Matrix
matrix = corr_df.corr()

# 3. Create a "Mask" for the upper triangle
# This makes the heatmap much easier to read by removing the mirrored half
mask = np.triu(np.ones_like(matrix, dtype=bool))

# 4. Plotting the Heatmap
sns.heatmap(
    matrix,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    center=0,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8},
)

plt.title("Refined Correlation Heatmap (Filtered Features)", fontsize=16)
plt.show()

# 5. Extracting specific insights for the Report
print("\n--- Top Features Correlated with Financial Distress (Target) ---")
target_corr = matrix["SeriousDlqin2yrs"].sort_values(ascending=False)
print(target_corr)

# 6. Checking for Multicollinearity (Redundant Variables)
print("\n--- Multicollinearity Warning ---")
high_corr = matrix.unstack().sort_values(ascending=False)
high_corr = high_corr[(high_corr > 0.8) & (high_corr < 1.0)]
if not high_corr.empty:
    print("The following features are highly correlated (>0.8) and may be redundant:")
    print(high_corr.drop_duplicates())


# ==========================================
# 8. DATA IMBALANCE MITIGATION (SMOTE) -> Pre Modeling
# ==========================================
print("\n--- Mitigating Data Imbalance ---")

# 1. Check current imbalance
counts = df["SeriousDlqin2yrs"].value_counts()
print(f"Original Class 0 (No Distress): {counts[0]}")
print(f"Original Class 1 (Distress): {counts[1]}")
print(f"Imbalance Ratio: 1:{round(counts[0]/counts[1], 2)}")

# 2. Applying SMOTE (Synthetic Minority Over-sampling Technique)
# Note: In a real project, you apply this ONLY to the training set, not the whole DF.
X = df.drop(columns=["SeriousDlqin2yrs"])
y = df["SeriousDlqin2yrs"]

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

print(f"Resampled Class 0: {pd.Series(y_resampled).value_counts()[0]}")
print(f"Resampled Class 1: {pd.Series(y_resampled).value_counts()[1]}")
print("Result: Synthetic data created to balance the classes perfectly (1:1).")

# [KDE Plots / Heatmaps logic...]
# print(df['LatePaymentIntensity'])
# plt.figure(figsize=(10, 6))
# sns.kdeplot(df[df['SeriousDlqin2yrs']==1]['LatePaymentIntensity'], label="Distress", fill=True)
# sns.kdeplot(df[df['SeriousDlqin2yrs']==0]['LatePaymentIntensity'], label="No Distress", fill=True)
# plt.title("Feature Engineering: Late Payment Intensity Distribution")
# plt.xlim(0, 2)
# plt.legend()
# plt.show()

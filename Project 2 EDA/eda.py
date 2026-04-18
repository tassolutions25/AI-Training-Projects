import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Loading Data
df = pd.read_csv("cs-training.csv")

df.drop(columns=["Unnamed: 0"], inplace=True, errors="ignore")

print(df.head())

# Data Cleaning
print(
    "cleaning Null values", df.isnull().sum()
)  # -> Found many Null values for monthly income and number of dependents

# fill the monthly income with the median value because it isn't skewed by extreme millionaires and the number of dependents with the mode value (most likely 0) because it is count
df["MonthlyIncome"] = df["MonthlyIncome"].fillna(df["MonthlyIncome"].median())
df["NumberOfDependents"] = df["NumberOfDependents"].fillna(
    df["NumberOfDependents"].median()
)

# Now we need to see how many people in the dataset actually experienced financial distress.
# We us univariate analysis -> Examines the distribution and pattern of the financial distress column
sns.countplot(
    x="SeriousDlqin2yrs", data=df
)  # Shows count of unique values in a categorical variable
plt.title("Distribution of Financial Distress (Target)")
plt.show()

print(
    "financial distress percentage: ",
    df["SeriousDlqin2yrs"].value_counts(normalize=True),
)


# now we use bivariate analysis to find correlation between the financial distress and the other columns and analyze the risk factor
# compare independent variables against the target variable
# 1. Age vs. Distress
plt.figure(figsize=(10, 6))
sns.boxplot(x="SeriousDlqin2yrs", y="age", data=df)
plt.title("Age vs Financial Distress")
plt.show()  # -> result -> Usually, younger borrowers( Age 35 to 50) are statistically higher risk than older, more established borrowers.

# 2. Considering past due behavior
# Comparing NumberOfTime30-59DaysPastDueNotWorse to the Target
sns.lmplot(x="NumberOfTimes90DaysLate", y="SeriousDlqin2yrs", data=df, logistic=True)
plt.title("Impact of 90+ Days Late Payments on Risk")
plt.show()  # -> result -> this is more likely the strongest predictor. -> If a borrower has been 90 days late before, the probability of them being in distress again is very high.

# detecting outliers -> in RevolvingUtilizationOfUnsecuredLines and in DebtRatio
# Check for extreme values in Utilization
print(
    "revolving utilization of unsecured lines: ",
    df["RevolvingUtilizationOfUnsecuredLines"].describe(),
)

# Check for extreme DebtRatio
print("Debt Ratio: ", df[df["DebtRatio"] > 1].shape)
# result -> Very high Debt Ratios or Utilization rates are "Outliers." We need to decide whether to cap these values or investigate if they are data entry errors.

# Finally, We check how all variables relate to each other. -> using correlation heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix")
plt.show()  # -> This shows which variables "move together."

# Analysis
# Key Risk Predictors -> NumberOfTimes90DaysLate and RevolvingUtilizationOfUnsecuredLines
# Data Quality Issues -> The bank needs to improve the collection of MonthlyIncome data, as many entries are missing.
# Income Bias: The DebtRatio calculation is skewed for borrowers where income is recorded as 0 or missing; these cases need a special "flag" in the model.

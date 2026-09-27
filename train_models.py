import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Create dummy heart model data
heart_data = pd.DataFrame({
  'age': np.random.randint(30, 65, 100),
  'gender': np.random.randint(0, 2, 100),
  'sbp': np.random.randint(100, 180, 100),
  'chol': np.random.randint(150, 300, 100),
  'heart_rate': np.random.randint(60, 110, 100),
  'target': np.random.randint(0, 2, 100)
})

X_heart = heart_data[['age', 'gender', 'sbp', 'chol', 'heart_rate']]
y_heart = heart_data['target']
heart_model = RandomForestClassifier()
heart_model.fit(X_heart, y_heart)

# Save heart model
os.makedirs("models", exist_ok=True)
joblib.dump(heart_model, "models/heart_model.pkl")

# Create dummy sugar (diabetes) model data
sugar_data = pd.DataFrame({
  'age': np.random.randint(25, 70, 100),
  'gender': np.random.randint(0, 2, 100),
  'glucose': np.random.randint(70, 200, 100),
  'target': np.random.randint(0, 2, 100)
})

X_sugar = sugar_data[['age', 'gender', 'glucose']]
y_sugar = sugar_data['target']
sugar_model = RandomForestClassifier()
sugar_model.fit(X_sugar, y_sugar)

# Save sugar model
joblib.dump(sugar_model, "models/sugar_model.pkl")

print("✅ Models trained and saved successfully.")
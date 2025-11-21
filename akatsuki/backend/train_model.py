import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# Load dataset
df = pd.read_csv("dataset.csv")

# Features and target
X = df[['hour', 'weekday', 'patient_count', 'emergency_count']]
y = df['wait_minutes']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
print("Model MAE:", mae)

# Save model
joblib.dump(model, "model.joblib")
print("model.joblib created successfully.")

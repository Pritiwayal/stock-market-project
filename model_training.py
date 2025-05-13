import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load historical data
data = pd.read_csv('data/stock_data.csv')

# Feature engineering
data['50_MA'] = data['Close'].rolling(window=50).mean()
data['200_MA'] = data['Close'].rolling(window=200).mean()
data['Volume_Trend'] = data['Volume'].diff()

# Drop NaN values
data = data.dropna()

# Define features and labels
X = data[['Close', '50_MA', '200_MA', 'Volume_Trend']]
y = np.where(data['Close'] > data['50_MA'], 'Buy', 'Sell')  # Example condition

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(model, 'stock_model.pkl')

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# Sample dataset (you can replace with real medical data)
data = pd.DataFrame({
    "fever": [1, 0, 1, 1, 0],
    "cough": [1, 1, 0, 1, 0],
    "fatigue": [1, 0, 1, 0, 0],
    "risk": [1, 0, 1, 1, 0]
})

X = data[["fever", "cough", "fatigue"]]
y = data["risk"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LogisticRegression()
model.fit(X_train, y_train)

preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))

joblib.dump(model, "risk_model.pkl")
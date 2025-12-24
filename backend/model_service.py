import joblib

class RiskModel:
    def __init__(self):
        self.model = joblib.load("risk_model.pkl")

    def predict_risk(self, symptoms_vector):
        prob = self.model.predict_proba([symptoms_vector])[0][1]
        if prob > 0.7:
            return "High Risk"
        if prob > 0.4:
            return "Medium Risk"
        return "Low Risk"
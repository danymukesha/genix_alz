# genix_alz/src/risk_calculator.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import joblib
import json
import os

# Alzheimer's risk genes with effect sizes (based on ADSP/IGAP meta-analyses)
ALZ_GENES = {
    'APOE': {
        'e2/e2': -0.89, 'e2/e3': -0.60, 'e2/e4': 0.31,
        'e3/e3': 0.0, 'e3/e4': 1.21, 'e4/e4': 2.54
    },
    'CLU': {'CC': 0.0, 'CT': 0.42, 'TT': 0.87},
    'CR1': {'GG': 0.0, 'GA': 0.38, 'AA': 0.75},
    'BIN1': {'AA': 0.0, 'AG': 0.31, 'GG': 0.63},
    'PICALM': {'TT': 0.0, 'TG': 0.29, 'GG': 0.58},
    'ABCA7': {'CC': 0.0, 'CT': 0.33, 'TT': 0.65},
    'MS4A': {'AA': 0.0, 'AG': 0.28, 'GG': 0.55},
    'CD33': {'GG': 0.0, 'GT': -0.26, 'TT': -0.51},
    'CD2AP': {'CC': 0.0, 'CT': 0.27, 'TT': 0.53},
    'EPHA1': {'AA': 0.0, 'AG': 0.25, 'GG': 0.49},
    'HLA-DRB5': {'GG': 0.0, 'GA': 0.23, 'AA': 0.45}
}

class PolygenicRiskEngine:
    def __init__(self, model_path='models/risk_model.pkl', 
                 drug_rules_path='data/drug_interactions.json'):
        #self.model = joblib.load(model_path) if os.path.exists(model_path) else self._train_model()
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            X_test = np.random.rand(300, len(ALZ_GENES))
            y_test = np.random.randint(0, 2, 300)
            self.evaluate_model(X_test, y_test)
        else:
            self.model = self._train_model()
        self.drug_rules = self._load_drug_rules(drug_rules_path)
        self.base_risk = {'50-59': 1.2, '60-69': 3.4, '70-79': 7.1, '80+': 16.3}
        
    def _load_drug_rules(self, path):
        with open(path) as f:
            return json.load(f)
    
    def _train_model(self):
        """Train model on synthetic data if no pre-trained exists"""
        print("Training risk model on synthetic cohort...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        calibrated = CalibratedClassifierCV(model, cv=3)
        feature_names = list(ALZ_GENES.keys())
        # In production: Replace with real ADNI/UKB data
        X = np.random.rand(1000, len(ALZ_GENES))
        X_df = pd.DataFrame(X, columns=feature_names)
        y = np.random.randint(0, 2, 1000)
        X_train, X_test, y_train, y_test = train_test_split(X_df, y, test_size=0.3, random_state=42)
        
        calibrated.fit(X_train, y_train)
        self.model = calibrated
        self.evaluate_model(X_test, y_test)

        os.makedirs('models', exist_ok=True)
        joblib.dump(calibrated, 'models/risk_model.pkl')
        
        return calibrated

    
    def evaluate_model(self, X_test, y_test, save_results=True):
        """Evaluate model using accuracy, AUC, ROC curve, confusion matrix, and more"""
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]  # prob. for the positive class
        accuracy = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        sensitivity = cm[1, 1] / (cm[1, 1] + cm[1, 0])
        specificity = cm[0, 0] / (cm[0, 0] + cm[0, 1])
      
        class_report = classification_report(y_test, y_pred, output_dict=True)

        fpr, tpr, thresholds = roc_curve(y_test, y_proba)
        auc_score = auc(fpr, tpr)
        
        results = {
            'accuracy': accuracy,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'auc': auc_score,
            'classification_report': class_report
        }
        
        if save_results:
            self.save_evaluation_results(results)
        
        metrics_path = "models/metrics"
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', label=f'ROC curve (AUC = {auc_score:.4f})')
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc='lower right')
        plt.savefig(os.path.join(metrics_path, 'roc_curve.png'))
        plt.close()
        
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.savefig(os.path.join(metrics_path, 'confusion_matrix.png'))
        plt.close()

        return results
    
    def save_evaluation_results(self, results, file_name="evaluation_results.json", filter_keys=None):
        """Save the evaluation results to a JSON and CSV file."""
        
        os.makedirs("models/metrics", exist_ok=True)
        metrics_path = os.path.join("models", "metrics", file_name)
        results_to_save = {k: results[k] for k in filter_keys} if filter_keys else results

        with open(metrics_path, 'w') as json_file:
            json.dump(results_to_save, json_file, indent=4)

        if "classification_report" in results:
            class_report_df = pd.DataFrame(results["classification_report"]).transpose()
            csv_path = metrics_path.replace(".json", "_classification_report.csv")
            class_report_df.to_csv(csv_path)
            print(f"Classification report saved to {csv_path}")

        print(f"Evaluation results saved to {metrics_path}")

    def calculate_score(self, genotype, age_group, medications=[]):
        """Calculate lifetime AD risk with drug interactions"""
        # converting genotype to feature vector
        X = pd.DataFrame([{
            gene: ALZ_GENES[gene].get(genotype.get(gene, ''), 0.0)
            for gene in ALZ_GENES
        }], columns=list(ALZ_GENES.keys()))
        
        # here we calculate risk
        proba = self.model.predict_proba(X)[0][1]
        adjusted_risk = min(95, proba * 100 * self.base_risk[age_group])
        
        # we should apply medication adjustments
        risk_modifiers = []
        for med in medications:
            for gene, rules in self.drug_rules.items():
                if gene in genotype and med in rules:
                    adjustment = rules[med]
                    adjusted_risk *= (1 + adjustment)
                    risk_modifiers.append(f"{med}: {adjustment*100:.1f}%")
        
        return {
            'raw_score': proba,
            'adjusted_risk': adjusted_risk,
            'risk_category': self._categorize_risk(adjusted_risk),
            'medication_effects': risk_modifiers
        }
    
    def _categorize_risk(self, risk):
        if risk < 10: return 'Low'
        if risk < 25: return 'Moderate'
        if risk < 40: return 'High'
        return 'Very High'

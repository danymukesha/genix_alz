# genix_alz/src/risk_calculator.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
import joblib
import json
import os

# Alzheimer's risk genes with effect sizes (based on ADSP/IGAP meta-analyses)
ALZ_GENES = {
    'APOE': {
        'ε2/ε2': -0.89, 'ε2/ε3': -0.60, 'ε2/ε4': 0.31,
        'ε3/ε3': 0.0, 'ε3/ε4': 1.21, 'ε4/ε4': 2.54
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
        self.model = joblib.load(model_path) if os.path.exists(model_path) else self._train_model()
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
        calibrated.fit(X_df, y)
        os.makedirs('models', exist_ok=True)
        joblib.dump(calibrated, 'models/risk_model.pkl')
        return calibrated
    
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
        
        # we sshould apply medication adjustments
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

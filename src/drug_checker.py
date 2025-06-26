# genix_alz/src/drug_checker.py
import json

class PharmacogenomicsAnalyzer:
    def __init__(self, rules_path='data/drug_interactions.json'):
        with open(rules_path) as f:
            self.rules = json.load(f)
    
    def check_interactions(self, genotype, medications):
        warnings = []
        recommendations = []
        
        for med in medications:
            for gene, variants in self.rules.items():
                if gene not in genotype:
                    continue
                    
                if med in variants:
                    effect = variants[med]
                    warnings.append(
                        f"{med} may {'increase' if effect > 0 else 'decrease'} "
                        f"AD risk by {abs(effect)*100:.1f}% in {gene} {genotype[gene]} carriers"
                    )
                    
                    # we can suggest alternatives
                    if 'alternatives' in variants:
                        recommendations.append(
                            f"Consider {', '.join(variants['alternatives'])} "
                            f"instead of {med}"
                        )
        
        return {
            'warnings': warnings,
            'recommendations': recommendations
        }

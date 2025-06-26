# genix_alz/src/cli.py
import argparse
import json
from risk_calculator import PolygenicRiskEngine
from drug_checker import PharmacogenomicsAnalyzer
from report_generator import ClinicalReportGenerator

def main():
    parser = argparse.ArgumentParser(description='AlzGen Insight CLI')
    parser.add_argument('--input', type=str, required=True, help='JSON input file')
    parser.add_argument('--output', type=str, default='report.pdf', help='Output PDF path')
    args = parser.parse_args()

    # load patient data
    with open(args.input) as f:
        patient = json.load(f)
    
    # initialize engines
    risk_engine = PolygenicRiskEngine()
    drug_analyzer = PharmacogenomicsAnalyzer()
    
    # process data
    risk_result = risk_engine.calculate_score(
        genotype=patient['genotype'],
        age_group=patient['age_group'],
        medications=patient.get('medications', [])
    )
    
    drug_result = drug_analyzer.check_interactions(
        genotype=patient['genotype'],
        medications=patient.get('medications', [])
    )
    
    # generate report
    reporter = ClinicalReportGenerator(patient, risk_result, drug_result)
    report_path = reporter.generate_pdf(args.output)
    
    print(f"Report generated: {report_path}")
    print(f"Risk Assessment: {risk_result['risk_category']} ({risk_result['adjusted_risk']:.1f}%)")
    
    if drug_result['warnings']:
        print("\nMedication Warnings:")
        for warning in drug_result['warnings']:
            print(f"  ⚠️ {warning}")

if __name__ == '__main__':
    main()

# genix_alz/src/report_generator.py
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
import numpy as np
import io

class ClinicalReportGenerator:
    def __init__(self, patient_data, risk_result, drug_results):
        self.patient = patient_data
        self.risk = risk_result
        self.drug = drug_results
    
    def generate_pdf(self, output_path='report.pdf'):
        pdf = FPDF()
        pdf.add_page()
        
        # the header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'AlzGen Insight - Alzheimer\'s Genetic Risk Report', 0, 1, 'C')
        pdf.ln(10)
        
        # the patient info
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Patient ID: {self.patient['id']}", 0, 1)
        pdf.cell(0, 10, f"Age Group: {self.patient['age_group']}", 0, 1)
        pdf.ln(5)
        
        # the risk summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Genetic Risk Assessment', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Lifetime AD Risk: {self.risk['adjusted_risk']:.1f}%", 0, 1)
        pdf.cell(0, 10, f"Risk Category: {self.risk['risk_category']}", 0, 1)
        
        # risk visualization
        self._generate_risk_chart()
        img = self._plot_to_base64()
        pdf.image(img, x=50, w=110)
        pdf.ln(5)
        
        # the drug interactions
        if self.drug['warnings']:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Medication Safety', 0, 1)
            pdf.set_font('Arial', '', 12)
            for warning in self.drug['warnings']:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, f"• {warning}", 0, 1)
            for rec in self.drug['recommendations']:
                pdf.set_text_color(0, 100, 0)
                pdf.cell(0, 10, f"• {rec}", 0, 1)
            pdf.set_text_color(0, 0, 0)
        
        # clinical recommendations
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Clinical Action Plan', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        actions = [
            "Annual cognitive screening",
            "MRI baseline at age 55",
            "Cardiovascular risk management",
            "Mediterranean diet counseling"
        ]
        
        if self.risk['adjusted_risk'] > 25:
            actions.append("Consider amyloid PET scan")
            actions.append("Eligible for prevention trials")
        
        for action in actions:
            pdf.cell(0, 10, f"• {action}", 0, 1)
        
        # saving the output
        pdf.output(output_path)
        return output_path
    
    def _generate_risk_chart(self):
        plt.figure(figsize=(8, 4))
        groups = ['Low', 'Moderate', 'High', 'Very High']
        values = [10, 25, 40, 95]
        colors = ['green', 'yellow', 'orange', 'red']
        
        current_risk = self.risk['adjusted_risk']
        bar_idx = next(i for i, v in enumerate(values) if current_risk <= v)
        
        plt.bar(groups, values, color=colors, alpha=0.3)
        plt.bar(groups[bar_idx], current_risk, color=colors[bar_idx])
        plt.axhline(y=current_risk, color='gray', linestyle='--')
        plt.ylabel('Risk (%)')
        plt.title('Alzheimer\'s Lifetime Risk')
        plt.tight_layout()
    
    def _plot_to_base64(self):
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        return io.BytesIO(buf.getvalue())

import streamlit as st
import os
import json
import datetime
import tempfile
from risk_calculator import PolygenicRiskEngine, ALZ_GENES
from drug_checker import PharmacogenomicsAnalyzer
from report_generator import ClinicalReportGenerator

# Page configuration
st.set_page_config(
    page_title="🧠 Genix Alz",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load medication interaction rules
with open('data/drug_interactions.json') as f:
    drug_rules = json.load(f)

# Extract medication list
medications_list = sorted({
    med for gene_rules in drug_rules.values()
    for med in gene_rules if med != "alternatives"
})

# App Header
st.title("🧠 AlzGen Insight")
st.markdown("#### Clinical-Grade Alzheimer’s Genetic Risk Assessment")

# Sidebar Inputs
st.sidebar.header("🧬 Patient Information")
patient_id = st.sidebar.text_input("Patient ID", value="PT-ALZ-001")
age_group = st.sidebar.selectbox("Age Group", ["50-59", "60-69", "70-79", "80+"])

st.sidebar.subheader("Genotype Profile")
genotype = {
    gene: st.sidebar.selectbox(gene, list(variants.keys()))
    for gene, variants in ALZ_GENES.items()
}

st.sidebar.subheader("💊 Current Medications")
selected_medications = st.sidebar.multiselect("Select medications", medications_list)

# Run assessment
if st.sidebar.button("🧾 Generate Assessment"):

    # Engines
    risk_engine = PolygenicRiskEngine(model_path='models/risk_model.pkl', drug_rules_path='data/drug_interactions.json')
    drug_checker = PharmacogenomicsAnalyzer(rules_path='data/drug_interactions.json')

    # Risk calculation
    risk_result = risk_engine.calculate_score(genotype=genotype, age_group=age_group, medications=selected_medications)
    drug_result = drug_checker.check_interactions(genotype=genotype, medications=selected_medications)

    # Display results
    st.subheader("📊 Assessment Summary")
    st.metric("Lifetime Alzheimer's Risk", f"{risk_result['adjusted_risk']:.1f}%", risk_result["risk_category"])

    st.markdown("#### 🧪 Medication Impact")
    if risk_result["medication_effects"]:
        for effect in risk_result["medication_effects"]:
            st.warning(effect)
    else:
        st.success("No medication-related risk modification detected.")

    st.markdown("#### ⚠️ Drug Interaction Warnings")
    if drug_result["warnings"]:
        for warning in drug_result["warnings"]:
            st.error(warning)
    else:
        st.info("No critical gene-drug warnings.")

    st.markdown("#### 💡 Recommendations")
    if drug_result["recommendations"]:
        for rec in drug_result["recommendations"]:
            st.success(rec)
    else:
        st.info("No special recommendations.")

    # PDF Report Generation
    st.markdown("---")
    st.subheader("📄 Downloadable Clinical PDF Report")

    patient_data = {
        'id': patient_id,
        'age_group': age_group,
        'genotype': genotype,
        'medications': selected_medications
    }

    reporter = ClinicalReportGenerator(patient_data, risk_result, drug_result)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        report_path = reporter.generate_pdf(tmp.name)
        with open(report_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF Report",
                data=f.read(),
                file_name=f"genix_alz_report_{patient_id}.pdf",
                mime="application/pdf"
            )
        os.remove(report_path)

    st.success("✅ Assessment complete. You can download the report above.")

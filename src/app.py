import streamlit as st
import os
import json
import datetime
import tempfile
from risk_calculator import PolygenicRiskEngine, ALZ_GENES
from drug_checker import PharmacogenomicsAnalyzer
from report_generator import ClinicalReportGenerator

st.set_page_config(
    page_title="🧠 Genix Alz",
    layout="centered",
    initial_sidebar_state="expanded"
)

with open('data/drug_interactions.json') as f:
    drug_rules = json.load(f)

medications_list = sorted({
    med for gene_rules in drug_rules.values()
    for med in gene_rules if med != "alternatives"
})

st.title("🧠 GENIX ALZ")
st.markdown("#### Clinical-Grade Alzheimer’s Genetic Risk Assessment")

tabs = st.tabs(["How To Use", "Risk Assessment", "About the AI Model"])

with tabs[0]:
    st.markdown("""
    **Please follow these simple steps to get started:**

    1. **Enter Patient Info:** Provide a unique Patient ID and select the patient’s age group in the sidebar.  
    2. **Select Genotypes:** Choose the patient’s genetic variants for each Alzheimer’s-associated gene.  
    3. **Add Medications:** Select any current medications the patient is taking.  
    4. **Generate Assessment:** Click the “Generate Assessment” button to calculate the risk score.  
    5. **View Results:** Review the risk score, medication effects, and warnings on the main page.  
    6. **Download Report:** Get a detailed PDF report summarizing the assessment and recommendations.
    ----
    """)
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
        risk_engine = PolygenicRiskEngine(model_path='models/risk_model.pkl', drug_rules_path='data/drug_interactions.json')
        drug_checker = PharmacogenomicsAnalyzer(rules_path='data/drug_interactions.json')

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

with tabs[1]:
  st.markdown("""
    Alzheimer’s disease (AD) is a progressive neurodegenerative disorder that represents the most common cause of dementia worldwide, affecting millions of individuals. 
    Genetic predisposition plays a critical role in AD risk, with well-established susceptibility genes such as **APOE**, **CLU**, **PICALM**, and others contributing to lifetime risk.

    This tool integrates **polygenic risk scoring**, combining the effects of multiple genetic variants validated by large-scale genome-wide association studies (GWAS) ([Lambert et al., 2013](https://www.nature.com/articles/ng.2802)) and subsequent meta-analyses, to provide an individualized risk estimate.  
    In addition, it assesses pharmacogenomic interactions, recognizing that certain medications can modulate AD risk pathways based on patient genotype, in line with emerging research on gene-drug interactions affecting neurodegeneration risk ([Sabbagh et al., 2020](https://doi.org/10.2147/CIA.S214423)).

    **Key features:**
    - Incorporates patient age, genetic profile, and medication usage to adjust risk estimates.
    - Provides medication warnings and personalized recommendations to optimize clinical management.
    - Generates downloadable clinical reports to aid healthcare professionals in decision-making.

    *Disclaimer:* This tool is designed for research and clinical support purposes and should be used in conjunction with comprehensive clinical evaluation.

    ---
    """)
  
with tabs[2]:
    st.header("🤖 About the Machine Learning Model Behind GENIX ALZ")

    st.markdown("""
    **GENIX ALZ** uses a state-of-the-art machine learning model built on clinical and genetic data to estimate lifetime Alzheimer's Disease (AD) risk.

    ### Model Overview:
    - Uses a **Random Forest classifier** calibrated with cross-validation.
    - Incorporates **11 validated AD risk genes** (e.g., APOE, CLU, CR1, BIN1) with specific genotype effect sizes based on large meta-analyses such as ADSP and IGAP.
    - Age stratification adjusts baseline risk to reflect known epidemiological data.
    - Incorporates **pharmacogenomic drug-gene interaction data** to refine risk based on current medications.
    
    ### Training Details:
    - The model is trained on synthetic cohorts when real datasets are unavailable, using features representing genotype data encoded with gene-specific effect sizes.
    - Prediction outputs a calibrated probability of AD risk, which is then scaled by age-group baselines.
    
    ### Scientific Evidence:
    - The selected genes and effect sizes are derived from published genome-wide association studies (GWAS) and meta-analyses:
        - [ADSP](https://www.niagads.org/adsp)
        - [IGAP](https://www.niagads.org/igap)
    - Drug interaction rules reflect current pharmacogenomic findings indicating how certain medications can modulate AD risk in specific genotypes.

    ### Code Snippet from the Core Model:
    ```python
    class PolygenicRiskEngine:
        def calculate_score(self, genotype, age_group, medications=[]):
            X = pd.DataFrame([{
                gene: ALZ_GENES[gene].get(genotype.get(gene, ''), 0.0)
                for gene in ALZ_GENES
            }])
            proba = self.model.predict_proba(X)[0][1]
            adjusted_risk = min(95, proba * 100 * self.base_risk[age_group])
            
            for med in medications:
                for gene, rules in self.drug_rules.items():
                    if gene in genotype and med in rules:
                        adjustment = rules[med]
                        adjusted_risk *= (1 + adjustment)
            
            return adjusted_risk
    ```

    ### References:
    1. Lambert, J.-C., et al. (2013). Meta-analysis of 74,046 individuals identifies 11 new susceptibility loci for Alzheimer's disease. *Nature Genetics*, 45(12), 1452–1458.
    2. Kunkle, B. W., et al. (2019). Genetic meta-analysis of diagnosed Alzheimer's disease identifies new risk loci and implicates Aβ, tau, immunity and lipid processing. *Nature Genetics*, 51(3), 414–430.

    This approach allows for **personalized risk profiling** that can inform early interventions and medication management.
    """)


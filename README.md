`genix_alz` is a clinically oriented software platform for assessing individualized Alzheimer's disease (AD) risk 
using genetic profiles, age stratification, and medication history. It uses a calibrated machine learning model trained 
on polygenic risk scores derived from validated AD-associated loci, including APOE and 10 additional susceptibility genes. 
The system integrates **pharmacogenomic rules** to account for *drug–gene* interactions that may modulate disease risk. 
The users receive a structured PDF report summarizing lifetime AD risk, genotype-specific medication considerations, 
and evidence-based clinical recommendations. 

It is designed for usability and deployment in research or clinical settings, `genix_alz` offers a scalable, 
explainable, and data-driven approach to personalized AD prevention and decision support. 
It also can be easily deployed via Docker, and supports synthetic and real-world data formats (ADNI, UK Biobank).


> Note: This project is under active development. We are currently working on integrating patient datasets, 
> expanding the gene panel, and improving FHIR/EHR interoperability for clinical production use.

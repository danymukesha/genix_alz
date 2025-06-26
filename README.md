# genix_alz

`genix_alz` is a clinical intended-use software platform for assessing individualized Alzheimer's disease (AD) risk 
using genetic profiles, age stratification, and medication history. It uses a calibrated machine learning model trained 
on polygenic risk scores derived from validated AD-associated loci, including APOE and 10 additional susceptibility genes. 
The system integrates **pharmacogenomic rules** to account for *drug–gene* interactions that may modulate disease risk. 
The users receive a structured PDF report summarizing lifetime AD risk, genotype-specific medication considerations, 
and evidence-based clinical recommendations. 

It is designed for usability and deployment in research or clinical settings, `genix_alz` offers a scalable, 
explainable, and data-driven approach to personalized AD prevention and decision support. 
It also can be easily deployed via Docker, and supports other various data formats (e.g.:ADNI, UK Biobank).


> Note: This project is under active development. We are currently working on integrating patient datasets, 
> expanding the gene panel, and improving FHIR/EHR interoperability for clinical production use.
> Currently, the large datasets (ADNI, UK Biobank) are being integrated and use to refine the predictive model
> for production-grade accuracy and regulatory readiness.
----
Here is guide on how to run the application:
1. Set up the environment
```sh
git clone https://github.com/danymukesha/genix_alz.git
cd genix_alz
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Run with sample data provide with the application
```sh
python src/cli.py --input data/sample_patient.json --output my_report.pdf
```
3. Build a Docker img
```sh
docker build -t genix_alz .
docker run -v $(pwd)/output:/output genix_alz
```

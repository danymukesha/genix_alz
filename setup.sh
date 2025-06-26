# genix_alz/setup.sh
#!/bin/bash

mkdir -p genix_alz/{data,src,models}

touch genix_alz/data/drug_interactions.json
touch genix_alz/data/sample_patient.json
touch genix_alz/src/{risk_calculator.py,drug_checker.py,report_generator.py,cli.py}
touch genix_alz/Dockerfile
touch genix_alz/requirements.txt

echo "The `genix_alz` project structure created."

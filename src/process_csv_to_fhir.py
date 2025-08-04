# Placeholder for fhir_client.py logic
import os
import json
import argparse
import pandas as pd
from fhir_client import FHIRClient

def csv_to_fhir_patient(row: pd.Series) -> dict:
    """
    Converts a row from a pandas DataFrame into a FHIR Patient resource.
    """
    patient = {
        "resourceType": "Patient",
        "identifier": [
            {
                "system": "urn:oid:1.2.36.1.2001.1005.17",
                "value": str(row['id'])
            }
        ],
        "name": [
            {
                "family": row['family_name'],
                "given": [row['given_name']]
            }
        ],
        "gender": row['gender'],
        "birthDate": row['birth_date']
    }
    return patient

def process_csv_file(client: FHIRClient, input_csv: str, output_dir: str, upload_to_fhir: bool):
    """
    Reads a CSV, converts each row to a FHIR Patient resource, and
    optionally saves or uploads it to the server.
    """
    if not os.path.exists(input_csv):
        print(f"Error: CSV file '{input_csv}' not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    resource_count = 0
    print(f"Processing {len(df)} rows from {input_csv}...")

    for _, row in df.iterrows():
        try:
            fhir_patient = csv_to_fhir_patient(row)
            
            if upload_to_fhir:
                response = client.create_resource("Patient", fhir_patient)
                if response:
                    resource_count += 1
                    print(f"  -> Uploaded Patient with ID {response.get('id')}")
            else:
                filename = f"patient_{row['id']}.json"
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'w') as f:
                    json.dump(fhir_patient, f, indent=2)
                resource_count += 1
                print(f"  -> Saved Patient to {filename}")
        except Exception as e:
            print(f"Error processing row for ID {row['id']}: {e}")

    print(f"Finished processing. Total resources handled: {resource_count}")

if __name__ == "__main__":
    fhir_client = FHIRClient('http://localhost:8080/fhir')

    # Example CSV data for your project's `data/` directory
    # Create a file named `data/sample_patients.csv` and add this content:
    # id,given_name,family_name,gender,birth_date
    # 101,John,Doe,male,1980-05-15
    # 102,Jane,Smith,female,1992-11-23

    parser = argparse.ArgumentParser(description="Process a CSV file and convert to FHIR Patient resources.")
    parser.add_argument("--input-csv", required=True, help="Path to the input CSV file.")
    parser.add_argument("--output-dir", required=True, help="Path to the directory to save the converted FHIR files.")
    parser.add_argument("--upload-to-fhir", action='store_true', help="Flag to upload the resources to the FHIR server instead of just saving.")
    
    args = parser.parse_args()
    
    process_csv_file(fhir_client, args.input_csv, args.output_dir, args.upload_to_fhir)
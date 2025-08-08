import os
import json
import argparse
import logging
import requests

# A simple FHIR Client class to handle the API calls
class FHIRClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        logging.info(f"FHIR Client initialized with base URL: {self.base_url}")

    def upload_bundle(self, bundle: dict):
        """
        Uploads a FHIR transaction bundle to the server's base URL.
        """
        headers = {
            "Content-Type": "application/fhir+json"
        }
        try:
            response = requests.post(self.base_url, json=bundle, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

def upload_synthea_bundles(client: FHIRClient, data_dir: str):
    """
    Reads Synthea-generated FHIR transaction Bundles from a directory and uploads them.
    """
    bundle_count = 0
    success_count = 0

    if not os.path.isdir(data_dir):
        logging.error(f"Directory not found: {data_dir}")
        return

    logging.info(f"Scanning directory for Synthea Bundles: {data_dir}")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(data_dir, filename)
            bundle_count += 1
            logging.info(f"  -> Processing file: {filename}")
            try:
                with open(file_path, 'r') as f:
                    bundle_data = json.load(f)

                # Validate that it's a transaction bundle from Synthea
                if bundle_data.get('resourceType') == "Bundle" and bundle_data.get('type') == "transaction":
                    response = client.upload_bundle(bundle_data)
                    if response:
                        success_count += 1
                        logging.info(f"    -> Successfully uploaded Bundle {filename}")
                    else:
                        logging.error(f"    -> Failed to upload Bundle {filename}")
                else:
                    logging.warning(f"  -> Skipping file {filename}: Not a valid FHIR transaction Bundle.")

            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")

    logging.info(f"Finished uploading. {success_count}/{bundle_count} bundles uploaded successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Synthea FHIR transaction Bundles to a server.")
    parser.add_argument("--data-dir", required=True, help="Path to the directory containing the Synthea FHIR JSON files (e.g., 'data-generation/output/fhir').")
    
    args = parser.parse_args()

    # The HAPI server base URL is typically just the server base
    fhir_client = FHIRClient('http://localhost:8080/fhir')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    upload_synthea_bundles(fhir_client, args.data_dir)
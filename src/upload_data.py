import os
import json
import argparse
import logging
from fhir_client import FHIRClient

def upload_fhir_data(client: FHIRClient, data_dir: str, resource_type: str):
    """
    Reads FHIR JSON files from a directory and uploads them to the server.
    This final version handles Bundles by uploading each resource individually.
    """
    resource_count = 0
    directory_to_scan = os.path.join(data_dir, resource_type)

    if not os.path.isdir(directory_to_scan):
        logging.error(f"Error: Directory '{directory_to_scan}' not found.")
        return

    logging.info(f"Uploading files from directory: {directory_to_scan}")
    for filename in os.listdir(directory_to_scan):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_to_scan, filename)
            try:
                with open(file_path, 'r') as f:
                    resource_data = json.load(f)

                # If the file is a Bundle, iterate through it and upload each entry
                if resource_data.get('resourceType') == "Bundle":
                    logging.info(f"  -> Found Bundle in {filename}. Uploading individual entries...")
                    for entry in resource_data.get('entry', []):
                        resource = entry.get('resource')
                        if resource:
                            entry_resource_type = resource.get('resourceType')
                            # Check if the resource type matches our expectation
                            if entry_resource_type == resource_type:
                                response = client.create_resource(entry_resource_type, resource)
                                if response:
                                    resource_count += 1
                                    logging.info(f"    -> Uploaded {entry_resource_type} with ID {response.get('id')}")
                            else:
                                logging.warning(f"    -> Skipping resource in Bundle: '{entry_resource_type}' does not match expected '{resource_type}'.")
                # Otherwise, assume it's a single resource and upload it
                elif resource_data.get('resourceType') == resource_type:
                    response = client.create_resource(resource_type, resource_data)
                    if response:
                        resource_count += 1
                        logging.info(f"  -> Uploaded {resource_type} from {filename} with ID {response.get('id')}")
                else:
                    logging.warning(f"  -> Skipping {filename}: resourceType '{resource_data.get('resourceType')}' does not match expected '{resource_type}'.")

            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")

    logging.info(f"Finished uploading. Total resources handled: {resource_count}")

if __name__ == "__main__":
    fhir_client = FHIRClient('http://localhost:8080/fhir')

    parser = argparse.ArgumentParser(description="Upload FHIR JSON files to a server.")
    parser.add_argument("--data-dir", required=True, help="Path to the parent directory containing FHIR resource subdirectories (e.g., 'data-generation/output/fhir').")
    parser.add_argument("--resource-type", required=True, help="The type of resource to upload (e.g., 'Patient').")

    args = parser.parse_args()

    upload_fhir_data(fhir_client, args.data_dir, args.resource_type)
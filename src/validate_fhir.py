import os
import json
import argparse
from fhir_client import FHIRClient

def validate_fhir_file(client: FHIRClient, file_path: str):
    """
    Validates a FHIR JSON file against the server's $validate endpoint.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        with open(file_path, 'r') as f:
            resource_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' is not valid JSON.")
        return
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return

    resource_type = resource_data.get('resourceType')
    if not resource_type:
        print(f"Error: File '{file_path}' is missing a 'resourceType' field.")
        return

    print(f"Validating {resource_type} resource from '{file_path}'...")
    
    # The FHIR validate operation is a POST request to the resource type's endpoint
    # with the `$validate` operation.
    response = client.create_resource(f"{resource_type}/$validate", resource_data)

    if response:
        # The response is an OperationOutcome resource
        outcome = response.get('resourceType')
        if outcome == "OperationOutcome":
            issues = response.get('issue', [])
            if issues:
                print("Validation completed with issues:")
                for issue in issues:
                    severity = issue.get('severity', 'unknown').upper()
                    code = issue.get('code', 'unknown')
                    details = issue.get('details', {}).get('text', 'No details provided.')
                    expression = issue.get('expression', [''])[0]
                    
                    print(f"  - [{severity}] Code: {code}")
                    print(f"    Details: {details}")
                    if expression:
                        print(f"    Location: {expression}")
            else:
                print("Validation successful: No issues found.")
        else:
            print(f"Unexpected response from server: {response}")
    else:
        print("Validation failed: Could not connect to server or received an error.")

if __name__ == "__main__":
    fhir_client = FHIRClient('http://localhost:8080/fhir')
    
    parser = argparse.ArgumentParser(description="Validate a FHIR JSON file.")
    parser.add_argument("--file", required=True, help="Path to the FHIR JSON file to validate.")
    
    args = parser.parse_args()
    
    validate_fhir_file(fhir_client, args.file)
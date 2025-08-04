import json
import logging
from typing import Dict, Any, Optional

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FHIRClient:
    """
    A simple client for interacting with a FHIR server.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def _make_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
        """
        Internal method to handle HTTP requests and error logging.
        """
        url = f"{self.base_url}{path}"
        headers = {'Content-Type': 'application/fhir+json'}
        try:
            logging.info(f"Making {method} request to {url}")
            response = requests.request(method, url, headers=headers, data=json.dumps(data) if data else None)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def create_resource(self, resource_type: str, resource_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Creates a new FHIR resource.
        """
        path = f"{resource_type}"
        response = self._make_request('POST', path, data=resource_data)
        if response:
            logging.info(f"Successfully created {resource_type}. ID: {response.json().get('id')}")
            return response.json()
        return None

    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single FHIR resource by ID.
        """
        path = f"{resource_type}/{resource_id}"
        response = self._make_request('GET', path)
        if response:
            logging.info(f"Successfully retrieved {resource_type} with ID: {resource_id}")
            return response.json()
        return None

    def search_resources(self, resource_type: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Searches for FHIR resources based on parameters.
        Returns a FHIR Bundle.
        """
        path = f"{resource_type}"
        response = self._make_request('GET', path, params=params)
        if response:
            logging.info(f"Successfully searched for {resource_type}. Found {len(response.json().get('entry', []))} entries.")
            return response.json()
        return None

if __name__ == '__main__':
    # This block is for testing the client independently
    test_client = FHIRClient('http://localhost:8080/fhir')
    
    # Example: Create a new Patient
    new_patient = {
        "resourceType": "Patient",
        "name": [{"family": "Test", "given": ["Client"]}],
        "gender": "other",
        "birthDate": "1990-01-01"
    }
    created_patient = test_client.create_resource("Patient", new_patient)
    if created_patient:
        patient_id = created_patient.get('id')
        print(f"Created Patient ID: {patient_id}")
        
        # Example: Retrieve the created patient
        retrieved_patient = test_client.get_resource("Patient", patient_id)
        if retrieved_patient:
            print(f"Retrieved Patient Name: {retrieved_patient.get('name')[0].get('family')}")
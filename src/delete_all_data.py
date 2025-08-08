import sys
import logging
from fhir_client import FHIRClient

def delete_all_resources(client: FHIRClient, resource_type: str):
    """
    Deletes all resources of a given type from the FHIR server.
    """
    logging.info(f"Searching for all {resource_type} resources to delete...")
    
    # We will search for resources 50 at a time to handle large datasets
    all_resources = []
    
    # Use a loop to fetch all resources, handling pagination if necessary
    next_url = f"{client.base_url}{resource_type}?_count=50"
    
    while next_url:
        response = client._make_request('GET', next_url.replace(client.base_url, ''))
        if not response:
            logging.error("Failed to fetch resources. Aborting deletion.")
            return
        
        bundle = response.json()
        entries = bundle.get('entry', [])
        
        for entry in entries:
            resource = entry.get('resource')
            if resource and resource.get('id'):
                all_resources.append(resource)
        
        next_url_entry = [link for link in bundle.get('link', []) if link.get('relation') == 'next']
        next_url = next_url_entry[0].get('url') if next_url_entry else None

    if not all_resources:
        logging.info(f"No {resource_type} resources found to delete.")
        return
    
    logging.info(f"Found {len(all_resources)} {resource_type} resources. Deleting them now...")
    
    deleted_count = 0
    for resource in all_resources:
        resource_id = resource.get('id')
        logging.info(f"  -> Deleting {resource_type}/{resource_id}")
        delete_response = client._make_request('DELETE', f"{resource_type}/{resource_id}")
        if delete_response:
            deleted_count += 1
        else:
            logging.warning(f"  -> Failed to delete {resource_type}/{resource_id}")
            
    logging.info(f"Finished deleting. Total resources deleted: {deleted_count}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    client = FHIRClient('http://localhost:8080/fhir')
    
    if len(sys.argv) < 2:
        print("Usage: python src/delete_all_data.py <resource_type>")
        sys.exit(1)
        
    resource_type_to_delete = sys.argv[1]
    delete_all_resources(client, resource_type_to_delete)
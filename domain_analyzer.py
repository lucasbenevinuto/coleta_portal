#!/usr/bin/env python3

import requests
import json
import time
import os
import sys
from typing import List

api_keys = ["b983a304a2msh2a9bf1ffaa4ee99p14c3c0jsndf5a6a8479cd", "06f2037979msh9d39374ceca037fp13ad8cjsnd6a2ef4ff0be", "1aa5df23dcmsha2d879af1e56a6ap12e3cejsn55e24c9f7ed9"]

def create_jsons_directory():
    """Create jsons directory if it doesn't exist"""
    if not os.path.exists("jsons"):
        os.makedirs("jsons")

def read_domains(file_path: str) -> List[str]:
    """Read domains from a text file, one domain per line"""
    try:
        with open(file_path, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
        return domains
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def select_api_key_for_request(request_index: int, keys: List[str]) -> str:
    """Return the API key according to the required distribution: 45, 45, then the rest."""
    if len(keys) == 0:
        raise ValueError("No API keys provided")
    if len(keys) < 3:
        # Fallback if fewer keys are provided: use the last key for the remainder
        return keys[min(request_index, len(keys) - 1)]

    if request_index < 45:
        return keys[0]
    if request_index < 90:
        return keys[1]
    return keys[2]

def make_request_with_retry(domain: str, api_key: str, max_retries: int = 20) -> dict:
    """Make API request with retry logic"""
    url = "https://similarweb12.p.rapidapi.com/v3/website-analytics/"
    
    headers = {
        'x-rapidapi-host': 'similarweb12.p.rapidapi.com',
        'x-rapidapi-key': api_key
    }
    
    params = {
        'domain': domain
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to fetch data for {domain} (attempt {attempt + 1}/{max_retries})")
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP {response.status_code} for {domain} on attempt {attempt + 1}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {domain} on attempt {attempt + 1}: {str(e)}")
            
        if attempt < max_retries - 1:
            time.sleep(2)  # Wait 2 seconds between retries
    
    print(f"Failed to fetch data for {domain} after {max_retries} attempts")
    return None

def save_json_response(domain: str, data: dict):
    """Save JSON response to file"""
    filename = f"jsons/{domain}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved data for {domain} to {filename}")
    except Exception as e:
        print(f"Error saving data for {domain}: {str(e)}")

def main():
    # Check if domains file is provided
    if len(sys.argv) != 2:
        print("Usage: python domain_analyzer.py <domains_file>")
        print("Example: python domain_analyzer.py cleaned_domains.txt")
        sys.exit(1)
    
    domains_file = sys.argv[1]
    
    # Create jsons directory
    create_jsons_directory()
    
    # Read domains from file
    domains = read_domains(domains_file)
    
    if not domains:
        print("No domains found in the file.")
        sys.exit(1)
    
    print(f"Found {len(domains)} domains to process")
    
    # Process each domain
    for i, domain in enumerate(domains):
        print(f"\nProcessing domain {i + 1}/{len(domains)}: {domain}")
        
        # Select API key based on request index
        current_key = select_api_key_for_request(i, api_keys)
        key_segment = 1 if i < 45 else (2 if i < 90 else 3)
        print(f"Using API key segment {key_segment}")
        
        # Make request with retry logic
        data = make_request_with_retry(domain, current_key)
        
        if data:
            # Save JSON response
            save_json_response(domain, data)
        else:
            print(f"Skipping {domain} - no data received")
        
        # Wait 30 seconds before next request (except for the last one)
        if i < len(domains) - 1:
            print("Waiting 30 seconds before next request...")
            time.sleep(30)
    
    print(f"\nCompleted processing all {len(domains)} domains")

if __name__ == "__main__":
    main()
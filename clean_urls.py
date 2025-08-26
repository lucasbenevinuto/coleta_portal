#!/usr/bin/env python3

import pandas as pd
import re
from urllib.parse import urlparse, parse_qs

def extract_domain_from_url_feed(url_feed):
    """Extract clean domain from Google News RSS URL"""
    if pd.isna(url_feed) or not url_feed:
        return None
    
    try:
        # Parse the Google News URL
        parsed_url = urlparse(url_feed)
        
        # Extract the 'q' parameter which contains the site: query
        query_params = parse_qs(parsed_url.query)
        q_param = query_params.get('q', [''])[0]
        
        # Extract domain from site: parameter using regex
        site_match = re.search(r'site:(?:https?://)?(?:www\.)?([^/\s\+]+)', q_param)
        
        if site_match:
            domain = site_match.group(1)
            # Remove trailing slash if present
            domain = domain.rstrip('/')
            return domain
        else:
            return None
            
    except Exception as e:
        print(f"Error processing URL: {url_feed} - {str(e)}")
        return None

def main():
    # Read the CSV file
    csv_file = '/home/lucas/Code/Trin/Monitoramento/fluxorelatorio/lista.csv'
    
    try:
        df = pd.read_csv(csv_file)
        
        # Create a new column with cleaned domains
        df['clean_domain'] = df['url_feed'].apply(extract_domain_from_url_feed)
        
        # Display results
        print("Cleaned domains:")
        print("================")
        
        # Show only rows where we successfully extracted a domain
        valid_domains = df[df['clean_domain'].notna()][['nome', 'url_feed', 'clean_domain']]
        
        for _, row in valid_domains.iterrows():
            print(f"{row['nome']}: {row['clean_domain']}")
        
        # Save domains to a text file for use with domain_analyzer.py
        domains_list = valid_domains['clean_domain'].dropna().unique().tolist()
        
        with open('cleaned_domains.txt', 'w') as f:
            for domain in sorted(domains_list):
                f.write(f"{domain}\n")
        
        print(f"\n{len(domains_list)} unique domains saved to 'cleaned_domains.txt'")
        
        # Optionally save the updated CSV with the new column
        output_csv = 'lista_with_clean_domains.csv'
        df.to_csv(output_csv, index=False)
        print(f"Updated CSV saved to '{output_csv}'")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")

if __name__ == "__main__":
    main()
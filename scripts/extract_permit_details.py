import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag


def parse_table(table: Tag) -> list[dict[str, Any]]:
    """Parse an HTML table into a list of dictionaries."""
    rows = []
    headers = []
    
    # Get headers
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    
    # If no thead, check first row
    if not headers:
        tbody = table.find('tbody')
        if tbody:
            first_row = tbody.find('tr')
        else:
            first_row = table.find('tr')
        
        if first_row:
            cells = first_row.find_all(['th', 'td'])
            # Use text from cells as headers
            headers = [cell.get_text(strip=True) for cell in cells]
    
    # Get data rows
    tbody = table.find('tbody')
    if tbody:
        data_rows = tbody.find_all('tr')
    else:
        data_rows = table.find_all('tr')
    
    # Skip first row (headers)
    data_rows = data_rows[1:] if data_rows else []
    
    for row in data_rows:
        cells = row.find_all(['td', 'th'])
        if cells:
            row_data = {}
            for idx, cell in enumerate(cells):
                header = headers[idx] if idx < len(headers) else f"Column {idx+1}"
                row_data[header] = cell.get_text(strip=True)
            
            # Only add non-empty rows
            if any(v for v in row_data.values()):
                rows.append(row_data)
    
    return rows


def clean_text(text: str) -> str:
    """Clean up text by removing extra whitespace."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Clean up newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def extract_permit_details(url):
    """Extract permit details from Parivahan website"""
    print(f"Fetching {url}...")
    
    # Add headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Try with timeout and retries
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}...")
            response = requests.get(url, headers=headers, timeout=30, verify=True)
            response.raise_for_status()
            print(f"Success! Status Code: {response.status_code}")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                raise
    
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f"Page Title: {soup.title.string if soup.title else 'No title'}\n")
    
    print("="*80)
    print("EXTRACTING STRUCTURED PERMIT DETAILS")
    print("="*80 + "\n")
    
    # Initialize data structure
    permit_data: dict[str, Any] = {
        "page_title": soup.title.string if soup.title else None,
        "url": url,
        "extraction_date": time.strftime("%Y-%m-%d"),
        "permit_categories": []
    }
    
    # Find main content
    main_content = soup.find('div', class_='node__content')
    if not main_content:
        print("Error: Could not find main content div")
        return None
    
    print("Found main content area\n")
    
    # Find the field body div which contains all the content
    field_body = main_content.find('div', class_='field--name-body')
    if not field_body:
        print("Error: Could not find field body")
        return None
    
    # Get all children in order
    children = list(field_body.children)
    
    # Process content
    current_category = None
    current_subsection = None
    
    for element in children:
        if not isinstance(element, Tag):
            continue
        
        if element.name == 'h2':
            # New major category
            category_title = element.get_text(strip=True)
            
            # Skip the first generic heading
            if category_title.lower() == 'types of permit and its condition':
                continue
            
            print(f"Processing category: {category_title}")
            
            current_category = {
                "category": category_title,
                "subsections": []
            }
            permit_data['permit_categories'].append(current_category)
            current_subsection = None
            
        elif element.name == 'h3':
            # H3 subsection
            subsection_title = element.get_text(strip=True)
            
            if current_category:
                current_subsection = {
                    "title": subsection_title,
                    "description": [],
                    "tables": []
                }
                current_category['subsections'].append(current_subsection)
            
        elif element.name == 'p':
            # Check if it's a bold paragraph (subsection title)
            classes = element.get('class', [])
            
            if 'font-bold' in classes:
                # This is a subsection title
                subsection_title = clean_text(element.get_text())
                
                if subsection_title and current_category:
                    current_subsection = {
                        "title": subsection_title,
                        "description": [],
                        "tables": []
                    }
                    current_category['subsections'].append(current_subsection)
            else:
                # Regular paragraph
                text = clean_text(element.get_text())
                
                if text:
                    if current_subsection:
                        current_subsection['description'].append(text)
                    elif current_category:
                        # Create a general subsection if none exists
                        if not current_category['subsections']:
                            current_subsection = {
                                "title": "General Information",
                                "description": [],
                                "tables": []
                            }
                            current_category['subsections'].append(current_subsection)
                            current_subsection = current_category['subsections'][0]
                        current_subsection['description'].append(text)
                        
        elif element.name == 'table':
            # Parse table
            table_data = parse_table(element)
            
            if table_data:
                if current_subsection:
                    current_subsection['tables'].append(table_data)
                elif current_category:
                    # Create a subsection for tables without a title
                    if not current_category['subsections']:
                        current_subsection = {
                            "title": "Tables",
                            "description": [],
                            "tables": []
                        }
                        current_category['subsections'].append(current_subsection)
                    else:
                        current_subsection = current_category['subsections'][-1]
                    current_subsection['tables'].append(table_data)
    
    # Clean up subsections - join descriptions
    for category in permit_data['permit_categories']:
        for subsection in category['subsections']:
            if subsection['description']:
                subsection['description'] = '\n\n'.join(subsection['description'])
            else:
                subsection['description'] = ""
            
            # Remove empty tables
            subsection['tables'] = [t for t in subsection['tables'] if t]
    
    print(f"\n{'='*80}")
    print(f"Total permit categories extracted: {len(permit_data['permit_categories'])}")
    total_subsections = sum(len(cat['subsections']) for cat in permit_data['permit_categories'])
    total_tables = sum(len(sub['tables']) for cat in permit_data['permit_categories'] for sub in cat['subsections'])
    print(f"Total subsections: {total_subsections}")
    print(f"Total tables: {total_tables}")
    print(f"{'='*80}\n")
    
    return permit_data


def main():
    parser = argparse.ArgumentParser(description='Extract permit details from Parivahan')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://parivahan.gov.in/content/about-permit',
        help='URL to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/permit_details.json',
        help='Output file path (default: data/permit_details.json)'
    )
    args = parser.parse_args()
    
    # Extract permit details
    permit_data = extract_permit_details(args.url)
    
    if permit_data:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(permit_data, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved to {output_path}")
        
        # Display summary
        print(f"\n{'='*80}")
        print("EXTRACTION SUMMARY:")
        print(f"{'='*80}")
        
        for idx, category in enumerate(permit_data['permit_categories'][:3], 1):
            print(f"\n{idx}. {category['category']}")
            for sub_idx, subsection in enumerate(category['subsections'][:2], 1):
                print(f"   {sub_idx}. {subsection['title']}")
                if subsection.get('tables'):
                    print(f"      └─ {len(subsection['tables'])} table(s)")
                if subsection.get('description'):
                    desc_len = len(subsection['description'])
                    print(f"      └─ Description: {desc_len} characters")
    else:
        print("\n⚠ No permit details extracted.")


if __name__ == "__main__":
    main()

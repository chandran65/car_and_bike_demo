import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag


def parse_table(table: Tag) -> list[dict[str, Any]]:
    """Parse an HTML table into a list of dictionaries with improved hierarchical handling."""
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
            # Check if first row looks like headers (all bold or all th tags)
            if all(cell.name == 'th' for cell in cells) or all(cell.find('strong') or cell.find('b') for cell in cells):
                headers = [cell.get_text(strip=True) for cell in cells]
    
    # Get data rows
    tbody = table.find('tbody')
    if tbody:
        data_rows = tbody.find_all('tr')
    else:
        data_rows = table.find_all('tr')
    
    # Skip first row if it was used as headers
    if headers and data_rows:
        # Check if first row matches headers
        first_cells = data_rows[0].find_all(['td', 'th'])
        first_row_text = [cell.get_text(strip=True) for cell in first_cells]
        if first_row_text == headers:
            data_rows = data_rows[1:]
    
    # Track the current serial number for hierarchical structure
    current_sl_no = None
    
    for row in data_rows:
        cells = row.find_all(['td', 'th'])
        if cells:
            row_data = {}
            for idx, cell in enumerate(cells):
                header = headers[idx] if idx < len(headers) else f"Column_{idx+1}"
                value = cell.get_text(strip=True)
                
                # Normalize section field - replace --- or -- with null
                if header == 'Section' and value in ['---', '--', '']:
                    value = None
                
                row_data[header] = value
            
            # Handle hierarchical serial numbers
            if 'Sl.No.' in row_data:
                sl_no = row_data['Sl.No.']
                if sl_no and sl_no.strip():
                    # This row has a serial number - update current
                    current_sl_no = sl_no
                else:
                    # This row is a sub-item - inherit parent's serial number
                    if current_sl_no:
                        row_data['Sl.No.'] = current_sl_no
            
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


def extract_fees(url):
    """Extract fees and charges from Parivahan website"""
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
    print("EXTRACTING FEES AND USER CHARGES DETAILS")
    print("="*80 + "\n")
    
    # Initialize data structure
    fees_data: dict[str, Any] = {
        "page_title": soup.title.string if soup.title else None,
        "url": url,
        "extraction_date": time.strftime("%Y-%m-%d"),
        "fee_categories": [],
        "notes": []
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
    
    # Find the main fees table
    table = field_body.find('table')
    if table:
        print("Found fees table\n")
        print("Parsing table data...")
        
        # Parse the table
        fees_list = parse_table(table)
        
        print(f"Extracted {len(fees_list)} raw fee entries")
        print("Building hierarchical structure...")
        
        # Build hierarchical structure
        current_category = None
        
        for fee_entry in fees_list:
            sl_no = fee_entry.get('Sl.No.', '').strip()
            purpose = fee_entry.get('Purpose', '').strip()
            amount = fee_entry.get('Amount', '').strip()
            rule = fee_entry.get('Rule', '').strip()
            section = fee_entry.get('Section')
            
            # Check if this is a main category (has serial number and either no amount or is a category header)
            is_main_category = False
            if sl_no and sl_no.endswith('.'):
                # Check if this looks like a category (no amount or is descriptive)
                if not amount or purpose.endswith(':'):
                    is_main_category = True
            
            if is_main_category:
                # Start new category
                current_category = {
                    "sl_no": sl_no,
                    "category": purpose,
                    "items": []
                }
                fees_data['fee_categories'].append(current_category)
            else:
                # This is a sub-item
                item = {
                    "purpose": purpose
                }
                
                if amount:
                    item["amount"] = amount
                if rule:
                    item["rule"] = rule
                if section is not None:
                    item["section"] = section
                
                # Add to current category or create a misc category
                if current_category:
                    current_category['items'].append(item)
                else:
                    # Create a misc category for items without a parent
                    if not fees_data['fee_categories'] or fees_data['fee_categories'][-1].get('category') != 'Miscellaneous':
                        current_category = {
                            "sl_no": "N/A",
                            "category": "Miscellaneous",
                            "items": []
                        }
                        fees_data['fee_categories'].append(current_category)
                    current_category['items'].append(item)
        
        print(f"Created {len(fees_data['fee_categories'])} fee categories")
    else:
        print("Warning: No table found")
    
    # Extract notes
    notes_divs = field_body.find_all('div', class_='bottom-space')
    print(f"\nFound {len(notes_divs)} note sections")
    
    for idx, note_div in enumerate(notes_divs, 1):
        note_text = clean_text(note_div.get_text())
        if note_text:
            fees_data['notes'].append(note_text)
            print(f"  Note {idx}: {note_text[:80]}...")
    
    print(f"\n{'='*80}")
    print(f"Total fee categories: {len(fees_data['fee_categories'])}")
    total_items = sum(len(cat['items']) for cat in fees_data['fee_categories'])
    print(f"Total fee items: {total_items}")
    print(f"Total notes: {len(fees_data['notes'])}")
    print(f"{'='*80}\n")
    
    return fees_data


def main():
    parser = argparse.ArgumentParser(description='Extract fees and charges from Parivahan')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://parivahan.gov.in/content/fees-and-user-charges',
        help='URL to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/fees_charges.json',
        help='Output file path (default: data/fees_charges.json)'
    )
    args = parser.parse_args()
    
    # Extract fees
    fees_data = extract_fees(args.url)
    
    if fees_data:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fees_data, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved to {output_path}")
        
        # Display summary
        print(f"\n{'='*80}")
        print("EXTRACTION SUMMARY:")
        print(f"{'='*80}")
        
        print(f"\nHierarchical Structure:")
        print(f"  Total categories: {len(fees_data['fee_categories'])}")
        total_items = sum(len(cat['items']) for cat in fees_data['fee_categories'])
        print(f"  Total fee items: {total_items}")
        
        print(f"\nCategory Overview:")
        for idx, category in enumerate(fees_data['fee_categories'][:5], 1):
            print(f"  {idx}. [{category['sl_no']}] {category['category'][:60]}{'...' if len(category['category']) > 60 else ''}")
            print(f"      Items: {len(category['items'])}")
    else:
        print("\n⚠ No fees data extracted.")


if __name__ == "__main__":
    main()

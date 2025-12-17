import argparse
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_faqs(url):
    """Extract FAQs from ICICI Bank website"""
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
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            print(f"Success! Status Code: {response.status_code}")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                raise
    
    # Get HTML content (kept in memory only)
    html_content = response.text
    
    print(f"Page Title: {response.url}\n")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("Analyzing page structure...\n")
    
    # Extract FAQs from the specific structure used by ICICI Bank
    # Find all faq-item divs
    faq_items = soup.find_all('div', class_='faq-item')
    print(f"Found {len(faq_items)} FAQ items")
    
    # Store FAQs
    faqs = []
    faqs_by_category = {}
    
    # Check if there's a category/topic header
    category_header = soup.find('div', class_='faq-topic')
    if category_header:
        category = category_header.find('h2')
        category = category.get_text(strip=True) if category else "Car Insurance"
    else:
        category = "Car Insurance"
    
    print(f"\nCategory: {category}")
    faqs_by_category[category] = []
    
    for idx, item in enumerate(faq_items, 1):
        # Extract question from div.faq-question > h3
        question_div = item.find('div', class_='faq-question')
        if not question_div:
            continue
        
        question_h3 = question_div.find('h3')
        if not question_h3:
            continue
        
        question = question_h3.get_text(strip=True)
        
        # Extract answer from div.faq-answer
        answer_div = item.find('div', class_='faq-answer')
        if not answer_div:
            continue
        
        # Get all text from paragraphs and list items
        answer_parts = []
        for element in answer_div.find_all(['p', 'li', 'strong', 'br']):
            if element.name == 'br':
                continue
            text = element.get_text(strip=True)
            if text:
                answer_parts.append(text)
        
        # If no specific elements found, get all text from div
        if not answer_parts:
            answer = answer_div.get_text(separator=' ', strip=True)
        else:
            answer = ' '.join(answer_parts)
        
        # Clean up the answer - remove extra whitespace
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        if question and answer and len(answer) > 10:
            faq_entry = {
                'question': question,
                'answer': answer
            }
            
            faqs_by_category[category].append(faq_entry)
            faqs.append({
                'category': category,
                'question': question,
                'answer': answer
            })
            
            if idx <= 3:  # Show first 3 FAQs during extraction
                print(f"  ✓ FAQ {idx}: {question[:60]}...")
    
    print(f"\n{'='*80}")
    print(f"Total FAQs extracted: {len(faqs)}")
    print(f"{'='*80}\n")
    
    return faqs_by_category


def main():
    parser = argparse.ArgumentParser(description='Extract FAQs from ICICI Bank website')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://www.icicibank.com/personal-banking/insurance/general-insurance/motor-insurance/car-insurance/car-insurance-faqs',
        help='URL to scrape (default: ICICI Bank car insurance FAQs)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/icici_faqs.json',
        help='Output file path (default: data/icici_faqs.json)'
    )
    args = parser.parse_args()
    
    # Extract FAQs
    faqs_by_category = extract_faqs(args.url)
    
    if faqs_by_category:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save hierarchical structure to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(faqs_by_category, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved to {output_path}")
        
        # Show some statistics
        total_faqs = sum(len(faqs) for faqs in faqs_by_category.values())
        print(f"\n{'='*80}")
        print("STATISTICS:")
        print(f"{'='*80}")
        print(f"Total FAQs: {total_faqs}")
        
        print(f"\nFAQs by category:")
        for cat, faq_list in faqs_by_category.items():
            print(f"  - {cat}: {len(faq_list)} FAQs")
    else:
        print("\n⚠ No FAQs found with current extraction logic.")


if __name__ == "__main__":
    main()

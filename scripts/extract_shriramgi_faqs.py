import argparse
import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def clean_text(text):
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return text
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def fetch_page_with_playwright(url):
    """Fetch the page with Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        print("Navigating to page...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("Waiting for content to load...")
        time.sleep(3)
        
        # Scroll to trigger lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        
        title = page.title()
        print(f"Page Title: {title}\n")
        
        html_content = page.content()
        
        browser.close()
        return html_content


def extract_faqs(url):
    """Extract FAQs from Shriram GI"""
    print(f"Fetching {url} with Playwright...")
    
    # Fetch the page
    html_content = fetch_page_with_playwright(url)
    
    if not html_content:
        print("\n❌ Failed to fetch the page.")
        return None
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("Analyzing page structure...\n")
    
    # Store FAQs hierarchically by category
    faqs_by_category = {}
    faqs = []  # Flat list
    
    # Find all tabcontent divs (each represents a category)
    tab_contents = soup.find_all('div', class_='tabcontent')
    print(f"Found {len(tab_contents)} FAQ categories")
    
    for tab_content in tab_contents:
        # Get category name from the id attribute
        category = tab_content.get('id', 'Uncategorized')
        
        print(f"\nProcessing category: {category}")
        
        # Find all FAQ items within this category
        faq_items = tab_content.find_all('div', class_='faq')
        print(f"  Found {len(faq_items)} FAQs in this category")
        
        # Initialize category list if not exists
        if category not in faqs_by_category:
            faqs_by_category[category] = []
        
        for item in faq_items:
            # Extract question from h4 with class 'accordion'
            question_h4 = item.find('h4', class_='accordion')
            if not question_h4:
                continue
            
            question = question_h4.get_text(strip=True)
            
            # Extract answer from div with class 'panel'
            answer_div = item.find('div', class_='panel')
            if not answer_div:
                continue
            
            # Get all text from the answer div, including nested elements
            answer_parts = []
            
            # Get text from paragraphs and list items
            for element in answer_div.find_all(['p', 'li']):
                text = element.get_text(strip=True)
                if text:
                    answer_parts.append(text)
            
            # If no specific elements found, get all text from div
            if not answer_parts:
                answer = answer_div.get_text(separator=' ', strip=True)
            else:
                answer = ' '.join(answer_parts)
            
            # Clean the question and answer
            question = clean_text(question)
            answer = clean_text(answer)
            
            # Only add if both question and answer exist and answer is substantial
            if question and answer and len(answer) > 10:
                faqs_by_category[category].append({
                    'question': question,
                    'answer': answer
                })
                # Also keep flat structure
                faqs.append({
                    'category': category,
                    'question': question,
                    'answer': answer
                })
    
    print(f"\n{'='*80}")
    print(f"Total FAQs extracted: {len(faqs)}")
    print(f"{'='*80}\n")
    
    return faqs_by_category


def main():
    parser = argparse.ArgumentParser(description='Extract FAQs from Shriram GI')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://www.shriramgi.com/motor-insurance/faqs',
        help='URL to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/shriramgi_faqs.json',
        help='Output file path (default: data/shriramgi_faqs.json)'
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

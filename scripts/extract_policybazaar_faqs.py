import argparse
import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def try_with_browser(browser_type, p, url):
    """Try to fetch the page with a specific browser"""
    print(f"\nTrying with {browser_type}...")
    
    try:
        if browser_type == 'firefox':
            browser = p.firefox.launch(
                headless=True,
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "useAutomationExtension": False
                }
            )
        else:  # chromium
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
        page = context.new_page()
        
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
        
        print("Navigating to page...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Error with domcontentloaded: {e}")
            print("Trying with load event...")
            page.goto(url, wait_until="load", timeout=60000)
        
        print("Waiting for content to load...")
        time.sleep(5)
        
        # Scroll to trigger lazy loading
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        
        title = page.title()
        print(f"Page Title: {title}\n")
        
        html_content = page.content()
        
        browser.close()
        return html_content, True
        
    except Exception as e:
        print(f"Failed with {browser_type}: {e}")
        try:
            browser.close()
        except:
            pass
        return None, False


def extract_faqs(url):
    """Extract FAQs from PolicyBazaar"""
    print(f"Fetching {url} with Playwright...")
    
    faqs = []
    
    # Try browsers in order
    html_content = None
    success = False
    
    with sync_playwright() as p:
        for browser_type in ['firefox', 'chromium']:
            html_content, success = try_with_browser(browser_type, p, url)
            if success and html_content:
                print(f"✓ Successfully fetched with {browser_type}!")
                break
    
    if not success or not html_content:
        print("\n❌ Failed to fetch the page with all browsers.")
        print("The website has strong anti-bot protection.")
        return None
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("Analyzing page structure...\n")
    
    # Extract FAQs from the specific structure used by PolicyBazaar
    # Find all faqsWrap containers
    faqs_wraps = soup.find_all('div', class_='faqsWrap')
    print(f"Found {len(faqs_wraps)} FAQ category sections")
    
    # Store FAQs hierarchically by category
    faqs_by_category = {}
    
    for wrap in faqs_wraps:
        # Get the category name from h2
        category_h2 = wrap.find('h2')
        category = category_h2.get_text(strip=True) if category_h2 else "Uncategorized"
        
        print(f"\nProcessing category: {category}")
        
        # Find the ul with class data_ul
        data_ul = wrap.find('ul', class_='data_ul')
        if not data_ul:
            continue
        
        # Find all li elements (each represents one FAQ)
        faq_items = data_ul.find_all('li', recursive=False)
        print(f"  Found {len(faq_items)} FAQs in this category")
        
        # Initialize category list if not exists
        if category not in faqs_by_category:
            faqs_by_category[category] = []
        
        for item in faq_items:
            # Extract question from h3 > a
            question_h3 = item.find('h3')
            if question_h3:
                question_a = question_h3.find('a')
                question = question_a.get_text(strip=True) if question_a else question_h3.get_text(strip=True)
            else:
                continue
            
            # Remove question number (e.g., "Q1. ", "Q10. ", etc.)
            question = re.sub(r'^Q\d+\.\s*', '', question)
            
            # Extract answer from the div following h3
            answer_div = item.find('div')
            if answer_div:
                # Get all text from the div, including nested elements
                answer_parts = []
                for element in answer_div.find_all(['p', 'li', 'td', 'th']):
                    text = element.get_text(strip=True)
                    if text:
                        answer_parts.append(text)
                
                # If no specific elements found, get all text from div
                if not answer_parts:
                    answer = answer_div.get_text(separator=' ', strip=True)
                else:
                    answer = ' '.join(answer_parts)
            else:
                continue
            
            if question and answer and len(answer) > 10:
                faqs_by_category[category].append({
                    'question': question,
                    'answer': answer
                })
                # Also keep flat structure for CSV
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
    parser = argparse.ArgumentParser(description='Extract FAQs from PolicyBazaar')
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/policybazaar_faqs.json',
        help='Output file path (default: data/policybazaar_faqs.json)'
    )
    args = parser.parse_args()
    
    # URL to scrape
    url = "https://www.policybazaar.com/motor-insurance/car-insurance/frequently-asked-questions/"
    
    # Extract FAQs
    faqs_by_category = extract_faqs(url)
    
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

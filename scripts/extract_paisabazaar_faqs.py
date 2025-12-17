import argparse
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_faqs(url):
    """Extract FAQs from PaisaBazaar website"""
    print("=" * 80)
    print("EXTRACTING PAISABAZAAR CAR LOAN FAQs")
    print("=" * 80)
    
    print(f"\nFetching {url}...")
    
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
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    faqs = []
    
    # Strategy 1: Find all <strong> tags with questions that start with "Q" and contain "?"
    print("\nSearching for FAQ elements...")
    question_tags = []
    
    # First, find the h2 with Q1
    h2_q1 = soup.find('h2', string=re.compile(r'^Q1\.'))
    if h2_q1:
        question_tags.append(h2_q1)
        print(f"Found H2 question: {h2_q1.get_text(strip=True)[:80]}")
    
    # Then find all strong tags with questions
    for strong in soup.find_all('strong'):
        text = strong.get_text(strip=True)
        if re.match(r'^Q\d+\.', text) and '?' in text:
            question_tags.append(strong)
    
    print(f"Found {len(question_tags)} question elements")
    
    # Extract Q&A pairs
    for i, q_tag in enumerate(question_tags, 1):
        try:
            question_text = q_tag.get_text(strip=True)
            
            # Remove the Q number prefix (Q1., Q2., etc.)
            question = re.sub(r'^Q\d+\.\s*', '', question_text)
            
            # Now find the answer
            answer = ""
            
            if q_tag.name == 'h2':
                # For h2, the answer might be in the next paragraph(s)
                next_elem = q_tag.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol']:
                    # Check if this paragraph contains another question
                    if next_elem.find('strong', string=re.compile(r'^Q\d+\.')):
                        break
                    answer += ' ' + next_elem.get_text(separator=' ', strip=True)
                    next_elem = next_elem.find_next_sibling()
            
            elif q_tag.name == 'strong':
                # For strong tags, get the parent (usually a <p> tag)
                parent = q_tag.parent
                
                if parent and parent.name == 'p':
                    # Get all text from parent, but remove the question part
                    parent_text = parent.get_text(separator=' ', strip=True)
                    # Remove the question from the beginning
                    answer = parent_text.replace(question_text, '', 1).strip()
                    
                    # If answer is still empty or too short, check next siblings
                    if len(answer) < 20:
                        next_elem = parent.find_next_sibling()
                        while next_elem and next_elem.name == 'p':
                            # Check if this paragraph contains another question
                            if next_elem.find('strong', string=re.compile(r'^Q\d+\.')):
                                break
                            answer += ' ' + next_elem.get_text(separator=' ', strip=True)
                            next_elem = next_elem.find_next_sibling()
            
            # Clean up answer
            answer = answer.strip()
            answer = re.sub(r'\s+', ' ', answer)  # Replace multiple spaces with single space
            
            # Only add if we have both question and answer
            if question and answer and len(answer) > 20:
                faqs.append({
                    'question': question,
                    'answer': answer
                })
                print(f"\n[{i}] Q: {question[:100]}")
                print(f"    A: {answer[:150]}{'...' if len(answer) > 150 else ''}")
            else:
                print(f"\n[{i}] SKIPPED (insufficient answer): {question[:100]}")
                
        except Exception as e:
            print(f"\nError processing question {i}: {e}")
            continue
    
    print(f"\n{'=' * 80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total FAQs extracted: {len(faqs)}")
    
    return faqs


def main():
    parser = argparse.ArgumentParser(description='Extract FAQs from PaisaBazaar website')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://www.paisabazaar.com/faqs/car-loan/',
        help='URL to scrape (default: PaisaBazaar car loan FAQs)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/paisabazaar_car_loan_faqs.json',
        help='Output file path (default: data/paisabazaar_car_loan_faqs.json)'
    )
    args = parser.parse_args()
    
    # Extract FAQs
    faqs = extract_faqs(args.url)
    
    if faqs:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(faqs, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved to {output_path}")
        
        # Display statistics
        print(f"\n{'=' * 80}")
        print("STATISTICS")
        print(f"{'=' * 80}")
        print(f"Total FAQs: {len(faqs)}")
        print(f"Average question length: {sum(len(faq['question']) for faq in faqs) / len(faqs):.0f} characters")
        print(f"Average answer length: {sum(len(faq['answer']) for faq in faqs) / len(faqs):.0f} characters")
        print(f"Shortest answer: {min(len(faq['answer']) for faq in faqs)} characters")
        print(f"Longest answer: {max(len(faq['answer']) for faq in faqs)} characters")
    else:
        print("\n⚠ No FAQs extracted. Please check the HTML structure.")


if __name__ == "__main__":
    main()

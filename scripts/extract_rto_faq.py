import argparse
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_faqs(url):
    """Extract FAQs from RTO website"""
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
    
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f"Page Title: {soup.title.string if soup.title else 'No title'}\n")
    
    faqs = []
    
    # Find all FAQ title containers
    faq_title_containers = soup.find_all('div', class_='faq-title-first-child')
    print(f"Found {len(faq_title_containers)} FAQ title containers")
    
    # Find all FAQ answer containers
    faq_answer_containers = soup.find_all('div', class_='faq-answer-second-child')
    print(f"Found {len(faq_answer_containers)} FAQ answer containers")
    
    # Extract questions from title containers
    questions = []
    for container in faq_title_containers:
        title_field = container.find('div', class_='views-field-title')
        if title_field:
            # Try to find the question text in a link or span
            link = title_field.find('a')
            if link:
                question = link.get_text(strip=True)
            else:
                question = title_field.get_text(strip=True)
            
            if question and len(question) > 5:
                questions.append(question)
    
    # Extract answers from answer containers
    answers = []
    for container in faq_answer_containers:
        body_field = container.find('div', class_='views-field-body')
        if body_field:
            # Get the field content div
            field_content = body_field.find('div', class_='field-content')
            if field_content:
                # Get all text, preserving line breaks
                answer_text = field_content.get_text(separator='\n', strip=True)
                # Clean up multiple newlines
                answer_text = '\n'.join(line.strip() for line in answer_text.split('\n') if line.strip())
                answers.append(answer_text)
    
    print(f"\nExtracted {len(questions)} questions")
    print(f"Extracted {len(answers)} answers")
    
    # Pair questions with answers
    # They should be in the same order on the page
    min_length = min(len(questions), len(answers))
    for i in range(min_length):
        faqs.append({
            'question': questions[i],
            'answer': answers[i]
        })
    
    # Handle case where there are more questions than answers or vice versa
    if len(questions) > len(answers):
        print(f"\n⚠ Warning: {len(questions) - len(answers)} questions without answers")
        for i in range(len(answers), len(questions)):
            faqs.append({
                'question': questions[i],
                'answer': "[Answer not found on page]"
            })
    elif len(answers) > len(questions):
        print(f"\n⚠ Warning: {len(answers) - len(questions)} answers without questions")
    
    print(f"\n{'='*80}")
    print(f"Total FAQs extracted: {len(faqs)}")
    print(f"{'='*80}\n")
    
    return faqs


def main():
    parser = argparse.ArgumentParser(description='Extract FAQs from RTO website')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://parivahan.gov.in/en/content/faq',
        help='URL to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/rto_faqs.json',
        help='Output file path (default: data/rto_faqs.json)'
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
        
        # Show some statistics
        print(f"\n{'='*80}")
        print("STATISTICS:")
        print(f"{'='*80}")
        print(f"Total FAQs: {len(faqs)}")
        print(f"Average question length: {sum(len(faq['question']) for faq in faqs) / len(faqs):.0f} characters")
        print(f"Average answer length: {sum(len(faq['answer']) for faq in faqs) / len(faqs):.0f} characters")
        print(f"Shortest answer: {min(len(faq['answer']) for faq in faqs)} characters")
        print(f"Longest answer: {max(len(faq['answer']) for faq in faqs)} characters")
    else:
        print("\n⚠ No FAQs found with current extraction logic.")


if __name__ == "__main__":
    main()

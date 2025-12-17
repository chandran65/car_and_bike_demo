import argparse
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_qa(url):
    """Extract Q&A from RC Transfer page"""
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
    
    qa_pairs = []
    
    # Strategy 1: Look for FAQ sections (common in blogs)
    faq_sections = soup.find_all(['section', 'div'], class_=lambda x: x and ('faq' in x.lower() or 'question' in x.lower()))
    print(f"Found {len(faq_sections)} FAQ sections")
    
    # Strategy 2: Look for heading + paragraph patterns (Q&A format)
    # Common patterns: h2/h3/h4 questions followed by paragraphs
    headings = soup.find_all(['h2', 'h3', 'h4', 'h5'])
    print(f"Found {len(headings)} headings")
    
    # Extract Q&A from headings that look like questions
    for heading in headings:
        heading_text = heading.get_text(strip=True)
        
        # Check if heading looks like a question (contains ? or starts with question words)
        question_indicators = ['?', 'how to', 'what is', 'why', 'when', 'where', 'who', 'can i', 'how do', 'what are']
        is_question = any(indicator in heading_text.lower() for indicator in question_indicators)
        
        if is_question or len(heading_text) > 20:  # Could be a question
            # Get the next siblings until we hit another heading
            answer_parts = []
            for sibling in heading.find_next_siblings():
                # Stop if we hit another heading
                if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
                
                # Collect text from paragraphs, lists, etc.
                if sibling.name in ['p', 'ul', 'ol', 'div']:
                    text = sibling.get_text(separator='\n', strip=True)
                    if text:
                        answer_parts.append(text)
                
                # Limit to reasonable number of elements
                if len(answer_parts) >= 5:
                    break
            
            if answer_parts:
                answer = '\n\n'.join(answer_parts)
                # Only add if answer is substantial
                if len(answer) > 30:
                    qa_pairs.append({
                        'question': heading_text,
                        'answer': answer
                    })
    
    # Strategy 3: Look for accordion/toggle patterns
    accordions = soup.find_all(['details', 'div'], class_=lambda x: x and ('accordion' in x.lower() or 'toggle' in x.lower() or 'collapse' in x.lower()))
    print(f"Found {len(accordions)} accordion/toggle elements")
    
    for accordion in accordions:
        # Look for summary/question
        summary = accordion.find(['summary', 'button', 'h3', 'h4'])
        if summary:
            question = summary.get_text(strip=True)
            # Look for content/answer
            content_div = accordion.find(['div', 'p'], class_=lambda x: x and ('content' in x.lower() or 'body' in x.lower()))
            if content_div:
                answer = content_div.get_text(separator='\n', strip=True)
                if len(answer) > 30:
                    # Check if not already added
                    if not any(qa['question'] == question for qa in qa_pairs):
                        qa_pairs.append({
                            'question': question,
                            'answer': answer
                        })
    
    # Strategy 4: Look for structured FAQ with dt/dd tags
    dl_elements = soup.find_all('dl')
    for dl in dl_elements:
        dt_elements = dl.find_all('dt')
        dd_elements = dl.find_all('dd')
        
        for dt, dd in zip(dt_elements, dd_elements):
            question = dt.get_text(strip=True)
            answer = dd.get_text(separator='\n', strip=True)
            if len(answer) > 30:
                if not any(qa['question'] == question for qa in qa_pairs):
                    qa_pairs.append({
                        'question': question,
                        'answer': answer
                    })
    
    # Remove duplicates based on question text
    seen_questions = set()
    unique_qa_pairs = []
    for qa in qa_pairs:
        if qa['question'] not in seen_questions:
            seen_questions.add(qa['question'])
            unique_qa_pairs.append(qa)
    
    qa_pairs = unique_qa_pairs
    
    print(f"\n{'='*80}")
    print(f"Total Q&A pairs extracted: {len(qa_pairs)}")
    print(f"{'='*80}\n")
    
    return qa_pairs


def main():
    parser = argparse.ArgumentParser(description='Extract Q&A from RC Transfer page')
    parser.add_argument(
        '-u', '--url',
        type=str,
        default='https://myraasta.in/blogs/rc-transfer-process-in-india-2025-step-by-step-guide-for-buyers-sellers',
        help='URL to scrape'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/rc_transfer_qa.json',
        help='Output file path (default: data/rc_transfer_qa.json)'
    )
    args = parser.parse_args()
    
    # Extract Q&A
    qa_pairs = extract_qa(args.url)
    
    if qa_pairs:
        # Ensure output directory exists
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved to {output_path}")
        
        # Show some statistics
        print(f"\n{'='*80}")
        print("STATISTICS:")
        print(f"{'='*80}")
        print(f"Total Q&A pairs: {len(qa_pairs)}")
        print(f"Average question length: {sum(len(qa['question']) for qa in qa_pairs) / len(qa_pairs):.0f} characters")
        print(f"Average answer length: {sum(len(qa['answer']) for qa in qa_pairs) / len(qa_pairs):.0f} characters")
        print(f"Shortest answer: {min(len(qa['answer']) for qa in qa_pairs)} characters")
        print(f"Longest answer: {max(len(qa['answer']) for qa in qa_pairs)} characters")
    else:
        print("\n⚠ No Q&A pairs found with current extraction logic.")


if __name__ == "__main__":
    main()

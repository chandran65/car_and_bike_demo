
import pypdf
import sys
import re

def extract_text_from_pdf(pdf_path):
    print(f"Reading {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def analyze_capabilities(text):
    if not text:
        return

    print("\n--- EXTRACTED TEXT SUMMARY ---\n")
    # print first 2000 chars to get an idea
    print(text[:2000]) 
    
    print("\n--- SEARCHING FOR 'USER JOURNEY' ---\n")
    # Find sections mentioning "User Journey"
    matches = re.finditer(r"(User Journey|Journey \d+)(.+?)(?=(User Journey|Journey \d+|$))", text, re.IGNORECASE | re.DOTALL)
    
    found_journeys = False
    for match in matches:
        found_journeys = True
        print(f"*** {match.group(1)} ***")
        content = match.group(2).strip()
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 40)

    if not found_journeys:
        print("No explicit 'User Journey' sections found via regex.")

if __name__ == "__main__":
    pdf_path = "Capabilities Document for AI Driven Chatbot (2).pdf"
    text = extract_text_from_pdf(pdf_path)
    analyze_capabilities(text)

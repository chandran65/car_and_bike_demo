import argparse
import json
from pathlib import Path


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def consolidate_faqs(data_dir):
    """Consolidate all FAQs from different sources"""
    consolidated_faqs = []
    
    # 1. Process shriramgi_faqs.json
    print("Processing shriramgi_faqs.json...")
    shriramgi_path = data_dir / 'shriramgi_faqs.json'
    if shriramgi_path.exists():
        shriramgi = load_json(shriramgi_path)
        for category, faqs in shriramgi.items():
            for faq in faqs:
                consolidated_faqs.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": "Motor Insurance",
                    "subcategory": category
                })
    
    # 2. Process rto_faqs.json
    print("Processing rto_faqs.json...")
    rto_path = data_dir / 'rto_faqs.json'
    if rto_path.exists():
        rto_faqs = load_json(rto_path)
        
        # Categorize RTO FAQs based on keywords
        for faq in rto_faqs:
            question = faq["question"].lower()
            
            if any(word in question for word in ["tax", "payment", "fee"]):
                subcategory = "Tax and Fees"
            elif any(word in question for word in ["license", "learner", "driving", "dl"]):
                subcategory = "Driving License"
            elif any(word in question for word in ["permit", "noc"]):
                subcategory = "Permits and NOC"
            elif any(word in question for word in ["registration", "rc", "duplicate rc"]):
                subcategory = "Vehicle Registration"
            elif any(word in question for word in ["appointment", "slot", "booking"]):
                subcategory = "Appointments"
            elif any(word in question for word in ["document", "upload", "photo", "signature"]):
                subcategory = "Documents"
            elif any(word in question for word in ["hypothecation", "loan"]):
                subcategory = "Hypothecation"
            elif any(word in question for word in ["transfer", "ownership"]):
                subcategory = "Ownership Transfer"
            else:
                subcategory = "General Services"
            
            consolidated_faqs.append({
                "question": faq["question"],
                "answer": faq["answer"],
                "category": "RTO Services",
                "subcategory": subcategory
            })
    
    # 3. Process rc_transfer_qa.json
    print("Processing rc_transfer_qa.json...")
    rc_path = data_dir / 'rc_transfer_qa.json'
    if rc_path.exists():
        rc_transfer = load_json(rc_path)
        for faq in rc_transfer:
            consolidated_faqs.append({
                "question": faq["question"],
                "answer": faq["answer"],
                "category": "Vehicle Registration",
                "subcategory": "RC Transfer"
            })
    
    # 4. Process policybazaar_faqs.json
    print("Processing policybazaar_faqs.json...")
    policybazaar_path = data_dir / 'policybazaar_faqs.json'
    if policybazaar_path.exists():
        policybazaar = load_json(policybazaar_path)
        
        category_mapping = {
            "Car Insurance Faqs": "General",
            "Third-Party Car Insurance Faqs": "Third-Party Insurance",
            "Comprehensive Car Insurance Faqs": "Comprehensive Insurance",
            "Add-on Covers in Car Insurance Faqs": "Add-on Covers",
            "Raising a Car Insurance Claim Faqs": "Claims",
            "Car Insurance Renewal Faqs": "Renewal"
        }
        
        for main_category, faqs in policybazaar.items():
            subcategory = category_mapping.get(main_category, main_category)
            for faq in faqs:
                consolidated_faqs.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": "Car Insurance",
                    "subcategory": subcategory
                })
    
    # 5. Process paisabazaar_car_loan_faqs.json
    print("Processing paisabazaar_car_loan_faqs.json...")
    paisabazaar_path = data_dir / 'paisabazaar_car_loan_faqs.json'
    if paisabazaar_path.exists():
        paisabazaar = load_json(paisabazaar_path)
        
        for faq in paisabazaar:
            question = faq["question"].lower()
            
            if any(word in question for word in ["what is", "benefits", "difference"]):
                subcategory = "General"
            elif any(word in question for word in ["eligibility", "salary", "guarantor", "reject"]):
                subcategory = "Eligibility"
            elif any(word in question for word in ["document", "submit"]):
                subcategory = "Documents"
            elif any(word in question for word in ["interest", "rate", "mclr", "fixed", "floating"]):
                subcategory = "Interest Rates"
            elif any(word in question for word in ["emi", "payment", "pay", "prepay"]):
                subcategory = "EMI and Payment"
            elif any(word in question for word in ["tenure", "loan amount", "maximum"]):
                subcategory = "Loan Terms"
            elif any(word in question for word in ["insurance", "registration", "financing"]):
                subcategory = "Additional Costs"
            elif any(word in question for word in ["tax", "benefit"]):
                subcategory = "Tax Benefits"
            elif any(word in question for word in ["zero percent", "zero financing"]):
                subcategory = "Special Offers"
            elif any(word in question for word in ["used car", "pre-owned", "pre-used"]):
                subcategory = "Used Car Loans"
            else:
                subcategory = "General"
            
            consolidated_faqs.append({
                "question": faq["question"],
                "answer": faq["answer"],
                "category": "Car Loans",
                "subcategory": subcategory
            })
    
    # 6. Process icici_faqs.json
    print("Processing icici_faqs.json...")
    icici_path = data_dir / 'icici_faqs.json'
    if icici_path.exists():
        icici = load_json(icici_path)
        
        for main_category, faqs in icici.items():
            for faq in faqs:
                question = faq["question"].lower()
                
                if any(word in question for word in ["claim", "cashless", "reimbursement", "settlement"]):
                    subcategory = "Claims Process"
                elif any(word in question for word in ["endorsement", "change", "transfer", "add"]):
                    subcategory = "Policy Modifications"
                elif any(word in question for word in ["road side", "rsa", "assistance"]):
                    subcategory = "Road Side Assistance"
                elif any(word in question for word in ["premium", "idv", "deductible", "discount", "ncb"]):
                    subcategory = "Premium and Pricing"
                elif any(word in question for word in ["cover", "covered", "loss", "event", "exclusion"]):
                    subcategory = "Coverage"
                elif any(word in question for word in ["renew", "renewal"]):
                    subcategory = "Renewal"
                elif any(word in question for word in ["document", "required"]):
                    subcategory = "Documents"
                elif any(word in question for word in ["garage", "cash"]):
                    subcategory = "Garage Cash"
                else:
                    subcategory = "General"
                
                consolidated_faqs.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": "Car Insurance",
                    "subcategory": subcategory
                })
    
    return consolidated_faqs


def main():
    parser = argparse.ArgumentParser(description='Consolidate all FAQs from different sources')
    parser.add_argument(
        '-d', '--data-dir',
        type=str,
        default='data',
        help='Data directory containing JSON files (default: data)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/consolidated_faqs.json',
        help='Output file path (default: data/consolidated_faqs.json)'
    )
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    
    # Consolidate FAQs
    consolidated_faqs = consolidate_faqs(data_dir)
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save consolidated FAQs
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated_faqs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Consolidation complete!")
    print(f"Total FAQs: {len(consolidated_faqs)}")
    print(f"Output file: {output_path}")
    
    # Print category summary
    print("\n📊 Category Summary:")
    category_counts = {}
    for faq in consolidated_faqs:
        cat = faq["category"]
        subcat = faq["subcategory"]
        key = f"{cat} > {subcat}"
        category_counts[key] = category_counts.get(key, 0) + 1
    
    for key, count in sorted(category_counts.items()):
        print(f"  {key}: {count}")


if __name__ == "__main__":
    main()

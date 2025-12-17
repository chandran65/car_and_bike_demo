# Consolidated FAQ Database

A comprehensive FAQ database consolidating questions and answers from multiple sources related to vehicle insurance, RTO services, car loans, and vehicle registration.

## Overview

- **Total FAQs**: 366
- **Main Categories**: 5
- **Source Files**: 6
- **Format**: JSON

## Data Structure

Each FAQ entry contains:
```json
{
  "question": "The FAQ question text",
  "answer": "Detailed answer text",
  "category": "Main category name",
  "subcategory": "Specific subcategory"
}
```

## Source Files

The consolidated FAQ database was created from the following sources:

1. **shriramgi_faqs.json** - Motor insurance FAQs from Shriram General Insurance
2. **rto_faqs.json** - Government RTO (Regional Transport Office) services FAQs
3. **rc_transfer_qa.json** - Vehicle RC (Registration Certificate) transfer FAQs
4. **policybazaar_faqs.json** - Car insurance FAQs from PolicyBazaar
5. **paisabazaar_car_loan_faqs.json** - Car loan FAQs from PaisaBazaar
6. **icici_faqs.json** - Car insurance FAQs from ICICI Lombard

---

## Categories & Subcategories

### 1. Car Insurance (83 FAQs)

Comprehensive information about car insurance policies, coverage, claims, and related services.

#### Subcategories:

| Subcategory | Count | Description |
|-------------|-------|-------------|
| **General** | 15 | Basic information about car insurance, mandatory requirements, premiums |
| **Coverage** | 12 | Details about what is covered, events, losses, and exclusions |
| **Claims Process** | 11 | How to file claims, cashless vs reimbursement, settlement procedures |
| **Premium and Pricing** | 7 | IDV, deductibles, discounts, NCB (No Claim Bonus) |
| **Road Side Assistance** | 7 | RSA services, availability, coverage, and exclusions |
| **Comprehensive Insurance** | 5 | Detailed information about comprehensive car insurance policies |
| **Policy Modifications** | 5 | Endorsements, changes, transfers, additions to existing policies |
| **Renewal** | 5 | Policy renewal process, online renewal, eligibility |
| **Third-Party Insurance** | 5 | Third-party liability coverage, rates, duration, transfer |
| **Add-on Covers** | 4 | Zero depreciation, NCB protection, engine cover, and other add-ons |
| **Documents** | 3 | Required documents for insurance and claims |
| **Claims** | 3 | General claim-related queries |
| **Garage Cash** | 1 | Garage cash cover benefits and duration |

**Key Topics:**
- Types of insurance (Third-party vs Comprehensive)
- Premium calculation factors
- Claim settlement procedures
- Add-on covers (Zero depreciation, Road Side Assistance)
- Policy renewal and modifications
- No Claim Bonus (NCB)

---

### 2. RTO Services (222 FAQs)

Government Regional Transport Office services including driving licenses, vehicle registration, permits, and taxes.

#### Subcategories:

| Subcategory | Count | Description |
|-------------|-------|-------------|
| **Driving License** | 95 | Learner's license, permanent license, renewal, duplicate, AEDL, IDP |
| **General Services** | 54 | General RTO procedures, online services, application status |
| **Tax and Fees** | 38 | Motor vehicle tax, payment procedures, refunds, fee receipts |
| **Documents** | 12 | Document upload, requirements, photo/signature submission |
| **Appointments** | 11 | Slot booking, rescheduling, cancellation for tests and services |
| **Vehicle Registration** | 6 | RC issuance, duplicate RC, change of address, surrender |
| **Hypothecation** | 3 | Addition, termination, continuation of vehicle hypothecation |
| **Permits and NOC** | 2 | Permit renewal, NOC for interstate transfer |
| **Ownership Transfer** | 1 | Transfer of vehicle ownership process |

**Key Topics:**
- Learner's License application and test
- Driving License (new, renewal, duplicate, AEDL)
- Motor vehicle tax payment
- Online appointment booking
- Document upload and verification
- Vehicle registration services
- Hypothecation management
- Interstate vehicle transfer (NOC)

---

### 3. Vehicle Registration (22 FAQs)

Specific information about vehicle registration certificate (RC) transfer and ownership changes.

#### Subcategories:

| Subcategory | Count | Description |
|-------------|-------|-------------|
| **RC Transfer** | 22 | Complete RC transfer process, documents, fees, timelines |

**Key Topics:**
- What is RC Transfer
- When RC transfer is mandatory
- Step-by-step RC transfer process (online and offline)
- Required documents for buyers and sellers
- RC transfer fees by vehicle type
- Timeline for RC transfer
- Interstate RC transfer
- Consequences of skipping RC transfer
- NOC requirements

---

### 4. Car Loans (26 FAQs)

Information about car loans, eligibility, interest rates, EMI, and repayment.

#### Subcategories:

| Subcategory | Count | Description |
|-------------|-------|-------------|
| **General** | 11 | Basic car loan information, benefits, lenders, zero percent financing |
| **EMI and Payment** | 5 | EMI calculation, payment methods, prepayment, defaults |
| **Additional Costs** | 3 | Insurance, registration, and other costs not covered by loan |
| **Eligibility** | 3 | Eligibility criteria, salary requirements, rejections |
| **Interest Rates** | 2 | Fixed vs floating rates, MCLR, negotiation |
| **Documents** | 1 | Required documents for loan application |
| **Used Car Loans** | 1 | Loans for pre-owned vehicles |

**Key Topics:**
- Car loan basics and benefits
- Loan eligibility criteria
- Interest rates (fixed vs floating, MCLR)
- EMI payment and prepayment
- Documents required
- Loan tenure and amount
- Used car financing
- Zero percent financing options
- Tax benefits (or lack thereof)

---

### 5. Motor Insurance (13 FAQs)

General motor insurance information covering both cars and two-wheelers.

#### Subcategories:

| Subcategory | Count | Description |
|-------------|-------|-------------|
| **General** | 5 | Basic motor insurance information, validity, online purchase |
| **Claim** | 2 | Claim process and settlement timelines |
| **Cover** | 2 | Third-party vs comprehensive, zero depreciation |
| **Policy** | 2 | Policy duplication, lost policy |
| **Premium** | 2 | Premium calculation, payment issues |

**Key Topics:**
- Motor insurance basics
- Policy validity and renewal
- Third-party vs comprehensive coverage
- Zero depreciation cover
- Claim settlement
- Premium calculation

---

## Usage

### Loading the Data

**Python:**
```python
import json

with open('consolidated_faqs.json', 'r', encoding='utf-8') as f:
    faqs = json.load(f)

# Get all FAQs from a specific category
car_insurance_faqs = [faq for faq in faqs if faq['category'] == 'Car Insurance']

# Get FAQs from a specific subcategory
claims_faqs = [faq for faq in faqs if faq['category'] == 'Car Insurance' and faq['subcategory'] == 'Claims Process']
```

**JavaScript:**
```javascript
const faqs = require('./consolidated_faqs.json');

// Get all FAQs from a specific category
const carInsuranceFaqs = faqs.filter(faq => faq.category === 'Car Insurance');

// Get FAQs from a specific subcategory
const claimsFaqs = faqs.filter(faq => 
  faq.category === 'Car Insurance' && faq.subcategory === 'Claims Process'
);
```

### Search Example

```python
def search_faqs(query, faqs):
    """Search FAQs by keyword in question or answer"""
    query_lower = query.lower()
    results = []
    for faq in faqs:
        if query_lower in faq['question'].lower() or query_lower in faq['answer'].lower():
            results.append(faq)
    return results

# Example usage
results = search_faqs("zero depreciation", faqs)
```

---

## Category Distribution

```
Car Insurance:         83 FAQs (22.7%)
RTO Services:         222 FAQs (60.7%)
Vehicle Registration:  22 FAQs (6.0%)
Car Loans:             26 FAQs (7.1%)
Motor Insurance:       13 FAQs (3.6%)
```

## Use Cases

This consolidated FAQ database can be used for:

1. **Customer Support Chatbots** - Train AI models for automated customer support
2. **Knowledge Base Systems** - Power searchable FAQ sections on websites
3. **Mobile Applications** - Provide offline FAQ access in mobile apps
4. **Content Management** - Organize and display FAQs by category
5. **Search Engines** - Enable semantic search across insurance and vehicle topics
6. **Training Data** - Use for training NLP models for automotive/insurance domain

---

## Updates and Maintenance

To update the consolidated FAQ database:

1. Update individual source JSON files
2. Run the consolidation script:
   ```bash
   conda run -n scrape python consolidate_faqs.py
   ```
3. The `consolidated_faqs.json` file will be regenerated with updated content

---

## File Information

- **File Name**: `consolidated_faqs.json`
- **Format**: JSON Array
- **Encoding**: UTF-8
- **Total Size**: ~2,200 lines
- **Last Updated**: December 2025

---

## License & Attribution

Data sourced from:
- Shriram General Insurance
- ICICI Lombard General Insurance
- PolicyBazaar.com
- PaisaBazaar.com
- Government of India - Parivahan Portal

---

## Contact & Support

For questions or issues regarding this FAQ database, please refer to the original source websites or contact the respective service providers.


# Web Scraping Scripts

A collection of Python scripts for extracting data from various websites including insurance FAQs, RTO information, and car details.

## 🚀 Quick Start

All scripts run in the `scrape` conda environment:

```bash
conda run -n scrape python scripts/<script_name>.py [OPTIONS]
```

## 📋 Available Scripts

### 🚗 CarAndBike Data Extractor

**Script:** `extract_carandbike_new_car_data.py`

Extract comprehensive car data from CarAndBike HTML files.

**Features:**
- ✅ Extracts car list (262 cars, 1,944 variants)
- ✅ Downloads and extracts detailed car information
- ✅ Resumable - automatically skips already extracted cars
- ✅ Progress bar with tqdm
- ✅ Fast - no delay by default
- ✅ Temp files in `.temp/carandbike_new_cars/` (git-ignored)

**Usage:**
```bash
# Using Makefile (recommended)
make extract-carandbike-cars       # Extract all 262 cars
make extract-carandbike-cars-test  # Test with 5 cars

# Or using Python directly
conda run -n scrape python scripts/extract_carandbike_new_car_data.py

# Test with 10 cars
conda run -n scrape python scripts/extract_carandbike_new_car_data.py --limit 10

# Add delay between requests
conda run -n scrape python scripts/extract_carandbike_new_car_data.py --delay 1.0

# Resume interrupted extraction
conda run -n scrape python scripts/extract_carandbike_new_car_data.py
```

**Options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--input` | `experiment-notebooks/html_files/carandbike.com_new-cars_models_6.html` | Input HTML file |
| `--output-dir` | `data` | Output directory |
| `--delay` | `0.0` | Delay between downloads (seconds) |
| `--limit` | `None` | Limit number of cars (for testing) |
| `--skip-download` | `False` | Skip downloading, only extract from existing HTML |

**Output:**
```
data/
├── new_cars_list.csv              # Car list (262 cars)
├── new_cars_list.json             # Car list in JSON
└── new_car_details/               # Detailed info (262 JSON files)
    ├── New_Hyundai_Venue.json
    ├── Mahindra_Bolero_2025.json
    └── ...

.temp/
└── carandbike_new_cars/           # Temp HTML files (git-ignored)
    └── ...
```

**Data Extracted:**
- Basic info (name, manufacturer, model, body type)
- Engine specs (displacement, power, torque)
- Transmission, fuel, dimensions
- Colors, price, brand info
- Ratings, reviews, pros/cons
- Mileage details (city/highway)
- Expert reviews, verdict
- Competitor comparison

---

### 🏦 Insurance FAQ Extractors

#### ICICI Bank FAQs
**Script:** `extract_icici_faqs.py`

```bash
conda run -n scrape python scripts/extract_icici_faqs.py
```

**Output:** `data/icici_faqs.json`

#### Policybazaar FAQs
**Script:** `extract_policybazaar_faqs.py`

```bash
conda run -n scrape python scripts/extract_policybazaar_faqs.py
```

**Output:** `data/policybazaar_faqs.json`

#### Paisabazaar Car Loan FAQs
**Script:** `extract_paisabazaar_faqs.py`

```bash
conda run -n scrape python scripts/extract_paisabazaar_faqs.py
```

**Output:** `data/paisabazaar_car_loan_faqs.json`

#### Shriram GI FAQs
**Script:** `extract_shriramgi_faqs.py`

```bash
conda run -n scrape python scripts/extract_shriramgi_faqs.py
```

**Output:** `data/shriramgi_faqs.json`

---

### 🚓 RTO Information Extractors

#### RTO FAQs
**Script:** `extract_rto_faq.py`

```bash
conda run -n scrape python scripts/extract_rto_faq.py
```

**Output:** `data/rto_faqs.json`

#### RC Transfer Q&A
**Script:** `extract_rc_transfer_qa.py`

```bash
conda run -n scrape python scripts/extract_rc_transfer_qa.py
```

**Output:** `data/rc_transfer_qa.json`

#### Permit Details
**Script:** `extract_permit_details.py`

```bash
conda run -n scrape python scripts/extract_permit_details.py
```

**Output:** `data/permit_details.json`

#### Fees & Charges
**Script:** `extract_fees_charges.py`

```bash
conda run -n scrape python scripts/extract_fees_charges.py
```

**Output:** `data/fees_charges.json`

---

### 📊 Consolidate FAQs
**Script:** `consolidate_faqs.py`

Consolidates all FAQ files into a single JSON file.

```bash
conda run -n scrape python scripts/consolidate_faqs.py
```

**Output:** `data/consolidated_faqs.json`

---

## 🌐 Streamlit Web Application

**NEW:** Interactive web interface for Mahindra Bot!

A rich, production-ready Streamlit application that provides an intuitive chat interface for interacting with the Mahindra Bot. Features include:

- 💬 **Chat Interface** - Real-time streaming responses
- 🎯 **Intent Detection** - Visual intent classification with confidence levels
- 🔧 **Tool Visualization** - Expandable sections showing tool executions
- 📜 **Conversation History** - Full chat history with context retention
- 🔄 **Session Management** - Reset functionality and state management

### Quick Start

```bash
# From project root
conda run -n scrape streamlit run streamlit_apps/mahindra_bot_app.py

# Or use the quick start script
./streamlit_apps/start_app.sh

# Access at http://localhost:8501
```

### Features

The app supports all 4 Mahindra Bot intents:
- 🤔 **General Q&A** - Insurance and documentation questions
- 🚗 **Car Recommendation** - Finding cars by budget/preferences
- ⚖️ **Car Comparison** - Comparing multiple cars
- 📅 **Book Test Drive** - Schedule test drive appointments

### Documentation

- 📖 [Streamlit App Guide](streamlit_apps/README.md) - Complete usage guide and setup
- 🧪 [Test Results](streamlit_apps/test_app.py) - Component verification

---

## 🔍 FAQ Search Service

**NEW:** Semantic search service for FAQs using OpenAI embeddings!

### Features
- ✅ Semantic search (understands intent, not just keywords)
- ✅ Dual embedding strategy (searches questions + answers)
- ✅ Intelligent caching (~$0.003 one-time cost for 329 FAQs)
- ✅ Fast search (<200ms per query)
- ✅ 18 comprehensive tests (100% passing)
- ✅ Production-ready with full documentation

### Quick Start

```python
from src.mahindrabot.services.faq_service import FAQService

# Initialize (loads from cache after first run)
service = FAQService()

# Search
results = service.search("How to transfer vehicle ownership?", limit=5)

# Display results
for result in results:
    print(f"{result.question} (score: {result.score:.4f})")
```

### Run Tests

```bash
conda run -n scrape pytest tests/test_faq_service.py -v
```

**Result:** ✅ 18/18 tests passed

### Run Demos

```bash
# Interactive demo
conda run -n scrape python demo_faq.py

# Automated demo (non-interactive)
conda run -n scrape python demo_faq_auto.py
```

### Performance
- **First run:** 3-6 minutes (generates embeddings)
- **Subsequent runs:** ~2 seconds (loads from cache)
- **Search speed:** 100-200ms per query
- **Accuracy:** >85% relevance for related queries

### Documentation
- 📖 [FAQ Service Guide](docs/services/faq-service.md) - Complete usage guide
- 📊 [Demo Results](docs/implementation/faq-service-demo-results.md) - Test results and examples
- 🏗️ [Implementation Details](docs/implementation/faq-service-implementation.md) - Technical details

### Example Results

Query: "How to transfer ownership?"
- **Top Result**: 0.9350 (93.5% relevance)
- **Question**: "If I want to transfer the ownership of my vehicle, what should I do?"

Query: "Lost registration certificate"
- **Top Result**: 0.9479 (94.8% relevance)
- **Question**: "I have lost my registration certificate. How do I apply for a duplicate registration certificate?"

## 📁 Project Structure

```
.
├── src/mahindrabot/               # Main package
│   ├── core/                      # Bot core system
│   ├── models/                    # Data models
│   └── services/                  # Services (Car, FAQ, LLM, etc.)
├── scripts/                       # Extraction scripts
│   ├── extract_carandbike_new_car_data.py
│   ├── extract_icici_faqs.py
│   ├── extract_policybazaar_faqs.py
│   ├── extract_paisabazaar_faqs.py
│   ├── extract_shriramgi_faqs.py
│   ├── extract_rto_faq.py
│   ├── extract_rc_transfer_qa.py
│   ├── extract_permit_details.py
│   ├── extract_fees_charges.py
│   └── consolidate_faqs.py
├── demos/                         # Demo scripts
│   ├── demo.py                    # Car service demo
│   ├── demo_faq.py                # FAQ service demo
│   ├── demo_mahindra_bot.py       # Complete bot demo
│   └── README.md
├── streamlit_apps/                # Streamlit web applications
│   ├── mahindra_bot_app.py        # Main Streamlit app
│   ├── test_app.py                # App component tests
│   ├── start_app.sh               # Quick start script
│   └── README.md                  # App documentation
├── docs/                          # 📚 Documentation
│   ├── services/                  # Service docs
│   ├── guides/                    # Quick start guides
│   ├── data/                      # Data documentation
│   ├── updates/                   # Change logs
│   ├── planning/                  # Architecture docs
│   ├── implementation/            # Implementation summaries
│   └── README.md                  # Documentation index
├── tests/                         # Test suites
├── data/                          # Output data (git-ignored)
│   ├── new_cars_list.csv
│   ├── new_cars_list.json
│   ├── new_car_details/           # 262 car detail JSON files
│   ├── icici_faqs.json
│   ├── policybazaar_faqs.json
│   ├── paisabazaar_car_loan_faqs.json
│   ├── shriramgi_faqs.json
│   ├── rto_faqs.json
│   ├── rc_transfer_qa.json
│   ├── permit_details.json
│   ├── fees_charges.json
│   └── consolidated_faqs.json
├── .temp/                         # Temporary files (git-ignored)
│   └── carandbike_new_cars/       # Temp HTML files for car scraping
├── experiment-notebooks/          # Jupyter notebooks (git-ignored)
├── .env                           # Environment variables
├── .gitignore
├── pyproject.toml                 # Project dependencies
├── uv.lock
├── Makefile
└── README.md                      # This file
```

## 🛠️ Setup

### Prerequisites
- Python 3.12
- Conda/Mamba
- Make (optional, for using Makefile commands)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scrape
   ```

2. **Create conda environment**
   ```bash
   conda env create -n scrape python=3.12
   conda activate scrape
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or if using uv
   uv sync
   ```

4. **Verify setup**
   ```bash
   make help
   ```

### Dependencies
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `pandas` - Data manipulation
- `tqdm` - Progress bars
- `lxml` - XML/HTML parser

## 📋 Makefile Commands

For convenience, you can use Make commands instead of running Python scripts directly:

```bash
# Show all available commands
make help

# Car data extraction
make extract-carandbike-cars       # Extract all 262 cars (~5-10 min)
make extract-carandbike-cars-test  # Test with 5 cars

# FAQ extraction
make extract-all                   # Extract all FAQs
make extract-policybazaar          # Individual FAQ extractors
make extract-icici
make extract-paisabazaar
make extract-rc-transfer
make extract-shriramgi
make extract-fees
make extract-permit
make extract-rto

# Consolidate data
make consolidate                   # Consolidate all FAQs

# Cleanup
make clean                         # Remove data files
make clean-temp                    # Remove temp files
make clean-all                     # Remove all generated files

# Run everything
make all                           # Extract all data and consolidate
```

## 🎯 Common Use Cases

### Extract All Car Data
```bash
# Using Makefile (recommended)
make extract-carandbike-cars

# Or using Python directly
conda run -n scrape python scripts/extract_carandbike_new_car_data.py

# View results
cat data/new_cars_list.csv
```

### Extract All Insurance FAQs
```bash
# Run all FAQ extractors
for script in extract_icici_faqs extract_policybazaar_faqs extract_paisabazaar_faqs extract_shriramgi_faqs; do
    conda run -n scrape python scripts/${script}.py
done

# Consolidate into one file
conda run -n scrape python scripts/consolidate_faqs.py
```

### Extract All RTO Information
```bash
# Run all RTO extractors
for script in extract_rto_faq extract_rc_transfer_qa extract_permit_details extract_fees_charges; do
    conda run -n scrape python scripts/${script}.py
done
```

## 💡 Tips & Tricks

### CarAndBike Extractor

**Test before full run:**
```bash
conda run -n scrape python scripts/extract_carandbike_new_car_data.py --limit 5
```

**Resume interrupted extraction:**
- Simply run the same command again
- Script automatically skips already extracted cars

**Add rate limiting:**
```bash
conda run -n scrape python scripts/extract_carandbike_new_car_data.py --delay 1.0
```

**Re-extract specific car:**
```bash
rm data/new_car_details/New_Hyundai_Venue.json
conda run -n scrape python scripts/extract_carandbike_new_car_data.py
```

**Clean temp files:**
```bash
rm -rf .temp/carandbike_new_cars
```

### General Tips

**Check output data:**
```bash
# List all output files
ls -lh data/

# View JSON file
cat data/new_cars_list.json | python -m json.tool | head -50

# View CSV in pandas
conda run -n scrape python -c "import pandas as pd; print(pd.read_csv('data/new_cars_list.csv'))"
```

**Monitor progress:**
- All scripts with tqdm show real-time progress bars
- Long-running scripts can be interrupted with Ctrl+C and resumed

## 🔧 Troubleshooting

### Network Errors
If you encounter network errors:
```bash
# Add delay between requests
conda run -n scrape python scripts/extract_carandbike_new_car_data.py --delay 2.0
```

### Missing Dependencies
```bash
conda activate scrape
pip install beautifulsoup4 requests pandas tqdm lxml
```

### Disk Space Issues
The `.temp/` folder can grow large. Clean it periodically:
```bash
# Check size
du -sh .temp/

# Clean CarAndBike temp files
rm -rf .temp/carandbike_new_cars/
```

### Script Fails
1. Check if running in correct environment: `conda activate scrape`
2. Check if input files exist
3. Check network connectivity
4. Review error messages in console output

## 📊 Data Quality

### CarAndBike Data
- ✅ 262 cars extracted
- ✅ 1,944 total variants
- ✅ 17+ data categories per car
- ✅ Comprehensive details including specs, reviews, comparisons

### FAQ Data
- ✅ Multiple sources consolidated
- ✅ Structured Q&A format
- ✅ Categorized by source

### RTO Data
- ✅ Comprehensive fee structures
- ✅ Transfer procedures
- ✅ Permit requirements

## 🚀 Performance

### CarAndBike Extractor
- **Car list extraction:** <1 second
- **Per car download:** ~1-2 seconds
- **Per car extraction:** <0.5 seconds
- **Total time (262 cars):** ~5-10 minutes
- **Resumable:** Yes, instant skip for existing cars

### FAQ Extractors
- **Per script:** ~5-30 seconds
- **Network dependent:** Yes
- **Retry logic:** Built-in

## 🔐 Environment Variables

Create a `.env` file for sensitive data:
```bash
# API keys (if needed)
API_KEY=your_api_key_here

# User agent (optional)
USER_AGENT=Mozilla/5.0...
```

## 📝 Notes

- All data files are git-ignored by default
- Temp files are automatically organized by script/task
- Scripts are resumable and handle errors gracefully
- Progress bars show real-time status
- All scripts use BeautifulSoup for reliable HTML parsing

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Services](docs/services/)** - Car Service, FAQ Service, Bot Core
- **[Guides](docs/guides/)** - Quick start guides and tutorials
- **[Data](docs/data/)** - Data structure documentation
- **[Updates](docs/updates/)** - Feature updates and changes
- **[Planning](docs/planning/)** - Architecture and design docs
- **[Implementation](docs/implementation/)** - Technical summaries

See [docs/README.md](docs/README.md) for the complete documentation index.

## 🤝 Contributing

When adding new scripts:
1. Follow the existing naming pattern: `extract_<source>_<type>.py`
2. Use `.temp/<script_name>/` for temporary files
3. Save output to `data/` directory
4. Include progress bars with tqdm
5. Make scripts resumable where possible
6. Update this README and relevant documentation

## 📄 License

[Your License Here]

## 📧 Contact

[Your Contact Information]

---

**Last Updated:** 2024-12-14  
**Python Version:** 3.12  
**Environment:** scrape

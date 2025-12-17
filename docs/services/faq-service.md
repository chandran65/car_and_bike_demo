# FAQ Search Service

A semantic search service for FAQs using OpenAI embeddings with intelligent caching to minimize API costs.

## Features

- **Semantic Search**: Find relevant FAQs based on meaning, not just keywords
- **Dual Embedding Strategy**: Searches both questions and answers for better recall
- **Smart Caching**: Embeddings are cached to `.temp/` directory to avoid regeneration costs
- **Batch Processing**: Efficient API usage with batched embedding generation
- **Score Merging**: When both Q&A match, keeps the highest relevance score

## Architecture

```
FAQService Initialization Flow:
1. Load consolidated_faqs.json
2. Check if cache exists (.temp/faq_embeddings.json)
3. If cache valid → Load embeddings from cache
4. If no cache → Generate embeddings & save to cache
5. Store embeddings in memory as numpy arrays

Search Flow:
1. Generate embedding for user query
2. Calculate cosine similarity with all question embeddings
3. Calculate cosine similarity with all answer embeddings
4. Merge results by FAQ ID (keep best score)
5. Sort by score and return top results
```

## Installation

All required dependencies are already in `pyproject.toml`:

```bash
# Install dependencies
uv sync
```

Required packages:
- `openai` - For embeddings API
- `numpy` - For vector operations
- `pydantic` - For data models
- `python-dotenv` - For API key management

## Setup

1. **Set OpenAI API Key**

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

2. **Prepare FAQ Data**

Ensure `data/consolidated_faqs.json` exists with this structure:

```json
[
  {
    "question": "Question text",
    "answer": "Answer text",
    "category": "Category name",
    "subcategory": "Subcategory name"
  }
]
```

## Usage

### Basic Usage

```python
from src.mahindrabot.services.faq_service import FAQService

# Initialize the service (loads or generates embeddings)
service = FAQService()

# Search for relevant FAQs
results = service.search("How do I transfer vehicle ownership?", limit=5)

# Process results
for result in results:
    print(f"Q: {result.question}")
    print(f"A: {result.answer}")
    print(f"Score: {result.score:.4f}")
    print(f"Category: {result.category} > {result.subcategory}")
    print()
```

### Custom Paths

```python
# Use custom FAQ file and cache directory
service = FAQService(
    faq_path="path/to/faqs.json",
    cache_dir="path/to/cache"
)
```

### Run Demo Script

```bash
python demo_faq_search.py
```

The demo includes:
- Pre-defined example queries
- Interactive mode for testing your own queries

## Data Models

### QNAResult

The search results are returned as `QNAResult` Pydantic models:

```python
class QNAResult(BaseModel):
    id: str              # Unique FAQ identifier
    question: str        # Question text
    answer: str          # Answer text
    score: float         # Relevance score (0-1, higher is better)
    category: str        # FAQ category
    subcategory: str     # FAQ subcategory
```

## Caching

### Cache Location

- Default: `.temp/faq_embeddings.json` in project root
- Already added to `.gitignore` to avoid committing large files

### Cache Structure

```json
{
  "questions": [[0.001, 0.002, ...], ...],  // Question embeddings
  "answers": [[0.003, 0.004, ...], ...],    // Answer embeddings
  "metadata": [                              // FAQ metadata
    {
      "id": "0",
      "question": "...",
      "answer": "...",
      "category": "...",
      "subcategory": "..."
    }
  ]
}
```

### Cache Validation

The service validates cache on startup:
- Checks for required keys (`questions`, `answers`, `metadata`)
- Verifies lengths match across all arrays
- Confirms FAQ count matches current data

If validation fails, embeddings are regenerated.

### Regenerating Cache

To force regeneration, simply delete the cache file:

```bash
rm .temp/faq_embeddings.json
```

Next initialization will regenerate embeddings.

## Implementation Details

### Embedding Model

- **Model**: `text-embedding-ada-002`
- **Dimension**: 1536
- **Provider**: OpenAI

### Similarity Metric

Cosine similarity is used to compare embeddings:

```python
similarity = dot(a, b) / (norm(a) * norm(b))
```

Range: -1 to 1 (higher = more similar)

### Merging Strategy

When both question and answer match for the same FAQ:

1. Calculate similarity scores for both
2. Keep the **maximum score**
3. Example:
   - Question similarity: 0.85
   - Answer similarity: 0.92
   - Final score: 0.92

This ensures the most relevant match is prioritized.

### Batch Processing

Embeddings are generated in batches of 50 to:
- Stay within API rate limits
- Provide progress feedback
- Handle large FAQ datasets efficiently

## Performance

### First Run (No Cache)

- Loads FAQ data: ~1s
- Generates embeddings: ~2-5 minutes (depends on FAQ count)
- Saves cache: ~1s

**Total**: ~3-6 minutes for ~250 FAQs

### Subsequent Runs (With Cache)

- Loads FAQ data: ~1s
- Loads embeddings from cache: ~1s

**Total**: ~2 seconds

### Search Performance

- Single query: ~100-200ms
- Includes embedding generation and similarity computation

## API Costs

### OpenAI Pricing (text-embedding-ada-002)

- **Cost**: $0.0001 per 1K tokens
- **Average**: ~1 FAQ = ~100 tokens (question + answer)
- **Example**: 250 FAQs ≈ 25K tokens ≈ **$0.0025**

With caching, this cost is incurred only once!

### Query Costs

- Each search query: ~10-50 tokens ≈ $0.000001-0.000005
- Very minimal cost per search

## Troubleshooting

### Issue: "No module named 'openai'"

**Solution**: Install dependencies

```bash
uv sync
```

### Issue: "OPENAI_API_KEY not found"

**Solution**: Create `.env` file with your API key

```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

### Issue: "Cache validation failed"

**Solution**: Delete cache and regenerate

```bash
rm .temp/faq_embeddings.json
python demo_faq_search.py
```

### Issue: Rate limit errors

**Solution**: Reduce batch size in `get_embeddings()`

```python
embeddings = get_embeddings(texts, batch_size=25)  # Reduced from 50
```

## Example Output

```
QUERY: How do I transfer vehicle ownership?
════════════════════════════════════════════════════════════════════════════════

1. [RTO Services > Ownership Transfer] (Score: 0.8942)
   Q: If I want to transfer the ownership of my vehicle, what should I do?
   A: In case the vehicle has been sold, passed on to another citizen...

2. [RTO Services > General Services] (Score: 0.7631)
   Q: How to make changes to my application after I submitted the information?
   A: a. Visit https://vahan.parivahan.gov.in/vahanservice/vahan/...

3. [RTO Services > Vehicle Registration] (Score: 0.7124)
   Q: How do I make changes to my details in Vehicle Registration Certificate?
   A: a. Visit https://vahan.parivahan.gov.in/vahanservice/vahan/...
```

## Future Enhancements

Potential improvements:
- [ ] Support for multiple embedding models
- [ ] Hybrid search (semantic + keyword)
- [ ] Relevance feedback mechanism
- [ ] Multi-language support
- [ ] Real-time cache updates
- [ ] Vector database integration (e.g., Pinecone, Weaviate)

## References

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
- Notebook: `experiment-notebooks/04-open-embeddings.ipynb`

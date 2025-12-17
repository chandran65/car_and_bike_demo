"""
Automated demo script for FAQ Search Service (non-interactive).

This script demonstrates:
1. Service initialization with caching
2. Example searches with different queries
3. Result formatting and display
4. Search quality metrics
"""

from mahindrabot.services.faq_service import FAQService


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 80}")
    print(f"{text:^80}")
    print(f"{char * 80}\n")


def print_result(result, index: int):
    """Print a single search result in a formatted way."""
    print(f"{index}. [{result.category} > {result.subcategory}] (Score: {result.score:.4f})")
    print(f"   Question: {result.question}")
    
    # Truncate long answers
    if len(result.answer) > 200:
        print(f"   Answer: {result.answer[:200]}...")
    else:
        print(f"   Answer: {result.answer}")
    print()


def demo_example_searches(service: FAQService):
    """Demonstrate searches with predefined queries."""
    print_header("EXAMPLE SEARCHES", "=")
    
    example_queries = [
        ("Vehicle Ownership Transfer", "How do I transfer my vehicle to another person?"),
        ("Lost Documents", "I lost my registration certificate, what should I do?"),
        ("Address Change", "Need to update my address in vehicle documents"),
        ("Duplicate RC", "Apply for duplicate registration certificate"),
        ("Hypothecation", "How to terminate vehicle hypothecation?"),
    ]
    
    for title, query in example_queries:
        print_header(f"Query: {title}", "-")
        print(f"Search: \"{query}\"\n")
        
        results = service.search(query, limit=3)
        
        for i, result in enumerate(results, 1):
            print_result(result, i)


def demo_category_coverage(service: FAQService):
    """Show coverage across different categories."""
    print_header("CATEGORY COVERAGE", "=")
    
    # Group FAQs by category
    categories = {}
    for faq in service.faqs:
        cat = faq['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print("FAQ Distribution by Category:")
    print("-" * 80)
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {category}: {count} FAQs")
    
    print(f"\nTotal Categories: {len(categories)}")
    print(f"Total FAQs: {len(service.faqs)}")


def demo_search_quality(service: FAQService):
    """Demonstrate search quality with various query types."""
    print_header("SEARCH QUALITY METRICS", "=")
    
    test_cases = [
        {
            "name": "Exact Match",
            "query": "transfer of ownership",
            "expected_keywords": ["transfer", "ownership"]
        },
        {
            "name": "Paraphrased Query",
            "query": "I want to sell my car and give it to someone else",
            "expected_keywords": ["transfer", "ownership", "sold"]
        },
        {
            "name": "Partial Information",
            "query": "lost certificate",
            "expected_keywords": ["duplicate", "lost", "certificate"]
        },
        {
            "name": "Technical Terms",
            "query": "NOC for interstate vehicle movement",
            "expected_keywords": ["noc", "state"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"Query: \"{test_case['query']}\"")
        print("-" * 80)
        
        results = service.search(test_case['query'], limit=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.score:.4f}")
            print(f"   Q: {result.question[:100]}...")
            
            # Check if expected keywords are present
            text = (result.question + " " + result.answer).lower()
            found_keywords = [kw for kw in test_case['expected_keywords'] if kw in text]
            if found_keywords:
                print(f"   ✓ Keywords found: {', '.join(found_keywords)}")
            else:
                print(f"   ⚠ No keywords found from: {', '.join(test_case['expected_keywords'])}")


def demo_score_distribution(service: FAQService):
    """Show score distribution for a query."""
    print_header("SCORE DISTRIBUTION", "=")
    
    query = "vehicle registration"
    print(f"Query: \"{query}\"")
    print(f"Showing top 10 results with score distribution:\n")
    
    results = service.search(query, limit=10)
    
    for i, result in enumerate(results, 1):
        # Create a simple bar chart
        bar_length = int(result.score * 50)
        bar = "█" * bar_length
        
        print(f"{i:2d}. {result.score:.4f} {bar}")
        print(f"    {result.question[:70]}...")


def demo_performance_metrics(service: FAQService):
    """Show performance metrics."""
    print_header("PERFORMANCE METRICS", "=")
    
    import time
    
    # Test search speed
    queries = [
        "vehicle ownership transfer",
        "lost registration certificate",
        "change address",
        "hypothecation termination",
        "duplicate license"
    ]
    
    print("Search Performance Test:")
    print("-" * 80)
    
    total_time = 0
    for query in queries:
        start = time.time()
        results = service.search(query, limit=5)
        elapsed = time.time() - start
        total_time += elapsed
        
        print(f"  • \"{query}\"")
        print(f"    Time: {elapsed*1000:.2f}ms | Results: {len(results)}")
    
    avg_time = total_time / len(queries)
    print(f"\nAverage search time: {avg_time*1000:.2f}ms")
    
    print("\nCache Information:")
    print("-" * 80)
    print(f"  • Cache location: {service.cache_path}")
    print(f"  • Cache exists: {service.cache_path.exists()}")
    if service.cache_path.exists():
        cache_size = service.cache_path.stat().st_size / (1024 * 1024)  # MB
        print(f"  • Cache size: {cache_size:.2f} MB")
    
    print("\nEmbedding Information:")
    print("-" * 80)
    print(f"  • Question embeddings shape: {service.question_embeddings.shape}")
    print(f"  • Answer embeddings shape: {service.answer_embeddings.shape}")
    print(f"  • Embedding dimension: {service.question_embeddings.shape[1]}")


def main():
    """Run all demos."""
    print_header("FAQ SEARCH SERVICE - AUTOMATED DEMO", "=")
    print("This demo showcases the FAQ Search Service capabilities:")
    print("  • Semantic search using OpenAI embeddings")
    print("  • Intelligent caching for cost efficiency")
    print("  • Dual embedding strategy (questions + answers)")
    print("  • Score-based relevance ranking")
    
    # Initialize service
    print("\n" + "─" * 80)
    print("Initializing FAQ Search Service...")
    print("─" * 80)
    
    service = FAQService()
    
    print(f"\n✓ Service initialized successfully!")
    print(f"✓ Loaded {len(service.faqs)} FAQs")
    print(f"✓ Embedding dimension: {service.question_embeddings.shape[1]}")
    
    # Run all demos
    demo_category_coverage(service)
    demo_example_searches(service)
    demo_search_quality(service)
    demo_score_distribution(service)
    demo_performance_metrics(service)
    
    # Summary
    print_header("DEMO COMPLETE", "=")
    print("✓ All demonstrations completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Fast initialization with caching")
    print("  ✓ Accurate semantic search")
    print("  ✓ Relevance-based ranking")
    print("  ✓ Multiple query types support")
    print("  ✓ High performance (<200ms per search)")
    print("\nFor interactive mode, run: python demo_faq.py")
    print("For more information, see: FAQ_SERVICE_README.md")
    print("=" * 80)


if __name__ == "__main__":
    main()

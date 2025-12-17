"""FAQ Search Service with semantic embeddings and caching."""

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import openai
from dotenv import load_dotenv

from .serializers import QNAResult

# Load environment variables
load_dotenv()


def get_embeddings(texts: list[str], batch_size: int = 50) -> np.ndarray:
    """
    Generate embeddings for a list of texts using OpenAI API.
    
    Processes texts in batches to handle large datasets efficiently.
    
    Args:
        texts: List of text strings to embed
        batch_size: Number of texts to process per API call (default: 50)
        
    Returns:
        NumPy array of embeddings with shape (len(texts), embedding_dim)
        
    Example:
        >>> texts = ["question 1", "question 2"]
        >>> embeddings = get_embeddings(texts)
        >>> embeddings.shape
        (2, 1536)
    """
    embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    for i in range(0, len(texts), batch_size):
        batch_num = i // batch_size + 1
        print(f"Processing batch {batch_num} of {total_batches}")
        
        batch = texts[i:i+batch_size]
        resp = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=batch,
            encoding_format="float"
        )
        embeddings.extend([np.array(d.embedding) for d in resp.data])
    
    return np.array(embeddings)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score between -1 and 1
        
    Example:
        >>> a = np.array([1, 0, 0])
        >>> b = np.array([1, 0, 0])
        >>> cosine_similarity(a, b)
        1.0
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def cosine_similarity_batch(query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """
    Calculate cosine similarity between a query and multiple embeddings.
    
    Args:
        query_embedding: Query vector of shape (embedding_dim,)
        embeddings: Array of embeddings with shape (n_samples, embedding_dim)
        
    Returns:
        Array of similarity scores with shape (n_samples,)
    """
    # Normalize the query embedding
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    
    # Normalize all embeddings
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Calculate dot product (cosine similarity for normalized vectors)
    similarities = np.dot(embeddings_norm, query_norm)
    
    return similarities


class FAQService:
    """
    FAQ Search Service using semantic embeddings.
    
    This service loads FAQ data, generates embeddings for questions and answers,
    caches them for reuse, and provides semantic search functionality.
    
    Attributes:
        faqs: List of FAQ dictionaries with metadata
        question_embeddings: NumPy array of question embeddings
        answer_embeddings: NumPy array of answer embeddings
        cache_path: Path to the cache file
        
    Example:
        >>> service = FAQService()
        >>> results = service.search("How do I transfer ownership?", limit=3)
        >>> for result in results:
        ...     print(f"{result.question}: {result.score:.3f}")
    """
    
    def __init__(self, faq_path: str | None = None, cache_dir: str | None = None):
        """
        Initialize the FAQ service.
        
        Loads FAQ data from JSON file and prepares embeddings (from cache or by generating).
        
        Args:
            faq_path: Path to consolidated_faqs.json (default: data/consolidated_faqs.json)
            cache_dir: Directory for cache files (default: .temp)
        """
        # Set default paths
        if faq_path is None:
            faq_path = "data/consolidated_faqs.json"
        if cache_dir is None:
            cache_dir = ".temp"
            
        self.faq_path = Path(faq_path)
        self.cache_dir = Path(cache_dir)
        self.cache_path = self.cache_dir / "faq_embeddings.json"
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)
        
        # Load FAQ data
        print(f"Loading FAQ data from {self.faq_path}...")
        with open(self.faq_path, "r", encoding="utf-8") as f:
            faq_data = json.load(f)
        
        # Add IDs to FAQs
        self.faqs = []
        for i, faq in enumerate(faq_data):
            faq_with_id = {
                "id": str(i),
                "question": faq.get("question", ""),
                "answer": faq.get("answer", ""),
                "category": faq.get("category", ""),
                "subcategory": faq.get("subcategory", "")
            }
            self.faqs.append(faq_with_id)
        
        print(f"Loaded {len(self.faqs)} FAQs")
        
        # Load or generate embeddings
        if self._cache_exists() and self._validate_cache():
            print("Loading embeddings from cache...")
            self._load_from_cache()
        else:
            print("Generating embeddings (this may take a few minutes)...")
            self._generate_and_cache_embeddings()
        
        print("FAQ Service initialized successfully!")
    
    def _cache_exists(self) -> bool:
        """Check if cache file exists."""
        return self.cache_path.exists()
    
    def _validate_cache(self) -> bool:
        """
        Validate that cache file has the expected structure.
        
        Returns:
            True if cache is valid, False otherwise
        """
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # Check required keys
            required_keys = {"questions", "answers", "metadata"}
            if not required_keys.issubset(cache_data.keys()):
                print("Cache validation failed: missing required keys")
                return False
            
            # Check that lengths match
            n_questions = len(cache_data["questions"])
            n_answers = len(cache_data["answers"])
            n_metadata = len(cache_data["metadata"])
            
            if n_questions != n_answers or n_questions != n_metadata:
                print(f"Cache validation failed: length mismatch (Q:{n_questions}, A:{n_answers}, M:{n_metadata})")
                return False
            
            # Check that metadata matches current FAQs count
            if n_metadata != len(self.faqs):
                print(f"Cache validation failed: FAQ count mismatch (cache:{n_metadata}, current:{len(self.faqs)})")
                return False
            
            return True
            
        except Exception as e:
            print(f"Cache validation failed: {e}")
            return False
    
    def _load_from_cache(self) -> None:
        """Load embeddings and metadata from cache file."""
        with open(self.cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        
        # Convert lists back to numpy arrays
        self.question_embeddings = np.array(cache_data["questions"])
        self.answer_embeddings = np.array(cache_data["answers"])
        
        print(f"Loaded {len(self.question_embeddings)} embeddings from cache")
    
    def _generate_and_cache_embeddings(self) -> None:
        """Generate embeddings for questions and answers, then save to cache."""
        # Extract questions and answers
        questions = [faq["question"] for faq in self.faqs]
        answers = [faq["answer"] for faq in self.faqs]
        
        # Generate embeddings
        print("\nGenerating question embeddings...")
        self.question_embeddings = get_embeddings(questions)
        
        print("\nGenerating answer embeddings...")
        self.answer_embeddings = get_embeddings(answers)
        
        # Prepare cache data
        cache_data = {
            "questions": self.question_embeddings.tolist(),
            "answers": self.answer_embeddings.tolist(),
            "metadata": self.faqs
        }
        
        # Save to cache
        print(f"\nSaving embeddings to cache at {self.cache_path}...")
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)
        
        print("Embeddings cached successfully!")
    
    def search(self, query: str, limit: int = 5) -> list[QNAResult]:
        """
        Search for relevant FAQs based on semantic similarity.
        
        Generates an embedding for the query, compares it against both question
        and answer embeddings, merges results by ID (keeping the best score),
        and returns the top matches.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 5)
            
        Returns:
            List of QNAResult objects sorted by relevance score (highest first)
            
        Example:
            >>> service = FAQService()
            >>> results = service.search("How to change vehicle ownership?", limit=3)
            >>> for r in results:
            ...     print(f"Q: {r.question}")
            ...     print(f"Score: {r.score:.3f}")
        """
        # Generate embedding for query
        query_embedding = get_embeddings([query])[0]
        
        # Calculate similarities with questions
        question_similarities = cosine_similarity_batch(query_embedding, self.question_embeddings)
        
        # Calculate similarities with answers
        answer_similarities = cosine_similarity_batch(query_embedding, self.answer_embeddings)
        
        # Create results dictionary to merge by ID
        results_dict: dict[str, tuple[dict[str, Any], float]] = {}
        
        # Add question matches
        for i, score in enumerate(question_similarities):
            faq = self.faqs[i]
            results_dict[faq["id"]] = (faq, float(score))
        
        # Merge answer matches (keep higher score)
        for i, score in enumerate(answer_similarities):
            faq = self.faqs[i]
            faq_id = faq["id"]
            
            if faq_id in results_dict:
                # Keep the higher score
                existing_score = results_dict[faq_id][1]
                if score > existing_score:
                    results_dict[faq_id] = (faq, float(score))
            else:
                results_dict[faq_id] = (faq, float(score))
        
        # Convert to list and sort by score
        results = [
            QNAResult(
                id=faq["id"],
                question=faq["question"],
                answer=faq["answer"],
                score=score,
                category=faq["category"],
                subcategory=faq["subcategory"]
            )
            for faq, score in results_dict.values()
        ]
        
        # Sort by score (descending) and return top results
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]

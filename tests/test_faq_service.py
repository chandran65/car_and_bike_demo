"""Pytest test suite for FAQ Service."""

import numpy as np
import pytest

from src.mahindrabot.services.faq_service import (
    FAQService,
    cosine_similarity,
    cosine_similarity_batch,
)


class TestCosineSimilarity:
    """Test cosine similarity functions."""
    
    def test_identical_vectors(self):
        """Test cosine similarity with identical vectors."""
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        similarity = cosine_similarity(a, b)
        assert abs(similarity - 1.0) < 1e-6
    
    def test_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors."""
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        similarity = cosine_similarity(a, b)
        assert abs(similarity - 0.0) < 1e-6
    
    def test_opposite_vectors(self):
        """Test cosine similarity with opposite vectors."""
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([-1.0, 0.0, 0.0])
        similarity = cosine_similarity(a, b)
        assert abs(similarity - (-1.0)) < 1e-6
    
    def test_batch_similarities(self):
        """Test batch cosine similarity calculation."""
        query = np.array([1.0, 0.0, 0.0])
        embeddings = np.array([
            [1.0, 0.0, 0.0],  # Same as query
            [0.0, 1.0, 0.0],  # Orthogonal
            [-1.0, 0.0, 0.0], # Opposite
        ])
        
        similarities = cosine_similarity_batch(query, embeddings)
        
        assert abs(similarities[0] - 1.0) < 1e-6
        assert abs(similarities[1] - 0.0) < 1e-6
        assert abs(similarities[2] - (-1.0)) < 1e-6


@pytest.fixture(scope="module")
def faq_service():
    """Create FAQ service instance for tests."""
    return FAQService()


class TestFAQService:
    """Test FAQ Service functionality."""
    
    def test_service_initialization(self, faq_service):
        """Test that service initializes correctly."""
        assert hasattr(faq_service, 'faqs')
        assert hasattr(faq_service, 'question_embeddings')
        assert hasattr(faq_service, 'answer_embeddings')
    
    def test_faqs_loaded(self, faq_service):
        """Test that FAQs are loaded."""
        assert len(faq_service.faqs) > 0
    
    def test_embeddings_shape(self, faq_service):
        """Test that embeddings have correct shape."""
        n_faqs = len(faq_service.faqs)
        assert faq_service.question_embeddings.shape[0] == n_faqs
        assert faq_service.answer_embeddings.shape[0] == n_faqs
        assert faq_service.question_embeddings.shape[1] == 1536  # Ada-002 dimension
    
    def test_faq_ids_assigned(self, faq_service):
        """Test that all FAQs have IDs."""
        assert all('id' in faq for faq in faq_service.faqs)
        # Test IDs are sequential strings
        ids = [faq['id'] for faq in faq_service.faqs]
        expected_ids = [str(i) for i in range(len(faq_service.faqs))]
        assert ids == expected_ids
    
    def test_search_returns_results(self, faq_service):
        """Test that search returns results."""
        query = "transfer vehicle ownership"
        results = faq_service.search(query, limit=3)
        
        assert len(results) > 0
        assert len(results) <= 3
    
    def test_result_structure(self, faq_service):
        """Test that search results have correct structure."""
        query = "duplicate registration certificate"
        results = faq_service.search(query, limit=5)
        
        for result in results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'question')
            assert hasattr(result, 'answer')
            assert hasattr(result, 'score')
            assert hasattr(result, 'category')
            assert hasattr(result, 'subcategory')
            
            # Verify types
            assert isinstance(result.id, str)
            assert isinstance(result.question, str)
            assert isinstance(result.answer, str)
            assert isinstance(result.score, float)
            assert isinstance(result.category, str)
            assert isinstance(result.subcategory, str)
    
    def test_scores_in_range(self, faq_service):
        """Test that scores are in valid range [0, 1]."""
        query = "change address"
        results = faq_service.search(query, limit=10)
        
        for result in results:
            assert 0.0 <= result.score <= 1.0
    
    def test_results_sorted_by_score(self, faq_service):
        """Test that results are sorted by score (descending)."""
        query = "hypothecation"
        results = faq_service.search(query, limit=10)
        
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
    
    def test_limit_parameter(self, faq_service):
        """Test that limit parameter works correctly."""
        query = "vehicle registration"
        
        results_3 = faq_service.search(query, limit=3)
        results_10 = faq_service.search(query, limit=10)
        
        assert len(results_3) <= 3
        assert len(results_10) <= 10
        assert len(results_10) >= len(results_3)
    
    def test_search_relevance(self, faq_service):
        """Test that search returns relevant results."""
        # Test ownership transfer query
        query = "How do I transfer my vehicle to someone else?"
        results = faq_service.search(query, limit=3)
        
        # The top result should be about ownership transfer
        top_result = results[0]
        assert "transfer" in top_result.question.lower() or "transfer" in top_result.answer.lower()
        assert top_result.score > 0.5  # Should have decent similarity
    
    def test_different_queries(self, faq_service):
        """Test search with various queries."""
        queries = [
            "lost registration certificate",
            "change address",
            "NOC application",
            "duplicate RC",
            "hypothecation termination"
        ]
        
        for query in queries:
            results = faq_service.search(query, limit=3)
            assert len(results) > 0
            assert all(r.score > 0 for r in results)


class TestCaching:
    """Test caching functionality."""
    
    def test_cache_file_created(self, faq_service):
        """Test that cache file is created."""
        assert faq_service.cache_path.exists()
    
    def test_cache_is_valid_json(self, faq_service):
        """Test that cache file is valid JSON."""
        import json
        with open(faq_service.cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        assert 'questions' in cache_data
        assert 'answers' in cache_data
        assert 'metadata' in cache_data
    
    def test_cache_reload(self):
        """Test that service can load from cache."""
        # Create first instance (may generate or load cache)
        service1 = FAQService()
        n_faqs_1 = len(service1.faqs)
        
        # Create second instance (should load from cache)
        service2 = FAQService()
        n_faqs_2 = len(service2.faqs)
        
        assert n_faqs_1 == n_faqs_2
        assert service2.question_embeddings.shape == service1.question_embeddings.shape

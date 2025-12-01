"""
Test script for embedding-based similarity search
"""
from app.services.dataset_analyzer import DatasetAnalyzer

def test_similarity_search():
    print("🧪 Testing Embedding-Based Similarity Search\n")
    
    analyzer = DatasetAnalyzer()
    
    # Test 1: VPN issue
    print("Test 1: VPN Connection Issue")
    results = analyzer.find_similar_issues('my vpn is not connecting', 'network', limit=3)
    print(f"Found {len(results)} similar issues:")
    for r in results:
        print(f"  ✓ {r['title']} (similarity: {r['similarity_score']:.2f})")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Slow computer
    print("Test 2: Performance Issue")
    results = analyzer.find_similar_issues('computer is very slow', 'performance', limit=3)
    print(f"Found {len(results)} similar issues:")
    for r in results:
        print(f"  ✓ {r['title']} (similarity: {r['similarity_score']:.2f})")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Email problem
    print("Test 3: Email Issue")
    results = analyzer.find_similar_issues('cannot send emails in outlook', 'software', limit=3)
    print(f"Found {len(results)} similar issues:")
    for r in results:
        print(f"  ✓ {r['title']} (similarity: {r['similarity_score']:.2f})")
        if 'resolution_steps' in r:
            print(f"    Steps: {len(r['resolution_steps'])} troubleshooting steps available")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_similarity_search()

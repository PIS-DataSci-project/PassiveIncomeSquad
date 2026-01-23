def test_getEntityById():
    from Claudia import BasicQueryEngine, JournalQueryHandler, CategoryQueryHandler
    from Entities import Journal, Category, Area
    
    # Setup
    bq = BasicQueryEngine()
    
    jq = JournalQueryHandler()
    jq.setDbPathOrUrl("http://127.0.0.1:8080/blazegraph/sparql")
    bq.addJournalHandler(jq)
    
    cq = CategoryQueryHandler()
    cq.setDbPathOrUrl("relational.db")
    bq.addCategoryHandler(cq)
    
    # Test 1: Get journal (should return Journal or None)
    result = bq.getEntityById("2532-8816")
    if result:
        assert isinstance(result, Journal), f"Expected Journal, got {type(result)}"
        print(f"✓ Found journal: {result.getTitle()}")
    else:
        print("✗ Journal not found")
    
    # Test 2: Get category (should return Category or None)
    result = bq.getEntityById("Artificial Intelligence")
    if result:
        assert isinstance(result, Category), f"Expected Category, got {type(result)}"
        print(f"✓ Found category: {result.getName()}")
    else:
        print("✗ Category not found")
    
    # Test 3: Not found (should return None)
    result = bq.getEntityById("invalid-id-12345")
    assert result is None, f"Expected None, got {result}"
    print("✓ Correctly returns None for invalid ID")

# Run test
test_getEntityById()
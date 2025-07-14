from science_data_kit.core.models.entity_schemas import File, Entity, OntologyTerm

# Test File class
file = File(id="test-file", name="test.txt")
print(f"File: {file.id}, {file.name}, {file.path}")

# Test Entity class
entity = Entity(id="test-entity", name="Test Entity")
print(f"Entity: {entity.id}, {entity.name}, {entity.label}")

# Test OntologyTerm class
term = OntologyTerm(id="test-term", name="Test Term")
print(f"OntologyTerm: {term.id}, {term.name}, {term.term}")

print("All tests passed!")
import pytest
from pydantic import BaseModel, Field
from app.services.llm_service import LLMService

class DummyModel(BaseModel):
    name: str = Field(..., description="A name")
    age: int = Field(..., description="An age")

def test_llm_service_initialization():
    service = LLMService()
    assert service.provider is not None

def test_llm_service_text_generation():
    service = LLMService()
    response = service.generate_text("Test prompt")
    assert isinstance(response, str)

def test_llm_service_structured_generation_mock():
    service = LLMService()
    
    # We patch the mock provider to return something that fits DummyModel
    original_json_gen = service.provider.generate_json
    
    def mock_json_gen(prompt, **kwargs):
        if "Bad JSON" in prompt:
            return '{"name": "Alice", age: }' # Invalid JSON syntax
        if "Bad Schema" in prompt:
            return '{"name": "Alice", "wrong_field": 25}'
        return '{"name": "Alice", "age": 30}'
        
    service.provider.generate_json = mock_json_gen
    
    # 1. Valid JSON and valid schema
    result = service.generate_structured("Good prompt", DummyModel)
    assert result.name == "Alice"
    assert result.age == 30
    
    # 2. Max retries exceeded due to syntax error
    with pytest.raises(ValueError, match="Failed to generate valid structured output"):
        service.generate_structured("Bad JSON prompt", DummyModel, max_retries=1)

    # 3. Max retries exceeded due to schema error
    with pytest.raises(ValueError, match="Failed to generate valid structured output"):
        service.generate_structured("Bad Schema prompt", DummyModel, max_retries=1)
        
    # Restore original for safety
    service.provider.generate_json = original_json_gen

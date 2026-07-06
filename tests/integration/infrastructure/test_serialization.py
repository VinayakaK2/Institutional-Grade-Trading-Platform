"""
Integration Tests for Serialization Framework
"""
import pytest
from pydantic import BaseModel
from backend.infrastructure.utils.serialization import SerializationHelper, SerializationException

class DummySerializationModel(BaseModel):
    id: int
    name: str

def test_dict_serialization():
    data = {"key": "value", "count": 1}
    serialized = SerializationHelper.serialize_dict(data)
    assert isinstance(serialized, str)
    assert "value" in serialized
    
    deserialized = SerializationHelper.deserialize_dict(serialized)
    assert deserialized == data

def test_model_serialization():
    model = DummySerializationModel(id=42, name="Test")
    serialized = SerializationHelper.serialize_model(model)
    assert isinstance(serialized, str)
    
    deserialized = SerializationHelper.deserialize_model(DummySerializationModel, serialized)
    assert deserialized.id == 42
    assert deserialized.name == "Test"

def test_model_deserialization_failure():
    invalid_json = '{"id": "not_an_int", "name": "Test"}'
    with pytest.raises(SerializationException) as excinfo:
        SerializationHelper.deserialize_model(DummySerializationModel, invalid_json)
    
    assert excinfo.value.error_code == "SERIALIZATION_ERROR"

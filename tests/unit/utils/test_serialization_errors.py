import pytest
from pydantic import BaseModel
from backend.infrastructure.utils.serialization import SerializationHelper, SerializationException

class DummyModel(BaseModel):
    name: str

def test_serialize_dict_error():
    with pytest.raises(SerializationException):
        SerializationHelper.serialize_dict({"unserializable": object()})

def test_deserialize_dict_error():
    with pytest.raises(SerializationException):
        SerializationHelper.deserialize_dict("{invalid json")

def test_deserialize_model_validation_error():
    with pytest.raises(SerializationException):
        SerializationHelper.deserialize_model(DummyModel, '{"wrong": "data"}')

def test_deserialize_model_general_error():
    with pytest.raises(SerializationException):
        SerializationHelper.deserialize_model(DummyModel, "{invalid")

class BadModel:
    def model_dump_json(self):
        raise ValueError("Simulated error")

def test_serialize_model_error():
    with pytest.raises(SerializationException):
        SerializationHelper.serialize_model(BadModel())

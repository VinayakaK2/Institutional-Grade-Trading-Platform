import pytest
from backend.liquidity_grab_engine.config.config import LiquidityGrabConfiguration

def test_configuration_defaults():
    config = LiquidityGrabConfiguration()
    assert config.version == 1
    assert config.pipeline.fail_fast is True
    assert config.validation.strict_mode is True
    
def test_configuration_hash():
    config1 = LiquidityGrabConfiguration()
    config2 = LiquidityGrabConfiguration(version=2)
    assert config1.generate_hash() == config2.generate_hash()

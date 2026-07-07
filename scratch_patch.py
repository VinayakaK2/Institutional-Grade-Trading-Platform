import os

def patch_file(path):
    with open(path, 'r') as f:
        content = f.read()
    
    content = content.replace(
        'pipeline_version="1.0.0",\n        validation_status',
        'pipeline_version="1.0.0",\n        config_hash="test_hash",\n        validation_status'
    )
    content = content.replace(
        'pipeline_version="1.0.0",\n            validation_status',
        'pipeline_version="1.0.0",\n            config_hash="test_hash",\n            validation_status'
    )
    
    with open(path, 'w') as f:
        f.write(content)

patch_file('tests/unit/watchlist_engine/test_models.py')
patch_file('tests/unit/watchlist_engine/test_repository.py')

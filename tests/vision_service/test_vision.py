import sys
import os
import importlib.util

# Define the path to main.py
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chess-vision-service'))
main_path = os.path.join(service_dir, 'main.py')

# Import main.py as a module named 'vision_main'
spec = importlib.util.spec_from_file_location("vision_main", main_path)
vision_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vision_main)

def test_main_structure():
    # Verify that the main function exists
    assert hasattr(vision_main, 'main')
    assert callable(vision_main.main)

def test_logger_initialized():
    assert hasattr(vision_main, 'logger')
    # In main.py, logger = logging.getLogger(__name__)
    # When imported via importlib, __name__ is 'vision_main'
    assert vision_main.logger.name == "vision_main"

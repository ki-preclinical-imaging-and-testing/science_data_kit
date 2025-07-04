try:
    from science_data_kit.core.session.session import Session
    print("Successfully imported Session class directly from session.py")
except ImportError as e:
    print(f"Error importing Session class directly: {e}")

try:
    from science_data_kit.core.session import Session
    print("Successfully imported Session class from session package")
except ImportError as e:
    print(f"Error importing Session class from package: {e}")
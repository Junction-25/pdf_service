import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    API_TITLE = "Dar.ai PDF Service"
    API_DESCRIPTION = "A microservice to generate property comparisons and quotes."
    API_VERSION = "1.0.0"
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Data file paths
    PROPERTIES_FILE = "data/properties.json"
    CONTACTS_FILE = "data/contacts.json"

settings = Settings() 
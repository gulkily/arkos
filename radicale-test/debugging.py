import os
from radicale_calendar_manager import RadicaleCalendarManager

def _initialize_calendar_manager():
    """Initialize the Radicale calendar manager with environment configuration"""
    radicale_url = os.getenv("RADICALE_URL", "http://localhost:5232")
    radicale_username = os.getenv("RADICALE_USERNAME", "")
    radicale_password = os.getenv("RADICALE_PASSWORD", "")
    
    if not radicale_username or not radicale_password:
        logger.warning("Radicale credentials not found in environment variables")
        
    calendar_manager = RadicaleCalendarManager(
        url=radicale_url,
        username=radicale_username,
        password=radicale_password
    )
    print(calendar_manager.connect())    
    # Test connection during initialization
    if not calendar_manager.connect():
        raise NotImplementedError
        
    logger.info(f"Successfully connected to Radicale server at {radicale_url}")

        
if __name__ == "__main__":
    print("HERE")
    _initialize_calendar_manager()
    


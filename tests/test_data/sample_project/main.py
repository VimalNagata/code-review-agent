"""Main entry point for sample project."""
import logging
from src.api import create_api, APIError
from src.utils import log_event, format_currency

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_demo_data(api):
    """Set up demo data for the application."""
    # Create users
    api.register_user("Alice Smith", "alice@example.com", ["admin", "user"])
    api.register_user("Bob Johnson", "bob@example.com", ["user"])
    
    # Create products
    api.add_product("Laptop", 999.99, "Powerful laptop for developers")
    api.add_product("Monitor", 299.50, "27-inch 4K monitor")
    api.add_product("Keyboard", 79.99, "Mechanical keyboard")
    
    # Set up shopping carts
    api.create_cart("alice@example.com")
    api.add_to_cart("alice@example.com", "Laptop", 1)
    api.add_to_cart("alice@example.com", "Monitor", 2)
    
    api.create_cart("bob@example.com")
    api.add_to_cart("bob@example.com", "Keyboard", 1)


def main():
    """Main application entry point."""
    try:
        # Create API
        api = create_api()
        logger.info("API initialized successfully")
        
        # Set up demo data
        setup_demo_data(api)
        logger.info("Demo data created successfully")
        
        # Display cart totals
        alice_total = api.get_cart_total("alice@example.com")
        bob_total = api.get_cart_total("bob@example.com")
        
        logger.info(f"Alice's cart total: {format_currency(alice_total)}")
        logger.info(f"Bob's cart total: {format_currency(bob_total)}")
        
        # Log the event
        log_event("app_started", {
            "cart_totals": {
                "alice": alice_total,
                "bob": bob_total
            }
        })
        
        return 0
    
    except APIError as e:
        logger.error(f"API Error: {e.message} (code: {e.code})")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 2


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
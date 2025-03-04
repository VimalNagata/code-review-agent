"""API module for sample project."""
from typing import Dict, List, Any, Optional
from .core import ConfigManager, initialize_app
from .models import User, Product, Cart


class APIError(Exception):
    """API error class."""
    
    def __init__(self, message: str, code: int = 400):
        """Initialize with message and code."""
        super().__init__(message)
        self.code = code
        self.message = message


class API:
    """API handler for sample project."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        """Initialize the API."""
        self.config = config or initialize_app()
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.carts: Dict[str, Cart] = {}
        
    def register_user(self, name: str, email: str, roles: List[str] = None) -> User:
        """Register a new user."""
        if email in self.users:
            raise APIError(f"User with email {email} already exists", 409)
            
        user = User(name, email, roles)
        self.users[email] = user
        return user
        
    def get_user(self, email: str) -> User:
        """Get a user by email."""
        if email not in self.users:
            raise APIError(f"User with email {email} not found", 404)
            
        return self.users[email]
        
    def add_product(self, name: str, price: float, description: str = "") -> Product:
        """Add a new product."""
        if name in self.products:
            raise APIError(f"Product with name {name} already exists", 409)
            
        product = Product(name, price, description)
        self.products[name] = product
        return product
        
    def get_product(self, name: str) -> Product:
        """Get a product by name."""
        if name not in self.products:
            raise APIError(f"Product with name {name} not found", 404)
            
        return self.products[name]
        
    def create_cart(self, user_email: str) -> Cart:
        """Create a shopping cart for a user."""
        user = self.get_user(user_email)
        cart = Cart(user)
        self.carts[user_email] = cart
        return cart
        
    def add_to_cart(self, user_email: str, product_name: str, quantity: int = 1) -> None:
        """Add a product to a user's cart."""
        if user_email not in self.carts:
            raise APIError(f"No cart found for user {user_email}", 404)
            
        product = self.get_product(product_name)
        self.carts[user_email].add_item(product, quantity)
        
    def get_cart_total(self, user_email: str) -> float:
        """Get the total price of items in a user's cart."""
        if user_email not in self.carts:
            raise APIError(f"No cart found for user {user_email}", 404)
            
        return self.carts[user_email].get_total()


def create_api() -> API:
    """Create and initialize the API."""
    config = initialize_app()
    return API(config)
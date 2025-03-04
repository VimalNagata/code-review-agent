"""Model definitions for sample project."""
from typing import List, Dict, Any
from .core import BaseModel


class User(BaseModel):
    """User model."""
    
    def __init__(self, name: str, email: str, roles: List[str] = None):
        """Initialize a user."""
        super().__init__(name)
        self.email = email
        self.roles = roles or []
        
    def has_role(self, role: str) -> bool:
        """Check if user has a role."""
        return role in self.roles
        
    def add_role(self, role: str) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)


class Product(BaseModel):
    """Product model."""
    
    def __init__(self, name: str, price: float, description: str = ""):
        """Initialize a product."""
        super().__init__(name)
        self.price = price
        self.description = description
        self.tags: List[str] = []
        
    def add_tag(self, tag: str) -> None:
        """Add a tag to the product."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "tags": self.tags
        }


class Cart:
    """Shopping cart model."""
    
    def __init__(self, user: User):
        """Initialize a cart for a user."""
        self.user = user
        self.items: List[Dict[str, Any]] = []
        
    def add_item(self, product: Product, quantity: int = 1) -> None:
        """Add a product to the cart."""
        self.items.append({
            "product": product,
            "quantity": quantity
        })
        
    def get_total(self) -> float:
        """Calculate the total price of items in the cart."""
        return sum(item["product"].price * item["quantity"] for item in self.items)
        
    def clear(self) -> None:
        """Clear the cart."""
        self.items = []
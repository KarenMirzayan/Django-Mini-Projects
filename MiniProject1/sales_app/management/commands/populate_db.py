import random
from django.utils.timezone import now
from products.models import Category, Product
from taggit.models import Tag

# Sample categories
categories_data = [
    {"name": "Electronics", "description": "Devices and gadgets"},
    {"name": "Clothing", "description": "Men and Women fashion"},
    {"name": "Home & Kitchen", "description": "Appliances and decor"},
    {"name": "Books", "description": "Educational and fictional books"},
    {"name": "Sports", "description": "Sports gear and accessories"},
]

# Sample products
products_data = [
    {"name": "Laptop", "description": "High-performance laptop", "price": 1200.00, "category": "Electronics", "stock": 10, "tags": ["tech", "gadgets"]},
    {"name": "T-Shirt", "description": "Cotton t-shirt", "price": 15.99, "category": "Clothing", "stock": 50, "tags": ["fashion", "casual"]},
    {"name": "Microwave", "description": "700W Microwave Oven", "price": 99.99, "category": "Home & Kitchen", "stock": 20, "tags": ["appliances", "cooking"]},
    {"name": "Python Programming", "description": "Learn Python", "price": 29.99, "category": "Books", "stock": 15, "tags": ["coding", "education"]},
    {"name": "Basketball", "description": "Standard size basketball", "price": 25.50, "category": "Sports", "stock": 30, "tags": ["sports", "outdoor"]},
]

def populate_db():
    print("📌 Populating database...")

    # Create Categories
    category_mapping = {}
    for data in categories_data:
        category, created = Category.objects.get_or_create(name=data["name"], defaults={"description": data["description"]})
        category_mapping[data["name"]] = category
        if created:
            print(f"✅ Created category: {category.name}")
    
    # Create Products
    for data in products_data:
        category = category_mapping[data["category"]]
        product, created = Product.objects.get_or_create(
            name=data["name"],
            defaults={
                "description": data["description"],
                "price": data["price"],
                "category": category,
                "stock": data["stock"],
                "created_at": now(),
                "updated_at": now(),
            },
        )
        if created:
            # Add tags
            product.tags.add(*data["tags"])
            print(f"✅ Created product: {product.name} (Category: {category.name})")

    print("🎉 Database population complete!")

# Run the function
if __name__ == "__main__":
    populate_db()

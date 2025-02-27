import random
from django.utils.timezone import now
from products.models import Category, Product
from taggit.models import Tag

categories_data = [
    {"name": "Electronics", "description": "Devices and gadgets"},
    {"name": "Clothing", "description": "Men and Women fashion"},
    {"name": "Home & Kitchen", "description": "Appliances and decor"},
    {"name": "Books", "description": "Educational and fictional books"},
    {"name": "Sports", "description": "Sports gear and accessories"},
]

products_data = [
    {"name": "Laptop", "description": "High-performance laptop", "category": "Electronics", "tags": ["tech", "gadgets"]},
    {"name": "T-Shirt", "description": "Cotton t-shirt", "category": "Clothing", "tags": ["fashion", "casual"]},
    {"name": "Microwave", "description": "700W Microwave Oven", "category": "Home & Kitchen", "tags": ["appliances", "cooking"]},
    {"name": "Python Programming", "description": "Learn Python", "category": "Books", "tags": ["coding", "education"]},
    {"name": "Basketball", "description": "Standard size basketball", "category": "Sports", "tags": ["sports", "outdoor"]},
]

def populate_db():
    print("📌 Populating database...")

    category_mapping = {}
    for data in categories_data:
        category, created = Category.objects.get_or_create(name=data["name"], defaults={"description": data["description"]})
        category_mapping[data["name"]] = category
        if created:
            print(f"✅ Created category: {category.name}")
    
    for data in products_data:
        category = category_mapping[data["category"]]
        product, created = Product.objects.get_or_create(
            name=data["name"],
            defaults={
                "description": data["description"],
                "category": category,
                "created_at": now(),
                "updated_at": now(),
            },
        )
        if created:
            product.tags.add(*data["tags"])
            print(f"✅ Created product: {product.name} (Category: {category.name})")

    print("🎉 Database population complete!")

if __name__ == "__main__":
    populate_db()

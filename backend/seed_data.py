# backend/seed_data.py
"""
Скрипт для заполнения базы данных тестовыми данными.
Создает категории и товары для демонстрации работы приложения.
Использует placeholder изображения с unsplash.com.
"""

from app.database import SessionLocal, init_db
from app.models.category import Category
from app.models.product import Product


def create_categories(db):
    """
    Создает категории товаров.

    Args:
        db: Сессия SQLAlchemy

    Returns:
        dict: Словарь созданных категорий {slug: Category}
    """
    categories_data = [
        {"name": "Electronics", "slug": "electronics"},
        {"name": "Clothing", "slug": "clothing"},
        {"name": "Books", "slug": "books"},
        {"name": "Home & Garden", "slug": "home-garden"},
    ]

    categories = {}
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        categories[cat_data["slug"]] = category

    db.commit()

    # Обновляем объекты после commit для получения ID
    for category in categories.values():
        db.refresh(category)

    return categories


def create_products(db, categories):
    """
    Создает товары в различных категориях.

    Args:
        db: Сессия SQLAlchemy
        categories: Словарь категорий
    """
    products_data = [
        # Electronics
        {
            "name": "Wireless Headphones",
            "description": "High-quality wireless headphones with noise cancellation. Perfect for music lovers and professionals. Battery life up to 30 hours.",
            "price": 299.99,
            "category_id": categories["electronics"].id,
            "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400"
        },
        {
            "name": "Smart Watch Pro",
            "description": "Advanced smartwatch with fitness tracking, heart rate monitor, and GPS. Water resistant up to 50m. Compatible with iOS and Android.",
            "price": 399.99,
            "category_id": categories["electronics"].id,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"
        },
        {
            "name": "Laptop Stand",
            "description": "Ergonomic aluminum laptop stand. Adjustable height and angle. Improves posture and reduces neck strain. Compatible with all laptop sizes.",
            "price": 49.99,
            "category_id": categories["electronics"].id,
            "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"
        },
        {
            "name": "USB-C Hub",
            "description": "Multi-port USB-C hub with HDMI, USB 3.0, and SD card reader. Fast data transfer and 4K video output. Compact design perfect for travel.",
            "price": 79.99,
            "category_id": categories["electronics"].id,
            "image_url": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400"
        },
        {
            "name": "Wireless Keyboard",
            "description": "Compact wireless keyboard with mechanical switches. Long battery life and ergonomic design. Perfect for both work and gaming.",
            "price": 89.99,
            "category_id": categories["electronics"].id,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"
        },

        # Clothing
        {
            "name": "Running Shoes",
            "description": "Comfortable running shoes with excellent cushioning. Breathable mesh upper and durable rubber sole. Perfect for jogging and gym workouts.",
            "price": 129.99,
            "category_id": categories["clothing"].id,
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"
        },

        # Books
        {
            "name": "Python Programming Guide",
            "description": "Comprehensive guide to Python programming. From basics to advanced topics. Includes practical examples and exercises. Perfect for beginners and intermediate programmers.",
            "price": 45.99,
            "category_id": categories["books"].id,
            "image_url": "https://images.unsplash.com/photo-1589998059171-988d887df646?w=400"
        },
        {
            "name": "The Art of Design",
            "description": "Inspirational book about design principles and creative thinking. Beautiful illustrations and case studies from famous designers.",
            "price": 39.99,
            "category_id": categories["books"].id,
            "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400"
        },
        {
            "name": "Cooking Masterclass",
            "description": "Professional cooking techniques and recipes. Step-by-step instructions with beautiful photography. Learn from world-class chefs.",
            "price": 49.99,
            "category_id": categories["books"].id,
            "image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400"
        },

        # Home & Garden
        {
            "name": "Plant Pot Set",
            "description": "Set of 3 ceramic plant pots with drainage holes. Modern design perfect for indoor plants. Includes saucers to protect furniture.",
            "price": 34.99,
            "category_id": categories["home-garden"].id,
            "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=400"
        },
        {
            "name": "LED Desk Lamp",
            "description": "Adjustable LED desk lamp with touch control. Multiple brightness levels and color temperatures. Energy efficient and eye-friendly.",
            "price": 59.99,
            "category_id": categories["home-garden"].id,
            "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400"
        },
        {
            "name": "Throw Pillow Set",
            "description": "Set of 2 decorative throw pillows. Soft and comfortable with removable covers. Perfect for sofa or bed decoration.",
            "price": 39.99,
            "category_id": categories["home-garden"].id,
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"
        },
        {
            "name": "Garden Tool Kit",
            "description": "Complete garden tool kit with 10 essential tools. Durable stainless steel construction. Includes carrying bag for easy storage.",
            "price": 79.99,
            "category_id": categories["home-garden"].id,
            "image_url": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"
        },
    ]

    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)

    db.commit()
    print(f" Created {len(products_data)} products")


def seed_database():
    """
    Главная функция для заполнения базы данных.
    Создает таблицы, категории и товары.
    """
    print(" Starting database seeding...")

    # Инициализируем БД (создаем таблицы)
    init_db()
    print(" Database tables created")

    # Создаем сессию
    db = SessionLocal()

    try:
        # Проверяем, не заполнена ли уже БД
        existing_categories = db.query(Category).count()
        if existing_categories > 0:
            print(" Database already contains data. Skipping seed.")
            return

        # Создаем категории
        print(" Creating categories...")
        categories = create_categories(db)
        print(f" Created {len(categories)} categories")

        # Создаем товары
        print(" Creating products...")
        create_products(db, categories)

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
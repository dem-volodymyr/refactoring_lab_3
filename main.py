import uuid
from datetime import datetime
from typing import List, Dict, Optional


class User:
    def __init__(self, username: str, email: str, password: str, address: str = "", phone: str = ""):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password  # В реальному проекті використовувати хешування паролів
        self.address = address
        self.phone = phone
        self.orders = []  # Список замовлень користувача

    def register(self) -> bool:
        # Логіка реєстрації користувача
        print(f"Користувач {self.username} зареєстрований")
        return True

    def login(self, email: str, password: str) -> bool:
        # Перевірка логіну користувача
        if self.email == email and self.password == password:
            print(f"Користувач {self.username} увійшов в систему")
            return True
        return False

    def logout(self) -> bool:
        # Логіка виходу користувача
        print(f"Користувач {self.username} вийшов з системи")
        return True

    def view_orders(self) -> List['Order']:
        # Повертає список замовлень користувача
        return self.orders

    def update_profile(self, username: str = None, address: str = None, phone: str = None) -> bool:
        # Оновлення профілю користувача
        if username:
            self.username = username
        if address:
            self.address = address
        if phone:
            self.phone = phone
        print(f"Профіль користувача {self.username} оновлено")
        return True


class Product:
    def __init__(self, name: str, description: str, price: float, stock_quantity: int, category: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.category = category
        self.reviews = []  # Список відгуків про товар

    def update_stock(self, quantity: int) -> bool:
        # Оновлення кількості товару на складі
        if self.stock_quantity + quantity >= 0:
            self.stock_quantity += quantity
            print(f"Кількість товару '{self.name}' оновлено. Нова кількість: {self.stock_quantity}")
            return True
        print(f"Помилка: недостатньо товару '{self.name}' на складі")
        return False

    def get_details(self) -> Dict:
        # Повертає інформацію про товар
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'category': self.category
        }

    def is_available(self, quantity: int = 1) -> bool:
        # Перевірка доступності товару в запрошеній кількості
        return self.stock_quantity >= quantity


class CartItem:
    def __init__(self, product: Product, quantity: int = 1):
        self.product = product
        self.quantity = quantity

    def calculate_subtotal(self) -> float:
        # Розрахунок вартості позиції
        return self.product.price * self.quantity

    def update_quantity(self, quantity: int) -> bool:
        # Оновлення кількості товару в кошику
        if quantity > 0 and quantity <= self.product.stock_quantity:
            self.quantity = quantity
            return True
        return False


class ShoppingCart:
    def __init__(self, user: User):
        self.id = str(uuid.uuid4())
        self.user = user
        self.items = []  # Список товарів у кошику (об'єкти CartItem)

    def add_item(self, product: Product, quantity: int = 1) -> bool:
        # Додавання товару в кошик
        if not product.is_available(quantity):
            print(f"Помилка: недостатньо товару '{product.name}' на складі")
            return False

        # Перевіряємо, чи товар вже є в кошику
        for item in self.items:
            if item.product.id == product.id:
                # Оновлюємо кількість
                if item.update_quantity(item.quantity + quantity):
                    print(f"Кількість товару '{product.name}' в кошику оновлено. Нова кількість: {item.quantity}")
                    return True
                return False

        # Додаємо новий товар у кошик
        self.items.append(CartItem(product, quantity))
        print(f"Товар '{product.name}' додано в кошик у кількості {quantity}")
        return True

    def remove_item(self, product_id: str) -> bool:
        # Видалення товару з кошика
        for i, item in enumerate(self.items):
            if item.product.id == product_id:
                del self.items[i]
                print(f"Товар '{item.product.name}' видалено з кошика")
                return True
        print("Помилка: товар не знайдено в кошику")
        return False

    def update_quantity(self, product_id: str, quantity: int) -> bool:
        # Оновлення кількості товару в кошику
        for item in self.items:
            if item.product.id == product_id:
                if item.update_quantity(quantity):
                    print(f"Кількість товару '{item.product.name}' в кошику оновлено. Нова кількість: {quantity}")
                    return True
                print(f"Помилка: неможливо оновити кількість товару '{item.product.name}'")
                return False
        print("Помилка: товар не знайдено в кошику")
        return False

    def get_items(self) -> List[CartItem]:
        # Повертає список товарів у кошику
        return self.items

    def calculate_total(self) -> float:
        # Розрахунок загальної вартості кошика
        return sum(item.calculate_subtotal() for item in self.items)

    def checkout(self) -> Optional['Order']:
        # Оформлення замовлення на основі вмісту кошика
        if not self.items:
            print("Помилка: кошик порожній")
            return None

        # Перевіряємо наявність товарів на складі
        for item in self.items:
            if not item.product.is_available(item.quantity):
                print(f"Помилка: недостатньо товару '{item.product.name}' на складі")
                return None

        # Створюємо замовлення
        order = Order(self.user, self.user.address)

        # Додаємо товари до замовлення
        for item in self.items:
            order.add_product(item.product, item.quantity)
            # Зменшуємо кількість товару на складі
            item.product.update_stock(-item.quantity)

        # Очищаємо кошик
        self.clear_cart()

        # Додаємо замовлення до списку замовлень користувача
        self.user.orders.append(order)

        print(f"Замовлення успішно оформлено. ID замовлення: {order.id}")
        return order

    def clear_cart(self) -> bool:
        # Очищення кошика
        self.items = []
        print("Кошик очищено")
        return True


class OrderItem:
    def __init__(self, product: Product, quantity: int, price: float):
        self.product = product
        self.quantity = quantity
        self.price = price  # Ціна товару на момент замовлення

    def calculate_subtotal(self) -> float:
        # Розрахунок вартості позиції замовлення
        return self.price * self.quantity


class Order:
    def __init__(self, user: User, shipping_address: str, payment_method: str = "Оплата при отриманні"):
        self.id = str(uuid.uuid4())
        self.user = user
        self.order_date = datetime.now()
        self.status = "Нове"  # Нове, В обробці, Відправлено, Доставлено, Скасовано
        self.shipping_address = shipping_address
        self.payment_method = payment_method
        self.items = []  # Список товарів у замовленні (об'єкти OrderItem)
        self.total_amount = 0.0

    def add_product(self, product: Product, quantity: int = 1) -> bool:
        # Додавання товару до замовлення
        self.items.append(OrderItem(product, quantity, product.price))
        self.calculate_total()
        print(f"Товар '{product.name}' додано до замовлення у кількості {quantity}")
        return True

    def remove_product(self, product_id: str) -> bool:
        # Видалення товару із замовлення
        for i, item in enumerate(self.items):
            if item.product.id == product_id:
                del self.items[i]
                self.calculate_total()
                print(f"Товар '{item.product.name}' видалено із замовлення")
                return True
        print("Помилка: товар не знайдено в замовленні")
        return False

    def calculate_total(self) -> float:
        # Розрахунок загальної вартості замовлення
        self.total_amount = sum(item.calculate_subtotal() for item in self.items)
        return self.total_amount

    def place_order(self) -> bool:
        # Розміщення замовлення
        if not self.items:
            print("Помилка: замовлення не містить товарів")
            return False

        self.status = "В обробці"
        print(f"Замовлення {self.id} розміщено та знаходиться в обробці")
        return True

    def cancel_order(self) -> bool:
        # Скасування замовлення
        if self.status in ["Відправлено", "Доставлено"]:
            print(f"Помилка: неможливо скасувати замовлення {self.id} у статусі '{self.status}'")
            return False

        # Повертаємо товари на склад
        for item in self.items:
            item.product.update_stock(item.quantity)

        self.status = "Скасовано"
        print(f"Замовлення {self.id} скасовано")
        return True

    def get_order_details(self) -> Dict:
        # Повертає інформацію про замовлення
        return {
            'id': self.id,
            'user_id': self.user.id,
            'order_date': self.order_date,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'payment_method': self.payment_method,
            'items': [{'product_name': item.product.name,
                       'quantity': item.quantity,
                       'price': item.price,
                       'subtotal': item.calculate_subtotal()} for item in self.items],
            'total_amount': self.total_amount
        }


class Review:
    def __init__(self, user: User, product: Product, rating: int, comment: str = ""):
        self.id = str(uuid.uuid4())
        self.user = user
        self.product = product
        self.rating = min(max(rating, 1), 5)  # Рейтинг від 1 до 5
        self.comment = comment
        self.review_date = datetime.now()

        # Додаємо відгук до списку відгуків про товар
        product.reviews.append(self)

    def add_review(self) -> bool:
        # Додавання відгуку до системи
        print(f"Користувач {self.user.username} залишив відгук про товар '{self.product.name}'")
        return True

    def update_review(self, rating: int = None, comment: str = None) -> bool:
        # Оновлення відгуку
        if rating:
            self.rating = min(max(rating, 1), 5)
        if comment is not None:
            self.comment = comment
        print(f"Відгук користувача {self.user.username} про товар '{self.product.name}' оновлено")
        return True

    def delete_review(self) -> bool:
        # Видалення відгуку
        if self in self.product.reviews:
            self.product.reviews.remove(self)
            print(f"Відгук користувача {self.user.username} про товар '{self.product.name}' видалено")
            return True
        return False

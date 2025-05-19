import unittest
from main import User, Product, ShoppingCart, Review


class TestOnlineShop(unittest.TestCase):

    def setUp(self):
        # Створення тестових об'єктів для використання в тестах
        self.user = User("testuser", "test@example.com", "password123", "Test Address", "123456789")

        # Створення тестових товарів
        self.product1 = Product("iPhone 15", "Смартфон Apple", 39999.99, 10, "Електроніка")
        self.product2 = Product("Samsung Galaxy S23", "Смартфон Samsung", 32999.99, 15, "Електроніка")
        self.product3 = Product("MacBook Pro", "Ноутбук Apple", 69999.99, 5, "Комп'ютери")

        # Створення кошика для користувача
        self.cart = ShoppingCart(self.user)

    def test_user_registration(self):
        # Тест реєстрації користувача
        user = User("newuser", "new@example.com", "newpass123")
        self.assertTrue(user.register())
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "new@example.com")

    def test_user_login(self):
        # Тест входу користувача в систему
        self.assertTrue(self.user.login("test@example.com", "password123"))
        self.assertFalse(self.user.login("test@example.com", "wrongpassword"))

    def test_user_update_profile(self):
        # Тест оновлення профілю користувача
        self.assertTrue(self.user.update_profile(username="updateduser", phone="987654321"))
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.phone, "987654321")
        self.assertEqual(self.user.address, "Test Address")  # Не повинно змінитися

    def test_product_update_stock(self):
        # Тест оновлення кількості товару на складі
        initial_stock = self.product1.stock_quantity
        self.assertTrue(self.product1.update_stock(5))
        self.assertEqual(self.product1.stock_quantity, initial_stock + 5)

        # Перевірка негативного сценарію - спроба відняти більше, ніж є на складі
        self.assertFalse(self.product1.update_stock(-(initial_stock + 5 + 1)))
        self.assertEqual(self.product1.stock_quantity, initial_stock + 5)  # Кількість не повинна змінитися

    def test_product_availability(self):
        # Тест перевірки доступності товару
        self.assertTrue(self.product1.is_available(5))  # Запит кількості менше наявної
        self.assertTrue(self.product1.is_available(10))  # Запит рівно наявної кількості
        self.assertFalse(self.product1.is_available(11))  # Запит більше наявної кількості

    def test_cart_add_item(self):
        # Тест додавання товару до кошика
        self.assertTrue(self.cart.add_item(self.product1, 2))
        self.assertEqual(len(self.cart.get_items()), 1)
        self.assertEqual(self.cart.get_items()[0].product.id, self.product1.id)
        self.assertEqual(self.cart.get_items()[0].quantity, 2)

        # Додавання ще одного товару
        self.assertTrue(self.cart.add_item(self.product2, 1))
        self.assertEqual(len(self.cart.get_items()), 2)

        # Додавання існуючого товару (повинно збільшити кількість)
        self.assertTrue(self.cart.add_item(self.product1, 1))
        self.assertEqual(len(self.cart.get_items()), 2)  # Кількість позицій не змінилася
        self.assertEqual(self.cart.get_items()[0].quantity, 3)  # Кількість товару збільшилася

    def test_cart_remove_item(self):
        # Тест видалення товару з кошика
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 1)
        self.assertEqual(len(self.cart.get_items()), 2)

        # Видалення товару
        self.assertTrue(self.cart.remove_item(self.product1.id))
        self.assertEqual(len(self.cart.get_items()), 1)
        self.assertEqual(self.cart.get_items()[0].product.id, self.product2.id)

        # Спроба видалити неіснуючий товар
        self.assertFalse(self.cart.remove_item("nonexistent_id"))

    def test_cart_update_quantity(self):
        # Тест оновлення кількості товару в кошику
        self.cart.add_item(self.product1, 2)
        self.assertTrue(self.cart.update_quantity(self.product1.id, 5))
        self.assertEqual(self.cart.get_items()[0].quantity, 5)

        # Спроба встановити недопустиму кількість
        self.assertFalse(self.cart.update_quantity(self.product1.id, 20))  # Більше ніж є на складі
        self.assertEqual(self.cart.get_items()[0].quantity, 5)  # Кількість не повинна змінитися

    def test_cart_calculate_total(self):
        # Тест розрахунку загальної вартості кошика
        self.cart.add_item(self.product1, 2)  # 39999.99 * 2 = 79999.98
        self.cart.add_item(self.product2, 1)  # 32999.99
        expected_total = 2 * self.product1.price + self.product2.price
        self.assertAlmostEqual(self.cart.calculate_total(), expected_total, places=2)

    def test_checkout_process(self):
        # Тест процесу оформлення замовлення
        # Додаємо товари до кошика
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 1)

        # Запам'ятовуємо початкову кількість товарів на складі
        product1_initial_stock = self.product1.stock_quantity
        product2_initial_stock = self.product2.stock_quantity

        # Оформлюємо замовлення
        order = self.cart.checkout()

        # Перевіряємо, що замовлення створено успішно
        self.assertIsNotNone(order)
        self.assertEqual(order.status, "Нове")
        self.assertEqual(len(order.items), 2)

        # Перевіряємо, що кількість товарів на складі зменшилася
        self.assertEqual(self.product1.stock_quantity, product1_initial_stock - 2)
        self.assertEqual(self.product2.stock_quantity, product2_initial_stock - 1)

        # Перевіряємо, що кошик очищено
        self.assertEqual(len(self.cart.get_items()), 0)

        # Перевіряємо, що замовлення додано до списку замовлень користувача
        self.assertEqual(len(self.user.view_orders()), 1)
        self.assertEqual(self.user.view_orders()[0].id, order.id)

    def test_order_cancel(self):
        # Тест скасування замовлення
        # Додаємо товари до кошика і оформлюємо замовлення
        self.cart.add_item(self.product1, 2)
        order = self.cart.checkout()

        # Запам'ятовуємо кількість товарів на складі після оформлення замовлення
        product1_stock_after_order = self.product1.stock_quantity

        # Скасовуємо замовлення
        self.assertTrue(order.cancel_order())
        self.assertEqual(order.status, "Скасовано")

        # Перевіряємо, що товари повернуто на склад
        self.assertEqual(self.product1.stock_quantity, product1_stock_after_order + 2)

    def test_review_system(self):
        # Тест системи відгуків
        # Створюємо відгук
        review = Review(self.user, self.product1, 5, "Дуже задоволений товаром!")
        self.assertTrue(review.add_review())

        # Перевіряємо, що відгук додано до списку відгуків про товар
        self.assertEqual(len(self.product1.reviews), 1)
        self.assertEqual(self.product1.reviews[0].rating, 5)
        self.assertEqual(self.product1.reviews[0].comment, "Дуже задоволений товаром!")

        # Оновлюємо відгук
        self.assertTrue(review.update_review(rating=4, comment="Гарний товар, але є недоліки"))
        self.assertEqual(self.product1.reviews[0].rating, 4)
        self.assertEqual(self.product1.reviews[0].comment, "Гарний товар, але є недоліки")

        # Видаляємо відгук
        self.assertTrue(review.delete_review())
        self.assertEqual(len(self.product1.reviews), 0)


if __name__ == '__main__':
    unittest.main()
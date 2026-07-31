# Руководство по тестированию API `fastapi-shop` в Postman

Репозиторий: [tsudoku04/fastapi-shop](https://github.com/tsudoku04/fastapi-shop)

Это руководство составлено на основе реального анализа кода бэкенда (`backend/app`) и живого тестирования запущенного сервера — все статус-коды и тела ответов ниже проверены, а не предположены.

К руководству прилагаются два файла, которые можно сразу импортировать в Postman:

- **`FastAPI-Shop.postman_collection.json`** — готовая коллекция из 22 запросов с автоматическими тестами (`pm.test`);
- **`FastAPI-Shop-Local.postman_environment.json`** — окружение с переменной `base_url`.

---

## 1. О проекте

FastAPI-бэкенд простого интернет-магазина без авторизации, на SQLite. Три сущности:

| Сущность | Роутер | Префикс |
|---|---|---|
| Товары (products) | `app/routes/products.py` | `/api/products` |
| Категории (categories) | `app/routes/categories.py` | `/api/categories` |
| Корзина (cart) | `app/routes/cart.py` | `/api/cart` |

Важная архитектурная особенность: **у корзины нет хранения на сервере**. Нет ни таблицы `carts`, ни cart_id, ни cookie/сессии. Текущее содержимое корзины — это просто `{product_id: quantity}}`, которое **клиент обязан передавать в теле каждого запроса**, а сервер возвращает обновлённую версию в ответ. Это нужно учитывать при построении тестов в Postman (см. раздел 5).

---

## 2. Подготовка окружения перед тестированием

```bash
git clone https://github.com/tsudoku04/fastapi-shop.git
cd fastapi-shop/backend
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### ⚠️ Обязательный шаг: заполнение базы данных

```bash
python seed_data.py
```

Без этого шага тестировать почти нечего: в `main.py` есть баг — обработчик `on_startup` вызывает `init_db` **без скобок**, поэтому таблицы при старте сервера автоматически не создаются, и любой запрос к API будет падать с ошибкой "no such table". Скрипт `seed_data.py` создаёт таблицы правильно (`init_db()`) и заполняет БД: **4 категории** (Electronics, Clothing, Books, Home & Garden) и **13 товаров**.

### Запуск сервера

```bash
python run.py
```

Сервер поднимется на `http://localhost:8000`. Полезные адреса:

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI-схема: `http://localhost:8000/openapi.json`

---

## 3. Настройка Postman

### Вариант А — импортировать готовое (рекомендуется)

1. Postman → **Import** → перетащить `FastAPI-Shop.postman_collection.json` и `FastAPI-Shop-Local.postman_environment.json`.
2. В правом верхнем углу выбрать окружение **"FastAPI Shop — Local"**.
3. Открыть коллекцию **"FastAPI Shop — Тестирование API"** и запускать запросы по порядку — переменные (`cart`, `product_id`, `category_id`) уже настроены и автоматически обновляются тест-скриптами.

### Вариант Б — настроить вручную с нуля

1. Создать новую коллекцию, например `FastAPI Shop`.
2. Создать окружение с переменной `base_url = http://localhost:8000`.
3. Для запросов с телом (`POST`, `PUT`, `DELETE /api/cart/remove/...`) добавлять заголовок `Content-Type: application/json`.
4. Тело задавать в **Body → raw → JSON**.

---

## 4. Карта эндпоинтов

| Метод | URL | Назначение | Требует тело |
|---|---|---|---|
| GET | `/` | Приветственное сообщение | — |
| GET | `/api/docs`, `/api/redoc` | Документация | — |
| GET | `/api/products` | Список всех товаров | — |
| GET | `/api/products/{product_id}` | Товар по ID | — |
| GET | `/api/products/category/{category_id}` | Товары по категории | — |
| GET | `/api/categories` | Список всех категорий | — |
| GET | `/api/categories/{category_id}` | Категория по ID | — |
| POST | `/api/cart/add` | Добавить товар в корзину | ✅ |
| PUT | `/api/cart/update` | Изменить количество товара | ✅ |
| DELETE | `/api/cart/remove/{product_id}` | Удалить товар из корзины | ✅ |

Эндпоинтов создания/редактирования товаров и категорий **в API нет**, хотя логика для этого частично есть в сервисном слое (`ProductService.create_product`, `CategoryServices.create_category`) — она просто не подключена ни к одному роуту.

---

## 5. Как тестировать корзину (важно!)

Поскольку сервер не хранит корзину, тестовый сценарий в Postman строится так:

1. Первый запрос `POST /api/cart/add` отправляется с `"cart": {}`.
2. Сервер возвращает актуальный `cart` в ответе — его нужно сохранить (в готовой коллекции это делает тест-скрипт: `pm.collectionVariables.set('cart', JSON.stringify(json.cart))`).
3. Следующий запрос (`update`, ещё один `add`, `remove`) подставляет сохранённый `{{cart}}` в тело запроса и снова получает обновлённую версию.

Если тестировать вручную (без скриптов), после каждого запроса нужно **вручную копировать** объект `cart` из ответа в тело следующего запроса — иначе изменения не будут "накапливаться".

Пример цепочки:

```
POST /api/cart/add   {"product_id":1,"quantity":2,"cart":{}}
  → {"cart":{"1":2}}

PUT /api/cart/update  {"product_id":1,"quantity":10,"cart":{"1":2}}
  → {"cart":{"1":10}}

DELETE /api/cart/remove/1   body: {"cart":{"1":10}}
  → {"cart":{}}
```

---

## 6. Тест-кейсы по группам

### 6.1 Товары (`/api/products`)

| # | Кейс | Запрос | Ожидаемый статус | Проверить в ответе |
|---|---|---|---|---|
| 1 | Список товаров | `GET /api/products` | 200 | `products` — массив, `total` = `products.length`, у каждого товара есть вложенный `category` |
| 2 | Товар по ID | `GET /api/products/1` | 200 | `id == 1`, есть `name`, `price`, `category_id`, `created_at` |
| 3 | Товар не найден | `GET /api/products/9999` | 404 | `detail: "Product with id 9999 not found"` |
| 4 | Нечисловой ID | `GET /api/products/abc` | 422 | ошибка валидации пути (`int_parsing`) — это делает сам FastAPI, до вызова бизнес-логики |
| 5 | Товары по категории | `GET /api/products/category/1` | 200 | все товары имеют `category_id == 1` |
| 6 | Несуществующая категория | `GET /api/products/category/9999` | 404 | `detail: "Category with id 9999 not found"` |
| 7 | Создание товара не поддерживается | `POST /api/products` | 405 | `Method Not Allowed` — роут существует только для GET |

### 6.2 Категории (`/api/categories`)

| # | Кейс | Запрос | Ожидаемый статус | 
|---|---|---|---|---|
| 8 | Список категорий | `GET /api/categories` | 200 | 
| 9 | Категория по ID | `GET /api/categories/1` | 200 | 
| 10 | Категория не найдена | `GET /api/categories/9999` | 404 | 

### 6.3 Корзина (`/api/cart`)

| # | Кейс | Запрос | Ожидаемый статус |
|---|---|---|---|
| 11 | Добавить товар | `POST /api/cart/add` `{"product_id":1,"quantity":2,"cart":{}}` | 200, `cart:{"1":2}` |
| 12 | Повторное добавление того же товара | `POST /api/cart/add` `{"product_id":1,"quantity":3,"cart":{"1":2}}` | 200, `cart:{"1":5}` (количество суммируется, не дублируется) |
| 13 | Добавление несуществующего товара | `product_id: 99999` | 404 |
| 14 | Некорректное количество (`quantity: 0`) | `POST /api/cart/add` | Ожидается 422
| 15 | Обновить количество | `PUT /api/cart/update` `{"product_id":1,"quantity":10,"cart":{"1":5}}` | 200, `cart:{"1":10}` (значение заменяется, не прибавляется) |
| 16 | Обновление отсутствующего в корзине товара | `product_id` не в `cart` | 404 |
| 17 | Удалить товар | `DELETE /api/cart/remove/1` body `{"cart":{"1":10}}` | 200, `cart:{}` |
| 18 | Удаление отсутствующего в корзине товара | `product_id` не в `cart` | 404 |
| 19 | Получить содержимое корзины | `POST /api/cart` | 200|


---

## 7. Чек-лист для регрессионного прогона

Короткий список для быстрой проверки после любых изменений в бэкенде:

- [ ] `GET /` → 200
- [ ] `GET /api/products` → 200, `total == len(products)`
- [ ] `GET /api/products/1` → 200
- [ ] `GET /api/products/999999` → 404
- [ ] `GET /api/products/category/1` → 200
- [ ] `GET /api/categories` → 200, 4 категории
- [ ] `POST /api/cart/add` (новый товар) → 200, количество корректно
- [ ] `POST /api/cart/add` (тот же товар повторно) → количество суммируется
- [ ] `PUT /api/cart/update` → количество заменяется
- [ ] `DELETE /api/cart/remove/{id}` → товар пропадает из `cart`
- [ ] `GET /health`, `POST /api/cart`, `GET /api/categories/{id}`
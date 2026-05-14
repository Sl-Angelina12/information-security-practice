# Electronic Dean's Office

## Опис
REST API на базі FastAPI + SQLite. 
Практична робота з дисципліни 
"Безпека інформаційних систем".

## Запуск
git clone https://github.com/Sl-Angelina12/information-security-practice.git
cd information-security-practice
docker compose up --build

## Доступ
- API: http://localhost:3010
- Документація (Swagger): http://localhost:3010/docs
- Команда: Ангеліна Слушняк, Анна Левіна, Марія Рубан
- Група: 231он

## Аутентифікація
API підтримує базову аутентифікацію користувачів: реєстрацію та вхід.

### POST /auth/register — Реєстрація користувача
Створює нового користувача в системі.

**Приклад запиту:**
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123",
  "full_name": "Новий Користувач"
}

**Відповідь (201 Created):**
{
  "id": 1,
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "Новий Користувач",
  "is_active": true,
  "created_at": "2026-04-03T18:00:00"
}
**Можливі помилки:**
- 409 Conflict — користувач або email вже існує
- 422 Validation Error — невалідні дані (email або пароль)

### POST /auth/login — Вхід у систему
Перевіряє облікові дані користувача.

**Приклад запиту:**
{
  "username": "admin",
  "password": "Admin123!@#"
}

**Відповідь (200 OK):**
{
  "message": "Вхід успішний",
  "user_id": 1,
  "username": "admin",
  "roles": ["admin"]
}

**Можливі помилки:**
401 Unauthorized — неправильний логін або пароль

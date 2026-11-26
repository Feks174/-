# ТехноСфера — информационная система магазина компьютерной техники

## Стек
Python 3.10+, Tkinter, MySQL, pandas, Pillow.

## Запуск
1. Выполнить `techno_sphere_script.sql` в MySQL.
2. в терминале `pip install -r requirements.txt` или ввести `pip install --upgrade --force-reinstall mysql-connector-python pandas Pillow openpyxl`
3. В `db_import.py` и `main.py` указать свой пароль root в словаре `DB`.
4. Положить Excel-файлы рядом со скриптами.
5. Создать папку `Images` и положить `logo.png` и картинки товаров
6. запустить `python db_import.py`
7. запустить `python main.py`

## Вход
Логины: `admin` (админ), `manager1` / `manager2` (менеджеры), `user1` / `user2` (клиенты). Пароль не нужен.

## Роли
- **Гость** — только каталог.
- **Авторизованный** — каталог с фильтрами, корзина, оформление.
- **Менеджер** — заказы, создание, удаление.
- **Администратор** — плюс редактирование даты и удаление позиций из заказа.
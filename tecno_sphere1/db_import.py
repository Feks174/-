import mysql.connector
import pandas as pd

DB = {"host": "localhost", "user": "root", "password": "пароль"}
conn = mysql.connector.connect(**DB)
cur = conn.cursor(buffered=True)

with open('techno_sphere_script.sql', 'r', encoding='utf-8') as f:
    for q in f.read().split(';'):
        if q.strip():
            cur.execute(q)
cur.execute("USE techno_sphere")

cur.executemany("INSERT INTO roles (role_name) VALUES (%s)",
                [('Администратор',), ('Менеджер',), ('Авторизованный пользователь',)])
roles = {'Администратор': 1, 'Менеджер': 2, 'Авторизованный пользователь': 3}

cur.executemany(
    "INSERT INTO users (last_name, first_name, middle_name, login, role_id) VALUES (%s,%s,%s,%s,%s)",
    [(r['Фамилия'], r['Имя'], r['Отчество'], r['Логин'], roles.get(str(r['Роль']).strip(), 3))
     for _, r in pd.read_excel('Users_import.xlsx').iterrows()])

cur.executemany("INSERT INTO modifications (mod_name) VALUES (%s)",
                [(str(r['Модификация']),) for _, r in pd.read_excel('Modifications_import.xlsx').iterrows()])

for _, r in pd.read_excel('Products_import.xlsx').iterrows():
    cur.execute("SELECT cat_id FROM categories WHERE cat_name=%s", (r['Категория'],))
    res = cur.fetchone()
    if res:
        cid = res[0]
    else:
        cur.execute("INSERT INTO categories (cat_name) VALUES (%s)", (r['Категория'],))
        cid = cur.lastrowid

    cur.execute("SELECT subcat_id FROM subcategories WHERE subcat_name=%s AND cat_id=%s", (r['Подкатегория'], cid))
    res = cur.fetchone()
    if res:
        sid = res[0]
    else:
        cur.execute("INSERT INTO subcategories (cat_id, subcat_name) VALUES (%s,%s)", (cid, r['Подкатегория']))
        sid = cur.lastrowid

    cur.execute(
        "INSERT INTO products (subcat_id, name, manufacturer, descr, specs, price, img) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (sid, r['Наименование товара'], r['Производство'], r['Описание'],
         r['Технические характеристики'], float(r['Цена']), r['Изображение']))

for _, r in pd.read_excel('Stock_Items_import.xlsx').iterrows():
    cur.execute("SELECT prod_id FROM products WHERE name=%s AND manufacturer=%s",
                (r['Наименование товара'], r['Производство']))
    res_p = cur.fetchone()
    if res_p:
        cur.execute("SELECT mod_id FROM modifications WHERE mod_name=%s", (str(r['Модификация']),))
        res_m = cur.fetchone()
        if res_m:
            cur.execute("INSERT INTO stock (prod_id, mod_id, qty) VALUES (%s,%s,%s)",
                        (res_p[0], res_m[0], int(r['Количество доступное для заказа'])))

df_o = pd.read_excel('Orders_import.xlsx')
for num in df_o['Номер заказа'].unique():
    grp = df_o[df_o['Номер заказа'] == num]
    fio = str(grp.iloc[0]['ФИО']).split()
    last_name = fio[0] if len(fio) > 0 else ""
    first_name = fio[1] if len(fio) > 1 else ""

    cur.execute("SELECT user_id FROM users WHERE last_name=%s AND first_name=%s", (last_name, first_name))
    res_u = cur.fetchone()
    uid = res_u[0] if res_u else 1

    dt_val = grp.iloc[0]['Дата заказа']
    cur.execute("INSERT INTO orders (user_id, dt) VALUES (%s, %s)",
                (uid, dt_val.strftime('%Y-%m-%d') if not isinstance(dt_val, str) else dt_val.split()[0]))
    oid = cur.lastrowid

    for _, r in grp.iterrows():
        cur.execute("SELECT prod_id FROM products WHERE name=%s AND manufacturer=%s",
                    (r['Наименование товара'], r['Производство']))
        res_p = cur.fetchone()
        if res_p:
            cur.execute("SELECT mod_id FROM modifications WHERE mod_name=%s", (str(r['Модификация']),))
            res_m = cur.fetchone()
            if res_m:
                cur.execute("SELECT stock_id FROM stock WHERE prod_id=%s AND mod_id=%s",
                            (res_p[0], res_m[0]))
                res_st = cur.fetchone()
                if res_st:
                    cur.execute(
                        "INSERT INTO order_items (order_id, stock_id, qty, price) VALUES (%s,%s,%s,%s)",
                        (oid, res_st[0], int(r['Количество']), float(r['Цена за единицу'])))

conn.commit()
conn.close()
print("Импорт завершен.")
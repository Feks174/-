import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from PIL import Image, ImageTk
from datetime import datetime
import os
from collections import defaultdict

os.chdir(os.path.dirname(os.path.abspath(__file__)))
DB = {"host": "localhost", "user": "root", "password": "пароль", "database": "techno_sphere"}
user, cart, admin_mode, admin_cid = {'id': None, 'role': 0, 'name': 'Гость'}, [], False, None

root = tk.Tk()
try:
    root.iconphoto(True, ImageTk.PhotoImage(Image.open("Images/logo.png")))
except:    pass
root.geometry("950x700")
root.title("ТехноСфера - Управление заказами")
root.option_add("*Font", "Calibri 12")


def db(sql, args=(), fetch=False):
    try:
        conn = mysql.connector.connect(**DB)
        c = conn.cursor()
        c.execute(sql, args)
        res = c.fetchall() if fetch else c.lastrowid
        conn.commit()
        conn.close()
        return res
    except Exception as e:
        messagebox.showerror("Ошибка БД", str(e))
        return [] if fetch else None


def clear(): [w.destroy() for w in root.winfo_children()]


def show_login():
    global admin_mode, admin_cid
    admin_mode, admin_cid = False, None
    clear()
    try:
        img = ImageTk.PhotoImage(Image.open("Images/logo.png").resize((150, 150), Image.LANCZOS))
        lbl = tk.Label(root, image=img)
        lbl.image = img
        lbl.pack(pady=20)
    except:
        tk.Label(root, text="ТехноСфера", font=("Calibri", 26, "bold"), fg="#70B2AF").pack(pady=30)
    tk.Label(root, text="Логин:").pack()
    ent = tk.Entry(root, width=30)
    ent.pack(pady=10)

    def login():
        res = db("SELECT user_id, last_name, first_name, role_id FROM users WHERE login=%s",
                 (ent.get().strip(),), True)
        if res:
            user.update({'id': res[0][0], 'name': f"{res[0][1]} {res[0][2]}", 'role': res[0][3]})
            show_catalog()
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден!")

    tk.Button(root, text="Войти", bg="#70B2AF", fg="white", width=20, command=login).pack(pady=10)
    tk.Button(root, text="Гость", bg="#D2F6E7", width=20,
              command=lambda: [user.update({'id': 1, 'role': 0}), show_catalog()]).pack()


def show_catalog():
    clear()
    top = tk.Frame(root, bg="#D2F6E7")
    top.pack(fill="x")
    tk.Label(top, text=f"{user['name']} ({['Гость', 'Админ', 'Менеджер', 'Клиент'][user['role']]})",
             bg="#D2F6E7").pack(side="left", padx=10)
    tk.Button(top, text="Выйти", bg="#ff8080", fg="white", command=show_login).pack(side="right", padx=5)
    if user['role']:
        tk.Button(top, text="Корзина", bg="#70B2AF", fg="white", command=show_cart).pack(side="right", padx=5)
    if user['role'] in [1, 2]:
        tk.Button(top, text="Заказы", bg="#70B2AF", fg="white", command=show_orders).pack(side="right", padx=5)

    f = tk.Frame(root)
    f.pack(fill="x", pady=10)
    srch, cat, srt = tk.StringVar(), tk.StringVar(value="Все"), tk.StringVar(value="По умолч.")
    if user['role']:
        tk.Entry(f, textvariable=srch, width=15).pack(side="left", padx=5)
        cb_cat = ttk.Combobox(f, textvariable=cat, state="readonly",
                              values=["Все"] + [r[0] for r in db("SELECT cat_name FROM categories", fetch=True)])
        cb_cat.pack(side="left")
        cb_srt = ttk.Combobox(f, textvariable=srt, state="readonly",
                              values=["По умолч.", "Цена ↑", "Цена ↓"])
        cb_srt.pack(side="left")

    canvas = tk.Canvas(root, bg="white")
    scroll = ttk.Scrollbar(root, command=canvas.yview)
    frame = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def load():
        [w.destroy() for w in frame.winfo_children()]
        sql = ("SELECT p.prod_id, p.name, p.manufacturer, p.price, p.img, "
               "(SELECT SUM(qty) FROM stock WHERE prod_id=p.prod_id) "
               "FROM products p JOIN subcategories s ON p.subcat_id=s.subcat_id "
               "JOIN categories c ON s.cat_id=c.cat_id WHERE 1=1")
        args = []
        if user['role']:
            if srch.get():
                sql += " AND (p.name LIKE %s OR p.descr LIKE %s)"
                args += [f"%{srch.get()}%"] * 2
            if cat.get() != "Все":
                sql += " AND c.cat_name=%s"
                args.append(cat.get())
            if srt.get() == "Цена ↑":
                sql += " ORDER BY p.price ASC"
            elif srt.get() == "Цена ↓":
                sql += " ORDER BY p.price DESC"

        for pid, name, manuf, price, img, qty in db(sql, tuple(args), True):
            qty = qty or 0
            bg = "#ff8080" if qty < 3 else "white"
            card = tk.Frame(frame, bg=bg, relief="solid", borderwidth=1)
            card.pack(fill="x", pady=2, padx=5)
            try:
                ph = ImageTk.PhotoImage(Image.open(f"Images/{img}").resize((60, 60), Image.LANCZOS))
                lbl = tk.Label(card, image=ph, bg=bg)
                lbl.image = ph
                lbl.pack(side="left", padx=5)
            except:
                tk.Label(card, text="Нет фото", bg=bg, width=8).pack(side="left", padx=5)
            tk.Label(card, text=f"{manuf} | {name}\nОстаток: {qty} шт.", bg=bg).pack(side="left", padx=10)
            tk.Button(card, text="Подробнее", bg="#70B2AF", fg="white",
                      command=lambda x=pid: open_card(x)).pack(side="right", padx=10)
            tk.Label(card, text=f"{int(price)} р.", bg=bg,
                     font=("Calibri", 14, "bold")).pack(side="right", padx=10)

    if user['role']:
        srch.trace_add("write", lambda *a: load())
        cb_cat.bind("<<ComboboxSelected>>", lambda e: load())
        cb_srt.bind("<<ComboboxSelected>>", lambda e: load())
    load()


def open_card(pid):
    if not user['role']:
        return messagebox.showwarning("Гость", "Авторизуйтесь!")
    win = tk.Toplevel(root)
    win.title("Просмотр товара")
    win.geometry("450x650")
    p = db("SELECT p.name, p.price, p.descr, p.manufacturer, p.specs, c.cat_name "
           "FROM products p JOIN subcategories s ON p.subcat_id=s.subcat_id "
           "JOIN categories c ON s.cat_id=c.cat_id WHERE p.prod_id=%s", (pid,), True)[0]
    for t, fnt, clr in [(p[0], ("Calibri", 16, "bold"), "black"),
                        (f"Категория: {p[5]}", None, "black"),
                        (f"Производитель: {p[3]}", None, "black"),
                        (f"Цена: {int(p[1])} р.", ("Calibri", 14, "bold"), "#70B2AF"),
                        (f"Характеристики: {p[4]}", ("Calibri", 10), "black"),
                        (p[2], ("Calibri", 10), "black")]:
        tk.Label(win, text=t, font=fnt, fg=clr, wraplength=420).pack(pady=5)

    tk.Label(win, text="Модификация:", font=("Calibri", 12, "bold")).pack(pady=5)
    sz, stock = tk.StringVar(), {}
    for s in db("SELECT m.mod_name, st.stock_id, st.qty FROM stock st "
                "JOIN modifications m ON st.mod_id=m.mod_id "
                "WHERE st.prod_id=%s AND st.qty>0", (pid,), True):
        tk.Radiobutton(win, text=f"{s[0]} (ост: {s[2]})", variable=sz, value=str(s[1])).pack(anchor="w")
        stock[str(s[1])] = s[2]

    tk.Label(win, text="Количество:").pack(pady=5)
    qty_ent = tk.Entry(win, width=10)
    qty_ent.pack()

    def add():
        if not sz.get():
            return messagebox.showerror("Ошибка", "Выберите модификацию!")
        try:
            q = int(qty_ent.get())
            if q <= 0:
                raise ValueError
        except:
            return messagebox.showerror("Ошибка", "Введите целое число > 0!")
        if q > stock.get(sz.get(), 0):
            return messagebox.showerror("Ошибка", f"Доступно только {stock.get(sz.get(), 0)} шт.")
        cart.append({'name': p[0], 'stid': int(sz.get()), 'qty': q, 'price': float(p[1])})
        messagebox.showinfo("Успех", "Добавлено в корзину!")
        win.destroy()

    tk.Button(win, text="В корзину", bg="#70B2AF", fg="white", command=add).pack(pady=20)


def show_cart():
    clear()
    tk.Button(root, text="Назад", command=show_catalog).pack(anchor="w", padx=10, pady=10)
    tk.Label(root, text=f"Заказ для ID:{admin_cid}" if admin_mode else "Корзина",
             font=("Calibri", 18, "bold")).pack()
    total = 0
    for i, it in enumerate(cart):
        f = tk.Frame(root)
        f.pack(fill="x", padx=20, pady=2)
        tk.Label(f, text=f"{it['name']} x{it['qty']}").pack(side="left")
        tk.Label(f, text=f"{int(it['price'] * it['qty'])} р.").pack(side="right")
        tk.Button(f, text="X", fg="red",
                  command=lambda x=i: [cart.pop(x), show_cart()]).pack(side="right", padx=10)
        total += it['price'] * it['qty']
    tk.Label(root, text=f"Итого: {int(total)} р.", font=("Calibri", 16, "bold")).pack(pady=20)

    def checkout():
        global admin_mode
        if not cart:
            return messagebox.showwarning("Внимание", "Корзина пуста!")
        need = defaultdict(int)
        for it in cart:
            need[it['stid']] += it['qty']
        for stid, q in need.items():
            avail = db("SELECT qty FROM stock WHERE stock_id=%s", (stid,), True)[0][0]
            if avail < q:
                return messagebox.showerror("Ошибка",
                                            f"Товара не хватает! Доступно: {avail}, в корзине: {q}")
        oid = db("INSERT INTO orders (user_id, dt) VALUES (%s,%s)",
                 (user['id'] if not admin_mode else admin_cid, datetime.now().strftime("%Y-%m-%d")))
        if oid:
            for it in cart:
                db("INSERT INTO order_items (order_id, stock_id, qty, price) VALUES (%s,%s,%s,%s)",
                   (oid, it['stid'], it['qty'], it['price']))
            for stid, q in need.items():
                db("UPDATE stock SET qty = qty - %s WHERE stock_id=%s", (q, stid))
            cart.clear()
            messagebox.showinfo("Успех", "Заказ оформлен!")
            admin_mode = False
            show_catalog()

    tk.Button(root, text="Подтвердить", bg="#70B2AF", fg="white", command=checkout).pack()


def show_orders():
    if user['role'] not in [1, 2]:
        return messagebox.showerror("Доступ", "Нет прав!")
    clear()
    top = tk.Frame(root, bg="#D2F6E7")
    top.pack(fill="x")
    tk.Button(top, text="Назад", command=show_catalog).pack(side="left", padx=10)

    def new_order():
        win = tk.Toplevel(root)
        win.title("Выбор клиента")
        win.geometry("300x400")
        u_var = tk.StringVar()
        for u in db("SELECT user_id, last_name, first_name FROM users WHERE role_id=3", fetch=True):
            tk.Radiobutton(win, text=f"{u[1]} {u[2]}", variable=u_var, value=u[0]).pack(anchor="w")

        def select():
            global admin_mode, admin_cid
            if not u_var.get():
                return messagebox.showerror("Ошибка", "Выберите клиента!")
            admin_mode, admin_cid = True, int(u_var.get())
            cart.clear()
            win.destroy()
            show_catalog()

        tk.Button(win, text="Выбрать", command=select).pack(pady=10)

    tk.Button(top, text="+ Заказ", bg="#70B2AF", fg="white", command=new_order).pack(side="right", padx=10)

    tree = ttk.Treeview(root, columns=("id", "dt", "fio"), show="headings")
    for c in ["id", "dt", "fio"]:
        tree.heading(c, text=c.upper())
    tree.pack(fill="both", expand=True, padx=20, pady=10)
    for r in db("SELECT o.order_id, o.dt, CONCAT(u.last_name, ' ', u.first_name) "
                "FROM orders o JOIN users u ON o.user_id=u.user_id "
                "ORDER BY o.order_id DESC", fetch=True):
        tree.insert("", "end", values=r)

    def view():
        sel = tree.selection()
        if not sel:
            return messagebox.showwarning("Внимание", "Выберите заказ!")
        oid = tree.item(sel[0])['values'][0]
        win = tk.Toplevel(root)
        win.geometry("700x450")
        tk.Label(win, text=f"Состав заказа #{oid}", font=("Calibri", 14, "bold")).pack(pady=5)
        it_tree = ttk.Treeview(win, columns=("item_id", "name", "mod", "qty", "price"),
                               show="headings")
        for c in ["item_id", "name", "mod", "qty", "price"]:
            it_tree.heading(c, text=c.capitalize())
        it_tree.pack(fill="both", expand=True)
        total = 0
        for item in db("SELECT i.item_id, p.name, m.mod_name, i.qty, i.price "
                       "FROM order_items i JOIN stock st ON i.stock_id=st.stock_id "
                       "JOIN products p ON st.prod_id=p.prod_id "
                       "JOIN modifications m ON st.mod_id=m.mod_id "
                       "WHERE i.order_id=%s", (oid,), True):
            it_tree.insert("", "end", values=item)
            total += item[3] * item[4]
        tk.Label(win, text=f"Итого: {int(total)} р.",
                 font=("Calibri", 14, "bold")).pack(pady=5)

        def del_item():
            if user['role'] != 1:
                return messagebox.showerror("Доступ", "Только администратор!")
            sel2 = it_tree.selection()
            if not sel2:
                return messagebox.showwarning("Внимание", "Выберите позицию!")
            iid = it_tree.item(sel2[0])['values'][0]
            row = db("SELECT stock_id, qty FROM order_items WHERE item_id=%s", (iid,), True)[0]
            db("UPDATE stock SET qty = qty + %s WHERE stock_id=%s", (row[1], row[0]))
            db("DELETE FROM order_items WHERE item_id=%s", (iid,))
            win.destroy()
            view()

        if user['role'] == 1:
            tk.Button(win, text="Удалить позицию", bg="#ff8080", fg="white",
                      command=del_item).pack(pady=5)

    def delete():
        sel = tree.selection()
        if sel and messagebox.askyesno("Удалить?", "Удалить заказ? Товары вернутся на склад."):
            oid = tree.item(sel[0])['values'][0]
            for stid, qty in db("SELECT stock_id, qty FROM order_items WHERE order_id=%s", (oid,), True):
                db("UPDATE stock SET qty = qty + %s WHERE stock_id=%s", (qty, stid))
            db("DELETE FROM order_items WHERE order_id=%s", (oid,))
            db("DELETE FROM orders WHERE order_id=%s", (oid,))
            show_orders()

    def edit_date():
        if user['role'] != 1:
            return messagebox.showerror("Доступ", "Только администратор!")
        sel = tree.selection()
        if not sel:
            return
        oid = tree.item(sel[0])['values'][0]
        old = tree.item(sel[0])['values'][1]
        new = simpledialog.askstring("Дата", "ГГГГ-ММ-ДД:", initialvalue=old)
        if new:
            try:
                datetime.strptime(new, '%Y-%m-%d')
                db("UPDATE orders SET dt=%s WHERE order_id=%s", (new, oid))
                show_orders()
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты!")

    tk.Button(top, text="Просмотр", command=view).pack(side="left", padx=5)
    tk.Button(top, text="Удалить", command=delete).pack(side="left", padx=5)
    if user['role'] == 1:
        tk.Button(top, text="Изм. дату", command=edit_date).pack(side="left", padx=5)
    tree.bind("<Double-1>", lambda e: view())


if __name__ == "__main__":
    show_login()
    root.mainloop()
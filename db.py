import sqlite3
"""
saves all the users of bot in a database for advance purposes

"""

class UsersData:


    def __init__(self, dbname = "users.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)


    def setup(self):
        statement1 = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, chatid INTEGER UNIQUE, balance INTEGER DEFAULT 1000 )"
        self.conn.execute(statement1)
        self.conn.commit()


    def add_user(self, username_):
        statement = "INSERT OR IGNORE INTO users (chatid) VALUES (?)"
        args = (username_, )
        self.conn.execute(statement, args)
        self.conn.commit()
    

    def update_balance(self, amount, userid):
        statement = "UPDATE users SET balance = ? WHERE chatid = ?"
        args = (amount, userid)
        self.conn.execute(statement, args)
        self.conn.commit()
        
        
        
    def get_balance(self, owner):
        statement = "SELECT balance FROM users WHERE chatid = ?"
        args = (owner,)
        cursor = self.conn.execute(statement, args)
        result = cursor.fetchone()
        if result:
            return result[0]
        return None


    def get_users(self):
        statement = "SELECT chatid FROM users"
        return [x[0] for x in self.conn.execute(statement)]
    
    
class Products:
    def __init__(self, dbname = "products.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)


    def setup(self):
        statement1 = """CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, 
                        productid INTEGER UNIQUE, name TEXT, price INTEGER,
                        location TEXT, description TEXT, type TEXT )"""
                        
        self.conn.execute(statement1)
        self.conn.commit()
        
        
    def add_product(self, productid, name, price, location, description, type):
        statement = """INSERT OR IGNORE INTO products (productid, name, price, location, description, type) VALUES (?, ?, ?, ?, ?, ?)"""
        args = (productid, name, price, location, description,type)
        self.conn.execute(statement, args)
        self.conn.commit()
    
    
    def delete_product(self, productid):
        statement = "DELETE FROM products WHERE productid = ?"
        args = (productid,)
        self.conn.execute(statement, args)
        self.conn.commit()
        
        
    def update_description(self, productid, description):
        statement = "UPDATE products SET description = ? WHERE productid = ?"
        args = (description, productid)
        self.conn.execute(statement, args)
        self.conn.commit()
        
        
    def update_price(self, productid, price):
        statement = "UPDATE products SET price = ? WHERE productid = ?"
        args = (price, productid)
        self.conn.execute(statement, args)
        self.conn.commit()
        
    
    def get_all_products(self):
        statement = "SELECT productid, name, price,  location, description , type FROM products"
        return [x for x in self.conn.execute(statement)]
    
    
    def get_product(self, productid):
        statement = "SELECT productid, name, price,  location, description , type FROM products WHERE productid = ?"
        args = (productid, )
        return [x for x in self.conn.execute(statement, args)]
        
        

class Orders(Products):
    def __init__(self, dbname="products.db"):
        super().__init__(dbname)
    
    def setup(self):
        super().setup()
        statement = """CREATE TABLE IF NOT EXISTS orders (
                            orderid INTEGER PRIMARY KEY AUTOINCREMENT, 
                            userid INTEGER,
                            productid INTEGER,
                            order_date TEXT,
                            paid BOOLEAN DEFAULT FALSE,
                            ordername TEXT DEFAULT NULL,
                            FOREIGN KEY(productid) REFERENCES products(productid))"""
        self.conn.execute(statement)
        self.conn.commit()

    def add_order(self, userid, productid, order_date, paid=False, ordername=None):
        statement = """INSERT INTO orders 
                       (userid, productid, order_date, paid, ordername) 
                       VALUES (?, ?, ?, ?, ?)"""
        args = (userid, productid, order_date, paid, ordername)
        self.conn.execute(statement, args)
        self.conn.commit()

    def delete_order(self, orderid):
        statement = "DELETE FROM orders WHERE orderid = ?"
        args = (orderid,)
        self.conn.execute(statement, args)
        self.conn.commit()

    def update_order(self, orderid, userid, paid=None, ordername=None):
        statement = "UPDATE orders SET "
        args = []
        if paid is not None:
            statement += "paid = ?, "
            args.append(paid)
        if ordername is not None:
            statement += "ordername = ?, "
            args.append(ordername)
        
        # Remove the last comma and add the WHERE clause
        statement = statement.rstrip(", ") + " WHERE orderid = ? AND userid = ?"
        args.append(orderid)
        args.append(userid)
        
        self.conn.execute(statement, tuple(args))
        self.conn.commit()

    def get_all_orders(self):
        statement = """SELECT orders.orderid, orders.userid, products.name, products.price, 
                              orders.order_date, orders.paid, orders.ordername
                       FROM orders
                       JOIN products ON orders.productid = products.productid"""
        return [x for x in self.conn.execute(statement)]

    def get_orders_by_user(self, userid):
        statement = """SELECT orders.orderid, products.name, products.price, 
                              orders.order_date, orders.paid, orders.ordername
                       FROM orders
                       JOIN products ON orders.productid = products.productid
                       WHERE orders.userid = ?"""
        args = (userid,)
        return [x for x in self.conn.execute(statement, args)]

    def get_order(self, orderid):
        statement = """SELECT orders.orderid, orders.userid, products.name, products.price, 
                              orders.order_date, orders.paid, orders.ordername
                       FROM orders
                       JOIN products ON orders.productid = products.productid
                       WHERE orders.orderid = ?"""
        args = (orderid,)
        return [x for x in self.conn.execute(statement, args)]

# Usage example
if __name__ == "__main__":
    prod_db = Products()
    prod_db.setup()
    prod_db.add_product(1, "Product1", 100, "Location1", "Description1", "Type1")
    
    orders_db = Orders()
    orders_db.setup()
    orders_db.add_order(42, 1, "2024-07-31")  # Adding an order with default paid=False and ordername=None

    print("All Orders:")
    print(orders_db.get_all_orders())

    print("\nUpdating Order:")
    orders_db.update_order(1, 42, paid=True, ordername="First Order")  # Updating based on orderid and userid

    print("\nAll Orders After Update:")
    print(orders_db.get_all_orders())
import datetime
import sqlite3 as sq

class DataBase:
    def __init__(self, filename):
        self.filename = filename
        self.items = None
        self.load()

    def load(self):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS ALLDATA (
                    ID  TEXT NOT NULL, 
                    NAME  TEXT NOT NULL,
                    COUNT INTEGER,
                    COST  REAL,
                    IMAGE  TEXT NOT NULL)''')
        self.conn.close()

    def ReturnAllItems(self):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.items = self.conn.execute('''SELECT ID, NAME, COUNT, COST, IMAGE FROM ALLDATA''').fetchall()
        self.conn.close()
        return self.items

    def validate_item_count(self, item_id, new_item_numbers, action='Add'):
        check_negative = False
        if action=='Delete': new_item_numbers *= (-1)

        self.conn = sq.connect(self.filename)
        current_count = self.conn.execute('''SELECT COUNT FROM ALLDATA WHERE ID==?''',(item_id,)).fetchone()
        self.conn.close()
        up_count = current_count[0] + new_item_numbers

        if up_count < 0: check_negative = True

        return up_count, check_negative

    def update_item_count(self, item_id, up_count):

        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''UPDATE ALLDATA SET COUNT = ? WHERE ID==?''', (up_count, item_id))
        self.conn.close()

        return 

    def check_item_eligibility(self, item_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            ID_exist = self.conn.execute('''SELECT EXISTS(SELECT 1 FROM ALLDATA WHERE ID==?)''',(item_id,)).fetchone()[0]
        self.conn.close()

        return ID_exist
    
    def add_new_items(self, item_list):
        self.conn = sq.connect(self.filename)

        with self.conn:
            self.conn.executemany('''INSERT INTO ALLDATA VALUES (?, ?, ?, ?, ?)''', item_list )
        
        self.conn.close()
        return

    def id_list(self):
        self.conn = sq.connect(self.filename)
        item_ids = self.conn.execute('''SELECT * FROM ALLDATA''').fetchall()
        self.conn.close()
        #return sorted([id_[0] for id_ in item_ids])
        return [(id_[0], id_[0]) for id_ in item_ids] + [(id_[1],id_[0]) for id_ in item_ids]

    def get_item_properties(self, item_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            Item_Properties = self.conn.execute('''SELECT ID, NAME, COUNT, COST, IMAGE FROM ALLDATA WHERE ID==?''',(item_id,)).fetchone()
        self.conn.close()
        return Item_Properties

    def UpdateNewItemDetails(self, partial_item):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''UPDATE ALLDATA SET NAME = ?, COUNT = ?, COST = ?, IMAGE = ? WHERE ID==?''', partial_item)
        self.conn.close()
        return 

    def DeleteItem(self, item_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''DELETE FROM ALLDATA WHERE ID==?''', (item_id,))
        self.conn.close()
        return 

    def UpdateCheckoutItemStock(self, partial_item):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.executemany('''UPDATE ALLDATA SET COUNT = COUNT - ? WHERE ID==?''', partial_item)
        self.conn.close()
        return 

class CustomerDataBase:
    def __init__(self, filename):
        self.filename = filename
        self.items = None
        self.load()

    def load(self):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS CUSTOMERDATA (
                    ID  TEXT NOT NULL, 
                    NAME  TEXT NOT NULL,
                    EMAIL  TEXT,
                    TOTAL_VISIT INTEGER,
                    COMMENT  TEXT)''')
        self.conn.close()

    def update_visit_count(self, customer_id):

        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''UPDATE CUSTOMERDATA SET TOTAL_VISIT = TOTAL_VISIT + 1 WHERE ID==?''', (customer_id,))
        self.conn.close()

        return 

    def check_customer_exists(self, customer_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            ID_exist = self.conn.execute('''SELECT EXISTS(SELECT 1 FROM CUSTOMERDATA WHERE ID==?)''',(customer_id,)).fetchone()[0]
        self.conn.close()

        return ID_exist
    
    def add_new_customer(self, customer_list):
        self.conn = sq.connect(self.filename)

        with self.conn:
            self.conn.execute('''INSERT INTO CUSTOMERDATA VALUES (?, ?, ?, ?, ?)''', customer_list)
        
        self.conn.close()
        return

    def id_list(self):
        self.conn = sq.connect(self.filename)
        item_ids = self.conn.execute('''SELECT * FROM CUSTOMERDATA''').fetchall()
        self.conn.close()
        #return sorted([id_[0] for id_ in item_ids])
        return [(id_[0], id_[0]) for id_ in item_ids] + [(id_[1],id_[0]) for id_ in item_ids]

    def DeleteCustomer(self, item_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''DELETE FROM CUSTOMERDATA WHERE ID==?''', (item_id,))
        self.conn.close()
        return 

    def get_customer_properties(self, customer_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            Item_Properties = self.conn.execute('''SELECT * FROM CUSTOMERDATA WHERE ID==?''',(customer_id,)).fetchone()
        self.conn.close()
        return Item_Properties

    def update_customer_details(self, partial_item):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''UPDATE CUSTOMERDATA SET NAME = ?, EMAIL = ?, COMMENT = ? WHERE ID==?''', partial_item)
        self.conn.close()
        return 


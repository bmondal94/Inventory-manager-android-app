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

    def update_item_count(self, item_id, new_item_numbers, action='Add'):
        self.conn = sq.connect(self.filename)
        new_item_numbers = int(new_item_numbers) if new_item_numbers is not None and new_item_numbers.strip() else 0
        if action=='Add':
            with self.conn:
                self.conn.execute('''UPDATE ALLDATA SET COUNT = COUNT + ? WHERE ID==?''', (new_item_numbers,item_id))
        elif action=='Delete':
            with self.conn:
                self.conn.execute('''UPDATE ALLDATA SET COUNT = COUNT - ? WHERE ID==?''', (new_item_numbers,item_id))
        else:
            pass

        with self.conn:
            current_count = self.conn.execute('''SELECT COUNT FROM ALLDATA WHERE ID==?''',(item_id,)).fetchone()
        
        self.conn.close()

        return current_count[0]

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

    def get_item_properties(self, item_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            Item_Properties = self.conn.execute('''SELECT ID, NAME, COUNT, COST, IMAGE FROM ALLDATA WHERE ID==?''',(item_id,)).fetchone()
        self.conn.close()
        return Item_Properties

    def UpdateNewCost(self, item_id, item_cost):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''UPDATE ALLDATA SET COST = ? WHERE ID==?''', (item_cost,item_id))
        self.conn.close()
        return 

    def DeleteItem(self, item_id):
        self.conn = sq.connect(self.filename)
        with self.conn:
            self.conn.execute('''DELETE FROM ALLDATA WHERE ID==?''', (item_id,))
        self.conn.close()
        return 


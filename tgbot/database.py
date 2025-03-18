import datetime
import sqlite3

DB_PATH = "database.db"  # Путь к файлу базы данных


def create_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS payments_table (
        user_id INTEGER PRIMARY KEY,
        end_payment_date TEXT NOT NULL
    )    
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS date_tranning (
        user_id INTEGER PRIMARY KEY,
        end_tranning_date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_payment(user_id):
    end_payment_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    conn=sqlite3.connect(DB_PATH)
    cur=conn.cursor()
    cur.execute('''
    INSERT INTO payments_table (user_id, end_payment_date)
    VALUES (?, ?)
    ON CONFLICT (user_id) DO UPDATE SET end_payment_date = ?
    ''',(user_id, end_payment_date, end_payment_date))
    conn.commit()
    conn.close()

def check_payment(user_id):
    conn=sqlite3.connect('database.db')
    cur=conn.cursor()
    cur.execute('''
    SELECT end_payment_date 
    FROM payments_table
    WHERE user_id = ?''', (user_id,))
    result=cur.fetchone()
    conn.close()
    if result:
        try:
            end_payment_date = datetime.datetime.strptime(result[0], '%Y-%m-%d')
            return end_payment_date > datetime.datetime.now()
        except ValueError:
            return False
    return False

def add_date_tranning(user_id):
    end_tranning_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO date_tranning (user_id, end_tranning_date)
        VALUES (?, ?)
        ON CONFLICT (user_id) DO UPDATE SET end_tranning_date = ?
        ''', (user_id, end_tranning_date, end_tranning_date))
    conn.commit()
    conn.close()

def check_date_tranning(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    SELECT end_tranning_date 
    FROM date_tranning
    WHERE user_id = ?''', (user_id,))
    result = cur.fetchone()
    if result:
        try:
            end_tranning_date = datetime.datetime.strptime(result[0], '%Y-%m-%d')
            now = datetime.datetime.now()
            if (now - end_tranning_date).days < 30:
                return False
        except ValueError:
            return False
    return True

if __name__ == "__main__":
    create_db()






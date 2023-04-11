import sqlite3 as sq


def creating():
    with sq.connect('DateBase.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_text TEXT,
        grups INTEGER DEFAULT '',
        user_photo BLOB
        )
        ''')

def add_user(user_id):
    with sq.connect('DateBase.db') as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        con.commit()


def edit_user_text(user_text, user_id):
    with sq.connect('DateBase.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE users SET user_text=? WHERE user_id=?", (user_text, user_id,))
        con.commit()

def add_groupss(group_id, user_id):
    with sq.connect('DateBase.db') as con:
        cur = con.cursor()
        cur.execute('SELECT grups FROM users WHERE user_id=?', (user_id,))
        groups = cur.fetchone()[0]
        if groups:
            groups_list = str(groups).split(',')
        else:
            groups_list = []
        if group_id in groups_list:
            print('Group already exists')
            return
        groups_list.append(group_id)
        cur.execute('UPDATE users SET grups=? WHERE user_id=?', (','.join(groups_list), user_id))
        con.commit()

def delete_groups(group_id, user_id):
    with sq.connect('DateBase.db') as con:
        cur = con.cursor()
        cur.execute('SELECT grups FROM users WHERE user_id=?', (user_id,))
        groups = cur.fetchone()[0]
        if groups:
            groups_list = str(groups).split(',')
        else:
            groups_list = []
        if group_id not in groups_list:
            print('Group already exists')
            return
        groups_list.remove(group_id)
        cur.execute('UPDATE users SET grups=? WHERE user_id=?', (','.join(groups_list), user_id))
        con.commit()

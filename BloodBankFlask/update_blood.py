import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Donor ID jiska blood group update karna hai
donor_id = 3

# Jo blood group dalna hai
new_blood_group = 'O-'

# Update command
cursor.execute("UPDATE users SET blood_group = ? WHERE id = ?", (new_blood_group, donor_id))
conn.commit()

# Confirm update
cursor.execute("SELECT * FROM users WHERE id = ?", (donor_id,))
print("Updated Row:", cursor.fetchone())

conn.close()

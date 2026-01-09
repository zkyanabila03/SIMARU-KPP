import sqlite3
from datetime import datetime
import pandas as pd
import csv
import os

class Database:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabel Users - DITAMBAHKAN UNIQUE constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Tabel Ruangan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                capacity INTEGER,
                status TEXT DEFAULT 'tersedia'
            )
        ''')
        
        # Tabel Aset Elektronik
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'tersedia',
                condition TEXT DEFAULT 'baik'
            )
        ''')
        
        # Tabel Kendaraan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                plate_number TEXT,
                status TEXT DEFAULT 'tersedia'
            )
        ''')
        
        # Tabel Booking Ruangan - LANGSUNG DISETUJUI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                room_id INTEGER,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                purpose TEXT,
                requester_name TEXT,
                status TEXT DEFAULT 'disetujui',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
        ''')
        
        # Tabel Booking Aset - LANGSUNG DISETUJUI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                asset_id INTEGER,
                borrow_date TEXT NOT NULL,
                return_date TEXT NOT NULL,
                purpose TEXT,
                requester_name TEXT,
                status TEXT DEFAULT 'disetujui',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (asset_id) REFERENCES assets (id)
            )
        ''')
        
        # Tabel Booking Kendaraan - LANGSUNG DISETUJUI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                vehicle_id INTEGER,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                destination TEXT,
                purpose TEXT,
                requester_name TEXT,
                status TEXT DEFAULT 'disetujui',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert data awal
        self.insert_initial_data()
        # Load users dari CSV
        self.load_users_from_csv("users.csv")
    
    def insert_initial_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cek apakah sudah ada data ruangan
        cursor.execute("SELECT COUNT(*) FROM rooms")
        if cursor.fetchone()[0] == 0:
            rooms = [
                ('Ruang Rapat', 10),
                ('Ruang Konsul 1', 7),
                ('Ruang Konsul 2', 8),
                ('Ruang Konsul 3', 9),
                ('Studio', 10),
                ('Aula', 20),
            ]
            cursor.executemany("INSERT INTO rooms (name, capacity) VALUES (?, ?)", rooms)
        
        # Cek apakah sudah ada data aset
        cursor.execute("SELECT COUNT(*) FROM assets")
        if cursor.fetchone()[0] == 0:
            assets = [
                ('Laptop Dell Latitude 1', 'Laptop'),
                ('Laptop Dell Latitude 2', 'Laptop'),
                ('Laptop HP ProBook 1', 'Laptop'),
                ('Laptop HP ProBook 2', 'Laptop'),
                ('Laptop Lenovo ThinkPad 1', 'Laptop'),
                ('Laptop Lenovo ThinkPad 2', 'Laptop'),
            ]
            cursor.executemany("INSERT INTO assets (name, type) VALUES (?, ?)", assets)
        
        # Cek apakah sudah ada data kendaraan
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        if cursor.fetchone()[0] == 0:
            vehicles = [
                ('Toyota Avanza 1', 'Mobil', 'L 1234 AB'),
                ('Toyota Avanza 2', 'Mobil', 'L 5678 CD'),
                ('Honda Mobilio', 'Mobil', 'L 9012 EF'),
                ("Toyota Innova Reborn", "Mobil", "L 3456 GH"),
                ("Suzuki Ertiga", "Mobil", "L 3344 MN")
            ]
            cursor.executemany("INSERT INTO vehicles (name, type, plate_number) VALUES (?, ?, ?)", vehicles)
        
        conn.commit()
        conn.close()
    
    def debug_users(self):
        """Fungsi debug untuk mengecek semua user di database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, name, role FROM users ORDER BY username")
        users = cursor.fetchall()
        conn.close()
        
        print("\n" + "="*50)
        print("DEBUG: USERS IN DATABASE")
        print("="*50)
        for user in users:
            print(f"ID: {user[0]}, Username: '{user[1]}', Name: {user[2]}, Role: {user[3]}")
        print(f"Total users: {len(users)}")
        print("="*50 + "\n")
        
        return users
    
    def debug_verify_user(self, username, password):
        """Debug khusus untuk verifikasi user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        username = str(username).strip()
        password = str(password).strip()
        
        print(f"\nDEBUG verify_user:")
        print(f"  Input username: '{username}' (length: {len(username)})")
        print(f"  Input password: '{password}' (length: {len(password)})")
        
        # Cari exact match
        cursor.execute(
            "SELECT id, username, name, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        
        # Debug: cari partial match
        cursor.execute("SELECT username FROM users WHERE username LIKE ?", (f"%{username}%",))
        similar = cursor.fetchall()
        print(f"  Similar usernames in DB: {similar}")
        
        conn.close()
        
        if user:
            print(f"  RESULT: FOUND - {user}")
            return {
                'id': user[0],
                'username': user[1],
                'name': user[2],
                'role': user[3]
            }
        else:
            print(f"  RESULT: NOT FOUND")
            return None
    
    def load_users_from_csv(self, csv_file="users.csv"):
        """Load users dari file CSV - DIPERBAIKI dengan membaca sebagai string"""
        try:
            if not os.path.exists(csv_file):
                print(f"File {csv_file} tidak ditemukan")
                return False
            
            # PERBAIKAN DI SINI: Baca CSV dengan dtype=str untuk menjaga leading zeros
            df = pd.read_csv(csv_file, dtype=str)
            
            # Pastikan semua data menjadi string
            df['USERNAME'] = df['USERNAME'].astype(str).str.strip()
            df['PASSWORD'] = df['PASSWORD'].astype(str).str.strip()
            df['NAMA'] = df['NAMA'].astype(str).str.strip()
            
            # Konfirmasi data
            print(f"Contoh data dari CSV: {df['USERNAME'].head().tolist()}")
            
            conn = self.get_connection()
            cursor = conn.cursor()
        
            # Hapus semua user (kecuali admin) untuk menghindari duplikat
            cursor.execute("DELETE FROM users WHERE username != 'admin'")
            
            # Insert user baru dari CSV
            success_count = 0
            for _, row in df.iterrows():
                try:
                    username = str(row['USERNAME']).strip()
                    password = str(row['PASSWORD']).strip()
                    name = str(row['NAMA']).strip()
                    
                    if username and password and name:
                        # Insert atau replace user
                        cursor.execute(
                            "INSERT OR REPLACE INTO users (username, password, name, role) VALUES (?, ?, ?, 'user')",
                            (username, password, name)
                        )
                        success_count += 1
                except Exception as e:
                    print(f"Error inserting user {username}: {e}")
            
            # Tambahkan admin default jika belum ada
            cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, 'admin')",
                    ('admin', 'admin123', 'Administrator')
                )
                success_count += 1
            
            conn.commit()
            
            # Verifikasi data yang sudah dimasukkan
            cursor.execute("SELECT username FROM users WHERE username LIKE '0%' LIMIT 5")
            sample_users = cursor.fetchall()
            print(f"Sample users di database: {sample_users}")
            
            conn.close()
            
            print(f"Successfully loaded {success_count} users from {csv_file}")
            return True
            
        except Exception as e:
            print(f"Error loading users from CSV: {e}")
            return False
        
    def verify_user(self, username, password):
        """Verifikasi login user - DIPERBAIKI dengan handling leading zeros"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # PERBAIKAN: Pastikan input menjadi string dan strip whitespace
        username = str(username).strip()
        password = str(password).strip()
        
        print(f"DEBUG login attempt - Username: '{username}', Password: '{password}'")
        print(f"DEBUG username length: {len(username)}")
        
        # Debug: tampilkan user dengan angka 0 di depan
        cursor.execute("SELECT username FROM users WHERE username LIKE '0%' LIMIT 5")
        zero_users = cursor.fetchall()
        print(f"DEBUG users dengan leading zero: {zero_users}")
        
        # Cari user dengan username dan password
        cursor.execute(
            "SELECT id, username, name, role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            print(f"DEBUG login SUCCESS for user: {user}")
            return {
                'id': user[0],
                'username': user[1],
                'name': user[2],
                'role': user[3]
            }
        
        print(f"DEBUG login FAILED for username: '{username}'")
        return None
    
    def get_users_by_division(self, division):
        """Ambil daftar user berdasarkan divisi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name FROM users WHERE username = ? ORDER BY name",
            (division,)
        )
        users = cursor.fetchall()
        conn.close()
        return users
    
    def get_all_users(self):
        """Ambil semua user untuk admin"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM users ORDER BY username, name", conn)
        conn.close()
        return df
    
    def add_user(self, username, password, name, role='user'):
        """Tambah user baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)",
                (username, password, name, role)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_user(self, user_id, username, password, name, role):
        """Update user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET username=?, password=?, name=?, role=? WHERE id=?",
                (username, password, name, role, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_user(self, user_id):
        """Hapus user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_all_rooms(self):
        """Ambil semua ruangan"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM rooms", conn)
        conn.close()
        return df
    
    def get_available_rooms(self, date, start_time, end_time):
        """Cek ruangan yang tersedia"""
        conn = self.get_connection()
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT r.* FROM rooms r
            WHERE r.id NOT IN (
                SELECT room_id FROM room_bookings
                WHERE date = ? 
                AND status = 'disetujui'
                AND (
                    (start_time <= ? AND end_time > ?) OR
                    (start_time < ? AND end_time >= ?) OR
                    (start_time >= ? AND end_time <= ?)
                )
            )
        """, (date, start_time, start_time, end_time, end_time, start_time, end_time))
    
        rooms = cursor.fetchall()
        conn.close()
        return rooms
    
    def add_room_booking(self, user_id, room_id, date, start_time, end_time, purpose, requester_name=None):
        """Tambah booking ruangan - LANGSUNG DISETUJUI dengan nama pemesan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Jika requester_name tidak diberikan, ambil dari tabel users
            if not requester_name:
                cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
                user_result = cursor.fetchone()
                requester_name = user_result[0] if user_result else "Tidak Diketahui"
            
            cursor.execute("""
                INSERT INTO room_bookings (user_id, room_id, date, start_time, end_time, purpose, requester_name, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'disetujui')
            """, (user_id, room_id, date, start_time, end_time, purpose, requester_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding room booking: {e}")
            return False
    
    def get_all_assets(self):
        """Ambil semua aset"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM assets", conn)
        conn.close()
        return df
    
    def get_available_assets(self, borrow_date, return_date, asset_type=None):
        """Cek aset yang tersedia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT a.* FROM assets a
            WHERE a.condition = 'baik'
        """
        params = []
        
        if asset_type:
            query += " AND a.type = ?"
            params.append(asset_type)
        
        query += """
            AND a.id NOT IN (
                SELECT asset_id FROM asset_bookings
                WHERE status = 'disetujui'
                AND (
                    (borrow_date <= ? AND return_date >= ?) OR
                    (borrow_date <= ? AND return_date >= ?) OR
                    (borrow_date >= ? AND return_date <= ?)
                )
            )
        """
        params.extend([return_date, borrow_date, borrow_date, return_date, borrow_date, return_date])
        
        cursor.execute(query, params)
        assets = cursor.fetchall()
        conn.close()
        return assets
    
    def add_asset_booking(self, user_id, asset_id, borrow_date, return_date, purpose, requester_name=None):
        """Tambah booking aset - LANGSUNG DISETUJUI dengan nama pemesan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Jika requester_name tidak diberikan, ambil dari tabel users
            if not requester_name:
                cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
                user_result = cursor.fetchone()
                requester_name = user_result[0] if user_result else "Tidak Diketahui"
            
            cursor.execute("""
                INSERT INTO asset_bookings (user_id, asset_id, borrow_date, return_date, purpose, requester_name, status)
                VALUES (?, ?, ?, ?, ?, ?, 'disetujui')
            """, (user_id, asset_id, borrow_date, return_date, purpose, requester_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding asset booking: {e}")
            return False
    
    def get_all_vehicles(self):
        """Ambil semua kendaraan"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)
        conn.close()
        return df
    
    def get_available_vehicles(self, date_str, start_time, end_time, vehicle_type=None):
        """Cek kendaraan yang tersedia berdasarkan tanggal dan jam"""
        conn = self.get_connection()
        cursor = conn.cursor()
    
        query = """
            SELECT v.* FROM vehicles v
            WHERE v.status = 'tersedia'
        """
        params = []
    
        if vehicle_type:
            query += " AND v.type = ?"
            params.append(vehicle_type)
    
        query += """
            AND v.id NOT IN (
                SELECT vehicle_id FROM vehicle_bookings
                WHERE start_date = ? 
                AND status = 'disetujui'
                AND (
                    (start_time <= ? AND end_time > ?) OR
                    (start_time < ? AND end_time >= ?) OR
                    (start_time >= ? AND end_time <= ?)
                )
            )
        """
        params.extend([date_str, end_time, start_time, end_time, start_time, start_time, end_time])
    
        cursor.execute(query, params)
        vehicles = cursor.fetchall()
        conn.close()
        return vehicles
    
    def add_vehicle_booking(self, user_id, vehicle_id, start_date, end_date, start_time, end_time, destination, purpose, requester_name=None):
        """Tambah booking kendaraan - LANGSUNG DISETUJUI dengan nama pemesan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Jika requester_name tidak diberikan, ambil dari tabel users
            if not requester_name:
                cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
                user_result = cursor.fetchone()
                requester_name = user_result[0] if user_result else "Tidak Diketahui"
            
            cursor.execute("""
                INSERT INTO vehicle_bookings (user_id, vehicle_id, start_date, end_date, start_time, end_time, destination, purpose, requester_name, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'disetujui')
            """, (user_id, vehicle_id, start_date, end_date, start_time, end_time, destination, purpose, requester_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding vehicle booking: {e}")
            return False
        
    def get_user_bookings(self, user_id):
        """Ambil semua booking user"""
        conn = self.get_connection()
        
        room_df = pd.read_sql_query("""
            SELECT rb.*, r.name as item_name, 'Ruangan' as type
            FROM room_bookings rb
            JOIN rooms r ON rb.room_id = r.id
            WHERE rb.user_id = ?
            ORDER BY rb.created_at DESC
        """, conn, params=(user_id,))
        
        asset_df = pd.read_sql_query("""
            SELECT ab.*, a.name as item_name, 'Aset' as type
            FROM asset_bookings ab
            JOIN assets a ON ab.asset_id = a.id
            WHERE ab.user_id = ?
            ORDER BY ab.created_at DESC
        """, conn, params=(user_id,))
        
        vehicle_df = pd.read_sql_query("""
            SELECT vb.*, v.name as item_name, 'Kendaraan' as type
            FROM vehicle_bookings vb
            JOIN vehicles v ON vb.vehicle_id = v.id
            WHERE vb.user_id = ?
            ORDER BY vb.created_at DESC
        """, conn, params=(user_id,))
        
        conn.close()
        return room_df, asset_df, vehicle_df
    
    def get_all_bookings(self):
        """Ambil semua booking untuk admin - PERBAIKAN DENGAN requester_name"""
        conn = self.get_connection()
        
        try:
            # Ruangan - tambah requester_name
            room_df = pd.read_sql_query("""
                SELECT 
                    rb.id,
                    rb.date,
                    rb.start_time,
                    rb.end_time,
                    r.name as item_name,
                    u.name as user_name,
                    rb.requester_name as requester_name,  -- Pastikan ada kolom ini
                    rb.purpose,
                    rb.status,
                    rb.created_at
                FROM room_bookings rb
                LEFT JOIN rooms r ON rb.room_id = r.id
                LEFT JOIN users u ON rb.user_id = u.id
                ORDER BY rb.date DESC, rb.start_time DESC
            """, conn)
            
            # Aset - tambah requester_name
            asset_df = pd.read_sql_query("""
                SELECT 
                    ab.id,
                    ab.borrow_date as date,
                    ab.return_date,
                    a.name as item_name,
                    u.name as user_name,
                    ab.requester_name as requester_name,  -- Pastikan ada kolom ini
                    ab.purpose,
                    ab.status,
                    ab.created_at
                FROM asset_bookings ab
                LEFT JOIN assets a ON ab.asset_id = a.id
                LEFT JOIN users u ON ab.user_id = u.id
                ORDER BY ab.borrow_date DESC
            """, conn)
            
            # Kendaraan - tambah requester_name
            vehicle_df = pd.read_sql_query("""
                SELECT 
                    vb.id,
                    vb.start_date as date,
                    vb.end_date,
                    vb.start_time,
                    vb.end_time,
                    v.name as item_name,
                    u.name as user_name,
                    vb.requester_name as requester_name,  -- Pastikan ada kolom ini
                    vb.destination,
                    vb.purpose,
                    vb.status,
                    vb.created_at
                FROM vehicle_bookings vb
                LEFT JOIN vehicles v ON vb.vehicle_id = v.id
                LEFT JOIN users u ON vb.user_id = u.id
                ORDER BY vb.start_date DESC, vb.start_time DESC
            """, conn)
            
            # Debug print untuk memastikan kolom ada
            print(f"\n=== DEBUG get_all_bookings ===")
            if not room_df.empty:
                print(f"Room columns: {room_df.columns.tolist()}")
                print(f"Room sample requester_name: {room_df['requester_name'].head(3).tolist()}")
            if not asset_df.empty:
                print(f"Asset columns: {asset_df.columns.tolist()}")
                print(f"Asset sample requester_name: {asset_df['requester_name'].head(3).tolist()}")
            if not vehicle_df.empty:
                print(f"Vehicle columns: {vehicle_df.columns.tolist()}")
                print(f"Vehicle sample requester_name: {vehicle_df['requester_name'].head(3).tolist()}")
            
            return room_df, asset_df, vehicle_df
            
        except Exception as e:
            print(f"ERROR in get_all_bookings: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        finally:
            conn.close()

        
    def update_booking_status(self, booking_id, booking_type, status):
        """Update status booking"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if booking_type == 'Ruangan':
                cursor.execute("UPDATE room_bookings SET status=? WHERE id=?", (status, booking_id))
            elif booking_type == 'Aset':
                cursor.execute("UPDATE asset_bookings SET status=? WHERE id=?", (status, booking_id))
            elif booking_type == 'Kendaraan':
                cursor.execute("UPDATE vehicle_bookings SET status=? WHERE id=?", (status, booking_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
        
    def cancel_booking(self, booking_id, booking_type):
        """Batalkan booking berdasarkan ID dan jenis"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if booking_type == 'Ruangan':
                cursor.execute("UPDATE room_bookings SET status='dibatalkan' WHERE id=?", (booking_id,))
            elif booking_type == 'Aset':
                cursor.execute("UPDATE asset_bookings SET status='dibatalkan' WHERE id=?", (booking_id,))
            elif booking_type == 'Kendaraan':
                cursor.execute("UPDATE vehicle_bookings SET status='dibatalkan' WHERE id=?", (booking_id,))
            else:
                return False
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error canceling booking: {e}")
            return False
    
    def get_statistics(self):
        """Ambil statistik untuk dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM room_bookings")
        stats['total_room_bookings'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM asset_bookings")
        stats['total_asset_bookings'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vehicle_bookings")
        stats['total_vehicle_bookings'] = cursor.fetchone()[0]
        
        # Semua langsung disetujui, jadi tidak ada yang menunggu
        stats['pending_room'] = 0
        stats['pending_asset'] = 0
        stats['pending_vehicle'] = 0
        
        cursor.execute("""
            SELECT r.name, COUNT(*) as count
            FROM room_bookings rb
            JOIN rooms r ON rb.room_id = r.id
            GROUP BY rb.room_id
            ORDER BY count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        stats['most_booked_room'] = result[0] if result else 'Belum ada'
        
        cursor.execute("""
            SELECT a.name, COUNT(*) as count
            FROM asset_bookings ab
            JOIN assets a ON ab.asset_id = a.id
            GROUP BY ab.asset_id
            ORDER BY count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        stats['most_booked_asset'] = result[0] if result else 'Belum ada'
        
        conn.close()
        return stats
    
    def add_room(self, name, capacity):
        """Tambah ruangan baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO rooms (name, capacity) VALUES (?, ?)", (name, capacity))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_room(self, room_id, name, capacity, status):
        """Update ruangan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rooms SET name=?, capacity=?, status=? WHERE id=?",
                (name, capacity, status, room_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_room(self, room_id):
        """Hapus ruangan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms WHERE id=?", (room_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def add_asset(self, name, asset_type):
        """Tambah aset baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO assets (name, type) VALUES (?, ?)", (name, asset_type))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_asset(self, asset_id, name, asset_type, status, condition):
        """Update aset"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE assets SET name=?, type=?, status=?, condition=? WHERE id=?",
                (name, asset_type, status, condition, asset_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_asset(self, asset_id):
        """Hapus aset"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assets WHERE id=?", (asset_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def add_vehicle(self, name, vehicle_type, plate_number):
        """Tambah kendaraan baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vehicles (name, type, plate_number) VALUES (?, ?, ?)",
                (name, vehicle_type, plate_number)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_vehicle(self, vehicle_id, name, vehicle_type, plate_number, status):
        """Update kendaraan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE vehicles SET name=?, type=?, plate_number=?, status=? WHERE id=?",
                (name, vehicle_type, plate_number, status, vehicle_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_vehicle(self, vehicle_id):
        """Hapus kendaraan"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def export_bookings_to_csv(self, csv_path="booking.csv"):
        """Export semua data booking ke file CSV - DIPERBAIKI"""
        try:
            # Ambil semua data booking
            room_df, asset_df, vehicle_df = self.get_all_bookings()
            
            # Buat list untuk menampung semua data
            all_bookings = []
            
            # Proses data ruangan
            for _, row in room_df.iterrows():
                all_bookings.append({
                    'Jenis': 'Ruangan',
                    'Tanggal': row.get('date', ''),
                    'Jam Mulai': row.get('start_time', ''),
                    'Jam Selesai': row.get('end_time', ''),
                    'Item': row.get('item_name', ''),
                    'Pemesan': row.get('user_name', ''),
                    'Keperluan': row.get('purpose', ''),
                    'Status': row.get('status', ''),
                    'Waktu Booking': row.get('created_at', '')
                })
            
            # Proses data aset
            for _, row in asset_df.iterrows():
                all_bookings.append({
                    'Jenis': 'Aset',
                    'Tanggal Pinjam': row.get('date', ''),
                    'Tanggal Kembali': row.get('return_date', ''),
                    'Item': row.get('item_name', ''),
                    'Pemesan': row.get('user_name', ''),
                    'Keperluan': row.get('purpose', ''),
                    'Status': row.get('status', ''),
                    'Waktu Booking': row.get('created_at', '')
                })
            
            # Proses data kendaraan
            for _, row in vehicle_df.iterrows():
                all_bookings.append({
                    'Jenis': 'Kendaraan',
                    'Tanggal Mulai': row.get('date', ''),
                    'Tanggal Kembali': row.get('end_date', ''),
                    'Jam Mulai': row.get('start_time', ''),
                    'Jam Selesai': row.get('end_time', ''),
                    'Item': row.get('item_name', ''),
                    'Pemesan': row.get('user_name', ''),
                    'Tujuan': row.get('destination', ''),
                    'Keperluan': row.get('purpose', ''),
                    'Status': row.get('status', ''),
                    'Waktu Booking': row.get('created_at', '')
                })
            
            # Buat DataFrame
            if all_bookings:
                export_df = pd.DataFrame(all_bookings)
                # Urutkan berdasarkan waktu booking
                if 'Waktu Booking' in export_df.columns:
                    export_df = export_df.sort_values('Waktu Booking', ascending=False)
                
                # Simpan ke CSV
                export_df.to_csv(csv_path, index=False, encoding='utf-8')
                print(f"Data berhasil diexport ke {csv_path} ({len(export_df)} records)")
                return True
            else:
                print("Tidak ada data untuk diexport")
                return False
                
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            import traceback
            traceback.print_exc()
            return False

    def export_daily_bookings(self, date_str, csv_path="booking_harian.csv"):
        """Export booking harian ke CSV - DIPERBAIKI"""
        try:
            # Ambil semua data
            room_df, asset_df, vehicle_df = self.get_all_bookings()
            
            # Filter untuk tanggal tertentu
            daily_bookings = []
            
            # Filter ruangan untuk tanggal tertentu
            if not room_df.empty and 'date' in room_df.columns:
                daily_rooms = room_df[room_df['date'] == date_str]
                for _, row in daily_rooms.iterrows():
                    daily_bookings.append({
                        'Jenis': 'Ruangan',
                        'Item': row.get('item_name', ''),
                        'Pemesan': row.get('user_name', ''),
                        'Waktu': f"{row.get('start_time', '')} - {row.get('end_time', '')}",
                        'Tanggal': row.get('date', ''),
                        'Keperluan': row.get('purpose', ''),
                        'Status': row.get('status', '')
                    })
            
            # Filter aset untuk tanggal tertentu
            if not asset_df.empty and 'date' in asset_df.columns and 'return_date' in asset_df.columns:
                daily_assets = asset_df[
                    (asset_df['date'] <= date_str) & 
                    (asset_df['return_date'] >= date_str)
                ]
                for _, row in daily_assets.iterrows():
                    daily_bookings.append({
                        'Jenis': 'Aset',
                        'Item': row.get('item_name', ''),
                        'Pemesan': row.get('user_name', ''),
                        'Waktu': f"{row.get('date', '')} s/d {row.get('return_date', '')}",
                        'Tanggal': row.get('date', ''),
                        'Keperluan': row.get('purpose', ''),
                        'Status': row.get('status', '')
                    })
            
            # Filter kendaraan untuk tanggal tertentu
            if not vehicle_df.empty and 'date' in vehicle_df.columns and 'end_date' in vehicle_df.columns:
                daily_vehicles = vehicle_df[
                    (vehicle_df['date'] <= date_str) & 
                    (vehicle_df['end_date'] >= date_str)
                ]
                for _, row in daily_vehicles.iterrows():
                    daily_bookings.append({
                        'Jenis': 'Kendaraan',
                        'Item': row.get('item_name', ''),
                        'Pemesan': row.get('user_name', ''),
                        'Waktu': f"{row.get('date', '')} s/d {row.get('end_date', '')}",
                        'Jam': f"{row.get('start_time', '')} - {row.get('end_time', '')}",
                        'Tanggal': row.get('date', ''),
                        'Tujuan': row.get('destination', ''),
                        'Keperluan': row.get('purpose', ''),
                        'Status': row.get('status', '')
                    })
            
            if daily_bookings:
                df_daily = pd.DataFrame(daily_bookings)
                df_daily.to_csv(csv_path, index=False, encoding='utf-8')
                print(f"Data harian berhasil diexport ke {csv_path} ({len(df_daily)} records)")
                return True
            else:
                print(f"Tidak ada data untuk tanggal {date_str}")
                return False
                
        except Exception as e:
            print(f"Error exporting daily bookings: {e}")
            return False
    
    def auto_save_bookings_to_csv(self, csv_path="booking.csv"):
        """Auto save semua booking ke CSV - untuk dipanggil setelah booking berhasil"""
        try:
            return self.export_bookings_to_csv(csv_path)
        except Exception as e:
            print(f"Error auto-saving to CSV: {e}")
            return False
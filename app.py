import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from db import Database
import calendar
from pathlib import Path
import time
import os
import csv

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(
    page_title="SIMARU-KPP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# LOAD CSS
# ============================================================================
def load_css():
    css_file = Path("styles.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("File CSS tidak ditemukan!")

load_css()

# ============================================================================
# INITIALIZE DATABASE & SESSION STATE
# ============================================================================
db = Database()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'booking_tab' not in st.session_state:
    st.session_state.booking_tab = 0

# ============================================================================
# NAVBAR MODERN
# ============================================================================
def show_navbar():
    user = st.session_state.user
    is_admin = user and user.get('role') == 'admin'
    
    # Get initials for avatar - dari NAMA
    initials = user['name'][0].upper() if user and user.get('name') else 'U'
    username = user['username'] if user and user.get('username') else 'Guest'
    name = user['name'] if user and user.get('name') else 'Tamu'
    role = user['role'].upper() if user and user.get('role') else 'GUEST'
    
    navbar_html = f"""
    <div class="navbar">
        <div class="navbar-content">
            <div class="navbar-brand">
                <div class="navbar-logo">S</div>
                <div class="navbar-title">
                    <div class="navbar-title-main">SIMARU-KPP</div>
                    <div class="navbar-title-sub">Sistem Manajemen Aset dan Ruangan</div>
                </div>
            </div>
            <div class="navbar-user">
                <div class="navbar-user-avatar">{initials}</div>
                <div class="navbar-user-info">
                    <div class="navbar-user-name">{name}</div>
                    <div class="navbar-user-role">{role} • IP: {username}</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)
    
    # Navigation Menu
    nav_menu_html = '<div class="nav-menu"><div class="nav-menu-container">'
    st.markdown(nav_menu_html, unsafe_allow_html=True)
    
    # Menu buttons
    if is_admin:
        cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
        menu_items = [
            ('home', 'Home'),
            ('booking', 'Booking'),
            ('jadwal', 'Jadwal'),
            ('riwayat', 'Riwayat'),
            ('profil', 'Profil'),
            ('admin', 'Admin'),
            ('statistik', 'Statistik'),
            ('logout', 'Logout')
        ]
    else:
        cols = st.columns([1, 1, 1, 1, 1, 1])
        menu_items = [
            ('home', 'Home'),
            ('booking', 'Booking'),
            ('jadwal', 'Jadwal'),
            ('riwayat', 'Riwayat'),
            ('profil', 'Profil'),
            ('logout', 'Logout')
        ]
    
    for i, (page_key, label) in enumerate(menu_items):
        with cols[i]:
            if page_key == 'logout':
                if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state.logged_in = False
                    st.session_state.user = None
                    st.session_state.page = 'home'
                    for key in list(st.session_state.keys()):
                        if 'available' in key or 'booking_data' in key:
                            del st.session_state[key]
                    st.rerun()
            else:
                if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                    st.session_state.page = page_key
                    st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================================================
# HALAMAN LOGIN - DIPERBAIKI TOTAL: SATU FORM UNTUK SEMUA
# ============================================================================
def show_login():
    login_html = """
    <div class="login-wrapper-white">
        <div class="login-container-white">
            <div class="login-header-blue">
                <div class="login-logo-blue">S</div>
                <div class="login-title-blue">SIMARU-KPP</div>
                <div class="login-subtitle-blue">
                    Sistem Manajemen Aset dan Ruangan<br>
                    KPP Pratama Jombang
                </div>
            </div>
            <div class="login-form-container-white">
    """
    
    st.markdown(login_html, unsafe_allow_html=True)
    
    st.markdown('<div class="login-form-white">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        username = st.text_input(
            "Username / Nomor IP",
            placeholder="Masukkan username atau nomor IP",
            key="username_input",
            help="Masukkan nomor IP (contoh: 060090147) dengan angka 0 di depan"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Masukkan password",
            key="password_input",
            help="Masukkan password yang sesuai"
        )
        
        # Tombol login
        if st.button("LOGIN KE SISTEM", use_container_width=True, key="btn_login", type="primary"):
            if not username or not password:
                st.error("Harap masukkan username dan password!")
            else:
                # Strip whitespace dan pastikan string
                username = str(username).strip()
                password = str(password).strip()
                
                # Verifikasi user dari database
                with st.spinner("Memverifikasi login..."):
                    user_data = db.verify_user(username, password)
                
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.page = 'home'
                    st.success(f"Login berhasil! Selamat datang, {user_data['name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Username atau password salah!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div></div></div>', unsafe_allow_html=True)
# ============================================================================
# HALAMAN HOME
# ============================================================================
def show_home():
    show_navbar()
    
    user = st.session_state.user
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">Selamat Datang, {user['name']}</div>
        <div class="card-body">
            <p style="font-size: 1.15rem; color: var(--gray-700); margin: 0;">
                Sistem Manajemen Aset dan Ruangan KPP Pratama Jombang.<br>
                Kelola booking ruangan, aset elektronik, dan kendaraan dinas dengan mudah dan efisien.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Access Menu
    st.markdown("### Menu Cepat Akses")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">R</div>
            <div class="feature-title">Booking Ruangan</div>
            <div class="feature-description">Pesan ruang rapat untuk kegiatan kantor dan meeting resmi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Booking Ruangan", use_container_width=True, key="home_room_btn"):
            st.session_state.page = 'booking'
            st.session_state.booking_tab = 0
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">A</div>
            <div class="feature-title">Booking Aset Elektronik</div>
            <div class="feature-description">Pinjam laptop, proyektor, printer untuk kebutuhan pekerjaan</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Booking Aset", use_container_width=True, key="home_asset_btn"):
            st.session_state.page = 'booking'
            st.session_state.booking_tab = 1
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">K</div>
            <div class="feature-title">Booking Kendaraan</div>
            <div class="feature-description">Pesan kendaraan dinas untuk perjalanan dinas resmi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Booking Kendaraan", use_container_width=True, key="home_vehicle_btn"):
            st.session_state.page = 'booking'
            st.session_state.booking_tab = 2
            st.rerun()
    
    # Dashboard Metrics
    st.markdown("### Ringkasan Aktivitas")
    
    # Ambil data dari database
    try:
        room_df, asset_df, vehicle_df = db.get_user_bookings(user['id'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_rooms = len(room_df)
            st.metric("Ruangan", str(total_rooms), "Booking")
        
        with col2:
            total_assets = len(asset_df)
            st.metric("Aset", str(total_assets), "Peminjaman")
        
        with col3:
            total_vehicles = len(vehicle_df)
            st.metric("Kendaraan", str(total_vehicles), "Pemesanan")
        
        with col4:
            # Semua booking langsung disetujui
            approved = len(room_df) + len(asset_df) + len(vehicle_df)
            st.metric("Disetujui", str(approved), "Semua")
    
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ruangan", "0", "Booking")
        with col2:
            st.metric("Aset", "0", "Peminjaman")
        with col3:
            st.metric("Kendaraan", "0", "Pemesanan")
        with col4:
            st.metric("Disetujui", "0", "Semua")

# ============================================================================
# HALAMAN BOOKING - LANGSUNG DISETUJUI
# ============================================================================
def show_booking():
    show_navbar()
    
    st.markdown("""
    <div class="card">
        <div class="card-header">Formulir Pemesanan</div>
        <div class="card-body">
            Pilih jenis pemesanan yang Anda butuhkan di bawah ini. <strong>Semua booking langsung disetujui otomatis.</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_labels = ["Ruang Rapat", "Aset Elektronik", "Kendaraan Dinas"]
    tabs = st.tabs(tab_labels)
    
    with tabs[0]:
        show_room_booking()
    
    with tabs[1]:
        show_asset_booking()
    
    with tabs[2]:
        show_vehicle_booking()

def show_room_booking():
    st.markdown("### Formulir Pemesanan Ruang Rapat")
    st.markdown("Silakan isi formulir di bawah ini untuk melakukan pemesanan ruang rapat. **Status: Langsung Disetujui**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Detail Waktu**")
        booking_date = st.date_input("Tanggal Penggunaan", min_value=date.today(), key="room_date_input")
        start_time = st.time_input("Jam Mulai (WIB)", key="room_start_input")
        end_time = st.time_input("Jam Selesai (WIB)", key="room_end_input")
    
    with col2:
        st.markdown("**Informasi Pemesanan**")
        purpose = st.text_area("Keperluan / Agenda Rapat", height=150, key="room_purpose_input",
                              placeholder="Contoh: Rapat Koordinasi Bulanan, Presentasi Project, dll.")
    
        # Field nama pemesan manual
        user_name = st.text_input("Nama Pemesan", 
                                 value=st.session_state.user['name'],
                                 key="room_requester_name",
                                 help="Nama pemesan yang akan ditampilkan di jadwal")
    
    # TAMPILKAN PILIHAN RUANGAN YANG TERSEDIA
    st.markdown("### Pilihan Ruangan Tersedia")
    
    # Cek ketersediaan dulu sebelum tombol booking
    if booking_date and start_time and end_time:
        available_rooms = db.get_available_rooms(
            str(booking_date),
            str(start_time),
            str(end_time)
        )
        
        if available_rooms:
            # Buat pilihan ruangan
            room_options = []
            for room in available_rooms:
                room_id = room[0]
                room_name = room[1]
                capacity = room[2] if len(room) > 2 else "N/A"
                room_options.append(f"{room_name} (Kapasitas: {capacity} orang)")
            
            # Tampilkan dropdown pilihan
            selected_room_option = st.selectbox(
                "Pilih Ruangan",
                options=room_options,
                key="room_selection"
            )
            
            # Ambil ID ruangan dari pilihan
            selected_room_name = selected_room_option.split(" (Kapasitas:")[0]
            selected_room_id = None
            for room in available_rooms:
                if room[1] == selected_room_name:
                    selected_room_id = room[0]
                    break
        else:
            st.warning("Tidak ada ruangan tersedia pada waktu tersebut.")
            selected_room_id = None
    else:
        st.info("Pilih tanggal dan waktu terlebih dahulu untuk melihat ruangan tersedia")
        selected_room_id = None
    
    # Spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Button booking
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("BOOKING SEKARANG", key="book_room_direct", use_container_width=True, type="primary"):
            if start_time >= end_time:
                st.error("Jam selesai harus lebih dari jam mulai!")
            elif not purpose:
                st.error("Keperluan rapat harus diisi!")
            elif not selected_room_id:
                st.error("Pilih ruangan terlebih dahulu!")
            else:
                with st.spinner("Memproses booking..."):
                    success = db.add_room_booking(
                        st.session_state.user['id'],
                        selected_room_id,
                        str(booking_date),
                        str(start_time),
                        str(end_time),
                        purpose,
                        user_name  # Ini adalah requester_name dari input field
                    )
                    
                    if success:
                        try:
                            db.export_bookings_to_csv("booking.csv")
                        except Exception as e:
                            print(f"Error saving to CSV: {e}")
                        
                        # Cari nama ruangan untuk pesan sukses
                        room_name = selected_room_name if 'selected_room_name' in locals() else "Ruangan"
                        st.success(f"Booking berhasil! Ruangan: {room_name} (Langsung Disetujui)")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Booking gagal. Silakan coba lagi.")
def show_asset_booking():
    st.markdown("### Formulir Peminjaman Aset Elektronik")
    st.markdown("Silakan isi formulir di bawah ini untuk melakukan peminjaman aset elektronik. **Status: Langsung Disetujui**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Detail Aset**")
        asset_type = st.selectbox("Jenis Aset", ["Laptop", "Proyektor"], key="asset_type_select")
        
        st.markdown("**Periode Peminjaman**")
        borrow_date = st.date_input("Tanggal Pinjam", min_value=date.today(), key="asset_borrow_date_input")
        return_date = st.date_input("Tanggal Kembali", min_value=date.today(), key="asset_return_date_input")
    
    with col2:
        st.markdown("**Informasi Peminjaman**")
        purpose = st.text_area("Keperluan Penggunaan", height=150, key="asset_purpose_input",
                              placeholder="Contoh: Presentasi klien, Training, Work from Home, dll.")
        # Field nama pemesan manual
        user_name = st.text_input("Nama Pemesan", 
                                 value=st.session_state.user['name'],
                                 key="asset_requester_name",
                                 help="Nama pemesan yang akan ditampilkan di jadwal")
    
    
    # TAMPILKAN PILIHAN ASET YANG TERSEDIA
    st.markdown("### Pilihan Aset Tersedia")
    
    if borrow_date and return_date:
        available_assets = db.get_available_assets(
            str(borrow_date),
            str(return_date),
            asset_type
        )
        
        if available_assets:
            # Buat pilihan aset
            asset_options = []
            for asset in available_assets:
                asset_id = asset[0]
                asset_name = asset[1]
                asset_type_name = asset[2] if len(asset) > 2 else "N/A"
                asset_options.append(f"{asset_name} ({asset_type_name})")
            
            # Tampilkan dropdown pilihan
            selected_asset_option = st.selectbox(
                "Pilih Aset",
                options=asset_options,
                key="asset_selection"
            )
            
            # Ambil ID aset dari pilihan
            selected_asset_name = selected_asset_option.split(" (")[0]
            selected_asset_id = None
            for asset in available_assets:
                if asset[1] == selected_asset_name:
                    selected_asset_id = asset[0]
                    break
        else:
            st.warning(f"Tidak ada {asset_type} tersedia pada periode tersebut.")
            selected_asset_id = None
    else:
        st.info("Pilih tanggal pinjam dan kembali terlebih dahulu")
        selected_asset_id = None
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Button booking
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("PINJAM SEKARANG", key="book_asset_direct", use_container_width=True, type="primary"):
            if return_date < borrow_date:
                st.error("Tanggal kembali harus lebih dari tanggal pinjam!")
            elif not purpose:
                st.error("Keperluan penggunaan harus diisi!")
            elif not selected_asset_id:
                st.error("Pilih aset terlebih dahulu!")
            else:
                with st.spinner("Memproses peminjaman..."):
                    success = db.add_asset_booking(
                        st.session_state.user['id'],
                        selected_asset_id,
                        str(borrow_date),
                        str(return_date),
                        purpose,
                        user_name  # Ini adalah requester_name dari input field
                    )
                       
                    
                    if success:
                        try:
                            db.export_bookings_to_csv("booking.csv")
                        except Exception as e:
                            print(f"Error saving to CSV: {e}")
                        
                        # Cari nama aset untuk pesan sukses
                        asset_name = selected_asset_name if 'selected_asset_name' in locals() else "Aset"
                        st.success(f"Peminjaman berhasil! Aset: {asset_name} (Langsung Disetujui)")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Peminjaman gagal. Silakan coba lagi.")
def show_vehicle_booking():
    st.markdown("### Formulir Pemesanan Kendaraan Dinas")
    st.markdown("Silakan isi formulir di bawah ini untuk melakukan pemesanan kendaraan dinas. **Status: Langsung Disetujui**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Detail Kendaraan**")
        vehicle_type = st.selectbox("Jenis Kendaraan", ["Mobil"], key="vehicle_type_select")
        st.markdown("**Periode Penggunaan**")
        booking_date = st.date_input("Tanggal Peminjaman", min_value=date.today(), key="vehicle_booking_date_input")
        
        # Pilihan sesi waktu
        time_sessions = {
            "Sesi 1 (08.12 - 12.16)": {"start": "08:12:00", "end": "12:16:00"},
            "Sesi 2 (13.30 - 16.00)": {"start": "13:30:00", "end": "16:00:00"}
        }
        selected_session = st.selectbox("Pilih Sesi Waktu", list(time_sessions.keys()), key="vehicle_time_session")
    
    with col2:
        st.markdown("**Informasi Perjalanan**")
        destination = st.text_input("Tujuan Perjalanan", key="vehicle_destination_input",
                                   placeholder="Contoh: Kantor Pajak Pusat, Meeting dengan klien, dll.")
        purpose = st.text_area("Keperluan Perjalanan", height=100, key="vehicle_purpose_input",
                              placeholder="Contoh: Dinas luar kota, Meeting dengan vendor, Pengambilan dokumen, dll.")
        # Field nama pemesan manual
        user_name = st.text_input("Nama Pemesan", 
                                 value=st.session_state.user['name'],
                                 key="vehicle_requester_name",
                                 help="Nama pemesan yang akan ditampilkan di jadwal")
    
    # TAMPILKAN PILIHAN KENDARAAN YANG TERSEDIA
    st.markdown("### Pilihan Kendaraan Tersedia")
    
    if booking_date and selected_session:
        session_info = time_sessions[selected_session]
        
        available_vehicles = db.get_available_vehicles(
            str(booking_date),
            session_info["start"],
            session_info["end"],
            vehicle_type
        )
        
        if available_vehicles:
            # Buat pilihan kendaraan
            vehicle_options = []
            for vehicle in available_vehicles:
                vehicle_id = vehicle[0]
                vehicle_name = vehicle[1]
                plate_number = vehicle[3] if len(vehicle) > 3 else "N/A"
                vehicle_options.append(f"{vehicle_name} ({plate_number})")
            
            # Tampilkan dropdown pilihan
            selected_vehicle_option = st.selectbox(
                "Pilih Kendaraan",
                options=vehicle_options,
                key="vehicle_selection"
            )
            
            # Ambil ID kendaraan dari pilihan
            selected_vehicle_name = selected_vehicle_option.split(" (")[0]
            selected_vehicle_id = None
            for vehicle in available_vehicles:
                if vehicle[1] == selected_vehicle_name:
                    selected_vehicle_id = vehicle[0]
                    break
        else:
            st.warning(f"Tidak ada {vehicle_type} tersedia pada waktu tersebut.")
            selected_vehicle_id = None
    else:
        st.info("Pilih tanggal dan sesi terlebih dahulu")
        selected_vehicle_id = None
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Button booking
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("PESAN SEKARANG", key="book_vehicle_direct", use_container_width=True, type="primary"):
            if not destination:
                st.error("Tujuan perjalanan harus diisi!")
            elif not purpose:
                st.error("Keperluan perjalanan harus diisi!")
            elif not selected_vehicle_id:
                st.error("Pilih kendaraan terlebih dahulu!")
            else:
                # Ambil waktu dari sesi yang dipilih
                session_info = time_sessions[selected_session]
                
                with st.spinner("Memproses pemesanan..."):
                    success = db.add_vehicle_booking(
                        st.session_state.user['id'],
                        selected_vehicle_id,
                        str(booking_date),
                        str(booking_date),
                        session_info["start"],
                        session_info["end"],
                        destination,
                        purpose,
                        user_name  # Ini adalah requester_name dari input field
                    )

                    
                    if success:
                        try:
                            db.export_bookings_to_csv("booking.csv")
                        except Exception as e:
                            print(f"Error saving to CSV: {e}")
                        
                        # Cari nama kendaraan untuk pesan sukses
                        vehicle_name = selected_vehicle_name if 'selected_vehicle_name' in locals() else "Kendaraan"
                        st.success(f"Pemesanan berhasil! Kendaraan: {vehicle_name} (Langsung Disetujui)")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Pemesanan gagal. Silakan coba lagi.")
# ============================================================================
# HALAMAN RIWAYAT
# ============================================================================
def show_riwayat():
    show_navbar()
    
    st.markdown("""
    <div class="card">
        <div class="card-header">Riwayat Pemesanan</div>
        <div class="card-body">
            <p>Berikut adalah riwayat pemesanan Anda. <strong>Anda dapat membatalkan pemesanan yang masih aktif.</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab untuk berbagai jenis riwayat
    tab1, tab2, tab3 = st.tabs(["Ruangan", "Aset", "Kendaraan"])
    
    with tab1:
        st.markdown("### Riwayat Pemesanan Ruangan")
        
        try:
            room_df, _, _ = db.get_user_bookings(st.session_state.user['id'])
            if not room_df.empty:
                # Format kolom untuk tampilan
                display_df = room_df[['id', 'date', 'item_name', 'start_time', 'end_time', 'purpose', 'status']].copy()
                display_df.columns = ['ID', 'Tanggal', 'Ruangan', 'Jam Mulai', 'Jam Selesai', 'Keperluan', 'Status']
                display_df['Status'] = display_df['Status'].str.capitalize()
                
                # Tampilkan dataframe tanpa kolom ID
                st.dataframe(display_df.drop('ID', axis=1), use_container_width=True)
                
                # Fitur pembatalan
                st.markdown("---")
                st.markdown("### Pembatalan Pemesanan")
                
                # Hanya tampilkan booking yang masih disetujui
                active_bookings = display_df[display_df['Status'] == 'Disetujui']
                
                if not active_bookings.empty:
                    # Buat opsi untuk dropdown
                    booking_options = []
                    for _, row in active_bookings.iterrows():
                        booking_options.append(
                            f"ID {row['ID']}: {row['Ruangan']} - {row['Tanggal']} ({row['Jam Mulai']} - {row['Jam Selesai']})"
                        )
                    
                    selected_option = st.selectbox(
                        "Pilih booking yang akan dibatalkan:",
                        options=booking_options,
                        key="cancel_room_select"
                    )
                    
                    if selected_option:
                        # Ambil ID dari pilihan
                        booking_id = int(selected_option.split("ID ")[1].split(":")[0])
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("Batalkan Booking Ini", 
                                       key="cancel_room_btn", 
                                       type="primary",
                                       use_container_width=True):
                                with st.spinner("Membatalkan booking..."):
                                    if db.cancel_booking(booking_id, 'Ruangan'):
                                        st.success("Booking berhasil dibatalkan!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Gagal membatalkan booking!")
                else:
                    st.info("Tidak ada booking aktif yang dapat dibatalkan")
            else:
                st.info("Belum ada riwayat pemesanan ruangan.")
                
        except Exception as e:
            st.error(f"Error memuat data ruangan: {str(e)}")
            st.info("Belum ada riwayat pemesanan ruangan.")
    
    with tab2:
        st.markdown("### Riwayat Peminjaman Aset")
        
        try:
            _, asset_df, _ = db.get_user_bookings(st.session_state.user['id'])
            if not asset_df.empty:
                # Format kolom untuk tampilan
                display_df = asset_df[['id', 'borrow_date', 'return_date', 'item_name', 'purpose', 'status']].copy()
                display_df.columns = ['ID', 'Tanggal Pinjam', 'Tanggal Kembali', 'Aset', 'Keperluan', 'Status']
                display_df['Status'] = display_df['Status'].str.capitalize()
                
                # Tampilkan dataframe tanpa kolom ID
                st.dataframe(display_df.drop('ID', axis=1), use_container_width=True)
                
                # Fitur pembatalan
                st.markdown("---")
                st.markdown("### Pembatalan Peminjaman")
                
                # Hanya tampilkan booking yang masih disetujui
                active_bookings = display_df[display_df['Status'] == 'Disetujui']
                
                if not active_bookings.empty:
                    # Buat opsi untuk dropdown
                    booking_options = []
                    for _, row in active_bookings.iterrows():
                        booking_options.append(
                            f"ID {row['ID']}: {row['Aset']} - {row['Tanggal Pinjam']} s/d {row['Tanggal Kembali']}"
                        )
                    
                    selected_option = st.selectbox(
                        "Pilih peminjaman yang akan dibatalkan:",
                        options=booking_options,
                        key="cancel_asset_select"
                    )
                    
                    if selected_option:
                        # Ambil ID dari pilihan
                        booking_id = int(selected_option.split("ID ")[1].split(":")[0])
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("Batalkan Peminjaman Ini", 
                                       key="cancel_asset_btn", 
                                       type="primary",
                                       use_container_width=True):
                                with st.spinner("Membatalkan peminjaman..."):
                                    if db.cancel_booking(booking_id, 'Aset'):
                                        st.success("Peminjaman berhasil dibatalkan!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Gagal membatalkan peminjaman!")
                else:
                    st.info("Tidak ada peminjaman aktif yang dapat dibatalkan")
            else:
                st.info("Belum ada riwayat peminjaman aset.")
                
        except Exception as e:
            st.error(f"Error memuat data aset: {str(e)}")
            st.info("Belum ada riwayat peminjaman aset.")
    
    with tab3: 
        st.markdown("### Riwayat Pemesanan Kendaraan")
        
        try:
            _, _, vehicle_df = db.get_user_bookings(st.session_state.user['id'])
            if not vehicle_df.empty:
                # Format kolom untuk tampilan
                display_df = vehicle_df[['id', 'start_date', 'end_date', 'item_name', 'destination', 'purpose', 'status']].copy()
                display_df.columns = ['ID', 'Tanggal Mulai', 'Tanggal Kembali', 'Kendaraan', 'Tujuan', 'Keperluan', 'Status']
                display_df['Status'] = display_df['Status'].str.capitalize()
                
                # Tampilkan dataframe tanpa kolom ID
                st.dataframe(display_df.drop('ID', axis=1), use_container_width=True)
                
                # Fitur pembatalan
                st.markdown("---")
                st.markdown("### Pembatalan Pemesanan")
                
                # Hanya tampilkan booking yang masih disetujui
                active_bookings = display_df[display_df['Status'] == 'Disetujui']
                
                if not active_bookings.empty:
                    # Buat opsi untuk dropdown
                    booking_options = []
                    for _, row in active_bookings.iterrows():
                        booking_options.append(
                            f"ID {row['ID']}: {row['Kendaraan']} - {row['Tanggal Mulai']} s/d {row['Tanggal Kembali']}"
                        )
                    
                    selected_option = st.selectbox(
                        "Pilih pemesanan yang akan dibatalkan:",
                        options=booking_options,
                        key="cancel_vehicle_select"
                    )
                    
                    if selected_option:
                        # Ambil ID dari pilihan
                        booking_id = int(selected_option.split("ID ")[1].split(":")[0])
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("Batalkan Pemesanan Ini", 
                                       key="cancel_vehicle_btn", 
                                       type="primary",
                                       use_container_width=True):
                                with st.spinner("Membatalkan pemesanan..."):
                                    if db.cancel_booking(booking_id, 'Kendaraan'):
                                        st.success("Pemesanan berhasil dibatalkan!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Gagal membatalkan pemesanan!")
                else:
                    st.info("Tidak ada pemesanan aktif yang dapat dibatalkan")
            else:
                st.info("Belum ada riwayat pemesanan kendaraan.")
                
        except Exception as e:
            st.error(f"Error memuat data kendaraan: {str(e)}")
            st.info("Belum ada riwayat pemesanan kendaraan.")

# ============================================================================
# HALAMAN ADMIN 
# ============================================================================
def show_admin():
    show_navbar()
    
    # Hanya untuk admin
    if st.session_state.user and st.session_state.user.get('role') != 'admin':
        st.warning("Hanya administrator yang dapat mengakses halaman ini.")
        return
    
    st.markdown("""
    <div class="card">
        <div class="card-header">Panel Administrasi</div>
        <div class="card-body">
            <p><strong>Catatan:</strong> Semua booking langsung disetujui otomatis.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab untuk berbagai fungsi admin
    tab1, tab2, tab3 = st.tabs(["Manajemen User", "Manajemen Aset", "Laporan"])
    
    with tab1:
        st.markdown("### Manajemen Pengguna")
        
        try:
            users_df = db.get_all_users()
            st.dataframe(users_df, use_container_width=True)
            
            # Form tambah pengguna
            with st.expander("Tambah Pengguna Baru"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Username", key="new_username")
                    new_password = st.text_input("Password", type="password", key="new_password")
                
                with col2:
                    new_name = st.text_input("Nama Lengkap", key="new_name")
                    new_role = st.selectbox("Role", ["user", "admin"], key="new_role")
                
                if st.button("Tambah Pengguna", key="add_user_btn"):
                    if db.add_user(new_username, new_password, new_name, new_role):
                        st.success("Pengguna berhasil ditambahkan!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Gagal menambah pengguna!")
                        
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")
    
    with tab2:
        st.markdown("### Manajemen Aset dan Ruangan")
        
        # Tampilkan ruangan
        st.markdown("#### Daftar Ruangan")
        try:
            rooms_df = db.get_all_rooms()
            st.dataframe(rooms_df, use_container_width=True)
            
            # TAMBAH FITUR HAPUS RUANGAN
            if not rooms_df.empty:
                with st.expander("Hapus Ruangan"):
                    # Buat pilihan untuk dropdown
                    room_options = []
                    for _, row in rooms_df.iterrows():
                        room_options.append(f"{row['name']} (Kapasitas: {row['capacity']})")
                    
                    selected_room = st.selectbox(
                        "Pilih Ruangan yang akan dihapus",
                        options=room_options,
                        key="delete_room_select"
                    )
                    
                    if st.button("Hapus Ruangan", key="delete_room_btn"):
                        # Ambil nama ruangan dari pilihan
                        room_name = selected_room.split(" (Kapasitas:")[0]
                        
                        # Cari ID ruangan
                        room_id = None
                        for _, row in rooms_df.iterrows():
                            if row['name'] == room_name:
                                room_id = row['id']
                                break
                        
                        if room_id and db.delete_room(room_id):
                            st.success(f"Ruangan '{room_name}' berhasil dihapus!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Gagal menghapus ruangan!")
            
            # Form tambah ruangan
            with st.expander("Tambah Ruangan Baru"):
                col1, col2 = st.columns(2)
                with col1:
                    new_room_name = st.text_input("Nama Ruangan", key="new_room_name")
                with col2:
                    new_room_capacity = st.number_input("Kapasitas", min_value=1, value=10, key="new_room_capacity")
                
                if st.button("Tambah Ruangan", key="add_room_btn"):
                    if db.add_room(new_room_name, new_room_capacity):
                        st.success("Ruangan berhasil ditambahkan!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Gagal menambah ruangan!")
                        
        except:
            st.info("Tidak ada data ruangan")
        
        # Tampilkan aset
        st.markdown("#### Daftar Aset")
        try:
            assets_df = db.get_all_assets()
            st.dataframe(assets_df, use_container_width=True)
            
            # TAMBAH FITUR HAPUS ASET
            if not assets_df.empty:
                with st.expander("Hapus Aset"):
                    # Buat pilihan untuk dropdown
                    asset_options = []
                    for _, row in assets_df.iterrows():
                        asset_options.append(f"{row['name']} ({row['type']})")
                    
                    selected_asset = st.selectbox(
                        "Pilih Aset yang akan dihapus",
                        options=asset_options,
                        key="delete_asset_select"
                    )
                    
                    if st.button("Hapus Aset", key="delete_asset_btn"):
                        # Ambil nama aset dari pilihan
                        asset_name = selected_asset.split(" (")[0]
                        
                        # Cari ID aset
                        asset_id = None
                        for _, row in assets_df.iterrows():
                            if row['name'] == asset_name:
                                asset_id = row['id']
                                break
                        
                        if asset_id and db.delete_asset(asset_id):
                            st.success(f"Aset '{asset_name}' berhasil dihapus!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Gagal menghapus aset!")
            
            # Form tambah aset
            with st.expander("Tambah Aset Baru"):
                col1, col2 = st.columns(2)
                with col1:
                    new_asset_name = st.text_input("Nama Aset", key="new_asset_name")
                with col2:
                    new_asset_type = st.selectbox("Jenis Aset", ["Laptop", "Proyektor"], key="new_asset_type")
                
                if st.button("Tambah Aset", key="add_asset_btn"):
                    if db.add_asset(new_asset_name, new_asset_type):
                        st.success("Aset berhasil ditambahkan!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Gagal menambah aset!")
                        
        except:
            st.info("Tidak ada data aset")
        
        # Tampilkan kendaraan
        st.markdown("#### Daftar Kendaraan")
        try:
            vehicles_df = db.get_all_vehicles()
            st.dataframe(vehicles_df, use_container_width=True)
            
            # TAMBAH FITUR HAPUS KENDARAAN
            if not vehicles_df.empty:
                with st.expander("Hapus Kendaraan"):
                    # Buat pilihan untuk dropdown
                    vehicle_options = []
                    for _, row in vehicles_df.iterrows():
                        vehicle_options.append(f"{row['name']} ({row['plate_number']})")
                    
                    selected_vehicle = st.selectbox(
                        "Pilih Kendaraan yang akan dihapus",
                        options=vehicle_options,
                        key="delete_vehicle_select"
                    )
                    
                    if st.button("Hapus Kendaraan", key="delete_vehicle_btn"):
                        # Ambil nama kendaraan dari pilihan
                        vehicle_name = selected_vehicle.split(" (")[0]
                        
                        # Cari ID kendaraan
                        vehicle_id = None
                        for _, row in vehicles_df.iterrows():
                            if row['name'] == vehicle_name:
                                vehicle_id = row['id']
                                break
                        
                        if vehicle_id and db.delete_vehicle(vehicle_id):
                            st.success(f"Kendaraan '{vehicle_name}' berhasil dihapus!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Gagal menghapus kendaraan!")
            
            # Form tambah kendaraan
            with st.expander("Tambah Kendaraan Baru"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_vehicle_name = st.text_input("Nama Kendaraan", key="new_vehicle_name")
                with col2:
                    new_vehicle_type = st.selectbox("Jenis Kendaraan", ["Mobil"], key="new_vehicle_type")
                with col3:
                    new_plate_number = st.text_input("Nomor Plat", key="new_plate_number")
                
                if st.button("Tambah Kendaraan", key="add_vehicle_btn"):
                    if db.add_vehicle(new_vehicle_name, new_vehicle_type, new_plate_number):
                        st.success("Kendaraan berhasil ditambahkan!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Gagal menambah kendaraan!")
                        
        except:
            st.info("Tidak ada data kendaraan")
    
    with tab3:
        st.markdown("### Laporan dan Statistik")
        
        try:
            stats = db.get_statistics()
            
            # Container untuk statistik
            with st.container():
                st.markdown("#### Statistik Sistem")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="Booking Ruangan", 
                        value=stats.get('total_room_bookings', 0),
                        delta="Total"
                    )
                
                with col2:
                    st.metric(
                        label="Booking Aset", 
                        value=stats.get('total_asset_bookings', 0),
                        delta="Total"
                    )
                
                with col3:
                    st.metric(
                        label="Booking Kendaraan", 
                        value=stats.get('total_vehicle_bookings', 0),
                        delta="Total"
                    )
                
                with col4:
                    total_all = (stats.get('total_room_bookings', 0) + 
                            stats.get('total_asset_bookings', 0) + 
                            stats.get('total_vehicle_bookings', 0))
                    st.metric(
                        label="Total Semua Booking", 
                        value=total_all,
                        delta="Semua Disetujui"
                    )
            
            # Export Data Booking
            st.markdown("---")
            st.markdown("#### Export Data Booking")
            
            # Card untuk export semua booking
            with st.container():
                st.markdown("##### Export Semua Data Booking")
                st.markdown("Download semua data booking dalam satu file CSV.")
                
                col_export1, col_export2 = st.columns([3, 1])
                
                with col_export1:
                    st.info("File berisi semua data booking ruangan, aset, dan kendaraan.")
                
                with col_export2:
                    if st.button("Export Semua", key="export_all_csv", use_container_width=True):
                        with st.spinner("Sedang mengexport data..."):
                            if db.export_bookings_to_csv("booking_lengkap.csv"):
                                st.success("Data berhasil diexport!")
                                
                                # Tombol download
                                try:
                                    with open("booking_lengkap.csv", "rb") as file:
                                        st.download_button(
                                            label="Download File CSV",
                                            data=file,
                                            file_name=f"booking_lengkap_{date.today()}.csv",
                                            mime="text/csv",
                                            use_container_width=True
                                        )
                                except:
                                    st.info("File berhasil dibuat")
                            else:
                                st.error("Gagal mengexport data")
            
            # Export Data Harian
            with st.container():
                st.markdown("##### Export Data Harian")
                st.markdown("Download data booking untuk tanggal tertentu.")
                
                col_date1, col_date2, col_date3 = st.columns([2, 2, 1])
                
                with col_date1:
                    selected_date = st.date_input(
                        "Pilih Tanggal",
                        date.today(),
                        key="export_date",
                        help="Pilih tanggal untuk export data harian"
                    )
                
                with col_date2:
                    st.markdown("")
                    st.markdown("")
                    st.info(f"Data untuk: **{selected_date}**")
                
                with col_date3:
                    st.markdown("")
                    st.markdown("")
                    if st.button("Export Harian", key="export_daily_csv", use_container_width=True):
                        with st.spinner(f"Mengexport data {selected_date}..."):
                            file_name = f"booking_{selected_date}.csv"
                            if db.export_daily_bookings(str(selected_date), file_name):
                                st.success(f"Data {selected_date} berhasil diexport!")
                                
                                # Tombol download
                                try:
                                    with open(file_name, "rb") as file:
                                        st.download_button(
                                            label=f"Download {selected_date}",
                                            data=file,
                                            file_name=file_name,
                                            mime="text/csv",
                                            use_container_width=True
                                        )
                                except:
                                    st.info(f"File berhasil dibuat: {file_name}")
                            else:
                                st.info(f"Tidak ada data untuk tanggal {selected_date}")
            
            # Export Statistik
            st.markdown("---")
            st.markdown("#### Export Statistik")
            
            with st.container():
                col_stats1, col_stats2 = st.columns([3, 1])
                
                with col_stats1:
                    st.markdown("##### Statistik Sistem")
                    
                    # Tampilkan statistik dalam bentuk tabel kecil
                    stats_data = {
                        "Metric": [
                            "Total Booking Ruangan",
                            "Total Booking Aset", 
                            "Total Booking Kendaraan",
                            "Total Semua Booking"
                        ],
                        "Value": [
                            str(stats.get('total_room_bookings', 0)),
                            str(stats.get('total_asset_bookings', 0)),
                            str(stats.get('total_vehicle_bookings', 0)),
                            str(stats.get('total_room_bookings', 0) + 
                            stats.get('total_asset_bookings', 0) + 
                            stats.get('total_vehicle_bookings', 0))
                        ]
                    }
                    
                    stats_df_display = pd.DataFrame(stats_data)
                    st.dataframe(stats_df_display, use_container_width=True, hide_index=True)
                
                with col_stats2:
                    st.markdown("")
                    st.markdown("")
                    if st.button("Export Statistik", key="export_stats_csv", use_container_width=True):
                        try:
                            # Buat DataFrame yang lebih lengkap untuk export
                            export_stats = {
                                "Waktu Export": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                                "Total Booking Ruangan": [stats.get('total_room_bookings', 0)],
                                "Total Booking Aset": [stats.get('total_asset_bookings', 0)],
                                "Total Booking Kendaraan": [stats.get('total_vehicle_bookings', 0)],
                                "Total Semua Booking": [stats.get('total_room_bookings', 0) + 
                                                    stats.get('total_asset_bookings', 0) + 
                                                    stats.get('total_vehicle_bookings', 0)],
                                "Ruangan Paling Banyak Dipesan": [stats.get('most_booked_room', 'Belum ada')],
                                "Aset Paling Banyak Dipinjam": [stats.get('most_booked_asset', 'Belum ada')]
                            }
                            
                            stats_df = pd.DataFrame(export_stats)
                            stats_df.to_csv('statistik_sistem.csv', index=False)
                            
                            st.success("Statistik berhasil diexport!")
                            
                            # Tombol download
                            with open('statistik_sistem.csv', 'rb') as file:
                                st.download_button(
                                    label="Download Statistik",
                                    data=file,
                                    file_name=f"statistik_sistem_{date.today()}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
            
            # Fallback jika error
            st.markdown("---")
            st.markdown("#### Export Data Booking")
            
            with st.container():
                st.warning("Tidak dapat memuat statistik. Anda masih bisa export data booking.")
                
                if st.button("Export Semua Data Booking", key="export_all_fallback", use_container_width=True):
                    with st.spinner("Sedang mengexport data..."):
                        if db.export_bookings_to_csv("booking_lengkap.csv"):
                            st.success("Data berhasil diexport!")
                            
                            try:
                                with open("booking_lengkap.csv", "rb") as file:
                                    st.download_button(
                                        label="Download CSV",
                                        data=file,
                                        file_name="booking_lengkap.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                            except:
                                st.info("File berhasil dibuat")

# ============================================================================
# HALAMAN PROFIL
# ============================================================================
def show_profil():
    show_navbar()
    
    user = st.session_state.user
    
    st.markdown(f"""
    <div class="profile-header-card">
        <div class="profile-avatar">{user['name'][0].upper()}</div>
        <h2 style="text-align: center; font-size: 2rem; margin-bottom: 0.5rem; color: white;">
            {user['name']}
        </h2>
        <p style="text-align: center; font-size: 1.1rem; opacity: 0.9; margin-bottom: 0.25rem; color: white;">
            {user['role'].upper()} • Login dengan IP: {user['username']}
        </p>
        <p style="text-align: center; font-size: 1rem; opacity: 0.8; color: white;">
            KPP Pratama Jombang
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informasi Pengguna
    st.markdown("### Informasi Detail")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="profile-info-card">
            <div class="profile-info-label">Nama Lengkap</div>
            <div class="profile-info-value">{user['name']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="profile-info-card">
            <div class="profile-info-label">Nomor IP</div>
            <div class="profile-info-value">{user['username']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="profile-info-card">
            <div class="profile-info-label">Hak Akses Sistem</div>
            <div class="profile-info-value">{user['role'].upper()}</div>
        </div>
        """, unsafe_allow_html=True)
    

# ============================================================================
# HALAMAN JADWAL 
# ============================================================================
def show_jadwal():
    show_navbar()
    
    st.markdown("""
    <div class="card">
        <div class="card-header">Jadwal Pemesanan (Semua User)</div>
        <div class="card-body">
            <p>Menampilkan jadwal booking <strong>semua pengguna</strong> pada tanggal yang dipilih.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pilih tanggal
    selected_date = st.date_input(
        "Pilih Tanggal", 
        date.today(), 
        key="schedule_date_input"
    )
    
    # Tampilkan jadwal berdasarkan jenis
    tab1, tab2, tab3 = st.tabs(["Ruangan", "Aset", "Kendaraan"])
    
    with tab1:
        st.markdown(f"### Jadwal Ruangan - {selected_date}")
        
        try:
            room_df, _, _ = db.get_all_bookings()
            
            if not room_df.empty:
                # Filter untuk tanggal yang dipilih
                filtered_df = room_df[room_df['date'] == str(selected_date)]
                
                if not filtered_df.empty:
                    # Gunakan requester_name jika ada dan bukan None/NaN, jika tidak gunakan user_name
                    filtered_df['display_name'] = filtered_df.apply(
                        lambda row: row['requester_name'] if pd.notna(row['requester_name']) and row['requester_name'].strip() != '' else row['user_name'], 
                        axis=1
                    )
                    
                    # Hapus baris yang tidak memiliki nama pemesan
                    filtered_df = filtered_df[filtered_df['display_name'].notna()]
                    
                    # Format dataframe untuk ditampilkan
                    display_df = filtered_df[['item_name', 'start_time', 'end_time', 'display_name', 'purpose', 'status']].copy()
                    display_df.columns = ['Ruangan', 'Jam Mulai', 'Jam Selesai', 'Pemesan', 'Keperluan', 'Status']
                    
                    # Format status
                    display_df['Status'] = display_df['Status'].apply(lambda x: str(x).capitalize() if pd.notna(x) else '')
                    
                    # Urutkan berdasarkan jam mulai
                    display_df = display_df.sort_values('Jam Mulai')
                    
                    st.dataframe(display_df, use_container_width=True, height=400)
                else:
                    st.info(f"Tidak ada jadwal ruangan untuk tanggal {selected_date}.")
            else:
                st.info("Belum ada data booking ruangan di sistem.")
                
        except Exception as e:
            st.error(f"Error loading room schedule: {str(e)}")
            st.info("Belum ada data jadwal ruangan.")
    
    with tab2:
        st.markdown(f"### Jadwal Aset Elektronik - {selected_date}")
        
        try:
            _, asset_df, _ = db.get_all_bookings()
            
            if not asset_df.empty:
                # Filter untuk tanggal yang dipilih - Aset dipinjam jika selected_date antara date dan return_date
                if 'date' in asset_df.columns and 'return_date' in asset_df.columns:
                    filtered_df = asset_df[
                        (asset_df['date'] <= str(selected_date)) & 
                        (asset_df['return_date'] >= str(selected_date))
                    ]
                    
                    if not filtered_df.empty:
                        # Gunakan requester_name jika ada dan bukan None/NaN, jika tidak gunakan user_name
                        filtered_df['display_name'] = filtered_df.apply(
                            lambda row: row['requester_name'] if pd.notna(row['requester_name']) and row['requester_name'].strip() != '' else row['user_name'], 
                            axis=1
                        )
                        
                        # Hapus baris yang tidak memiliki nama pemesan
                        filtered_df = filtered_df[filtered_df['display_name'].notna()]
                        
                        # Format dataframe untuk ditampilkan
                        display_df = filtered_df[['item_name', 'date', 'return_date', 'display_name', 'purpose', 'status']].copy()
                        display_df.columns = ['Aset', 'Tanggal Pinjam', 'Tanggal Kembali', 'Pemesan', 'Keperluan', 'Status']
                        
                        # Format status
                        display_df['Status'] = display_df['Status'].apply(lambda x: str(x).capitalize() if pd.notna(x) else '')
                        
                        # Urutkan berdasarkan tanggal pinjam
                        display_df = display_df.sort_values('Tanggal Pinjam')
                        
                        st.dataframe(display_df, use_container_width=True, height=400)
                    else:
                        st.info(f"Tidak ada aset yang dipinjam pada tanggal {selected_date}.")
                else:
                    st.warning("Format data aset tidak sesuai")
                    st.info("Tidak ada data peminjaman aset.")
            else:
                st.info("Belum ada data peminjaman aset di sistem.")
                
        except Exception as e:
            st.error(f"Error loading asset schedule: {str(e)}")
            st.info("Belum ada data peminjaman aset.")
    
    with tab3:
        st.markdown(f"### Jadwal Kendaraan Dinas - {selected_date}")
        
        try:
            _, _, vehicle_df = db.get_all_bookings()
            
            if not vehicle_df.empty:
                # Filter untuk tanggal yang dipilih
                if 'date' in vehicle_df.columns:
                    filtered_df = vehicle_df[vehicle_df['date'] == str(selected_date)]
                    
                    if not filtered_df.empty:
                        # Gunakan requester_name jika ada dan bukan None/NaN, jika tidak gunakan user_name
                        filtered_df['display_name'] = filtered_df.apply(
                            lambda row: row['requester_name'] if pd.notna(row['requester_name']) and row['requester_name'].strip() != '' else row['user_name'], 
                            axis=1
                        )
                        
                        # Hapus baris yang tidak memiliki nama pemesan
                        filtered_df = filtered_df[filtered_df['display_name'].notna()]
                        
                        # Format dataframe untuk ditampilkan
                        display_df = filtered_df[['item_name', 'start_time', 'end_time', 'display_name', 'destination', 'purpose', 'status']].copy()
                        display_df.columns = ['Kendaraan', 'Jam Mulai', 'Jam Selesai', 'Pemesan', 'Tujuan', 'Keperluan', 'Status']
                        
                        # Format status
                        display_df['Status'] = display_df['Status'].apply(lambda x: str(x).capitalize() if pd.notna(x) else '')
                        
                        # Urutkan berdasarkan jam mulai
                        display_df = display_df.sort_values('Jam Mulai')
                        
                        st.dataframe(display_df, use_container_width=True, height=400)
                    else:
                        st.info(f"Tidak ada kendaraan yang dipesan pada tanggal {selected_date}.")
                else:
                    st.warning("Format data kendaraan tidak sesuai")
                    st.info("Tidak ada data pemesanan kendaraan.")
            else:
                st.info("Belum ada data pemesanan kendaraan di sistem.")
                
        except Exception as e:
            st.error(f"Error loading vehicle schedule: {str(e)}")
            st.info("Belum ada data pemesanan kendaraan.")

# ============================================================================
# HALAMAN STATISTIK
# ============================================================================
def show_statistik():
    show_navbar()
    
    st.markdown("""
    <div class="card">
        <div class="card-header">Statistik dan Analisis</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        stats = db.get_statistics()
        
        with col1:
            total_all = (stats.get('total_room_bookings', 0) + 
                        stats.get('total_asset_bookings', 0) + 
                        stats.get('total_vehicle_bookings', 0))
            st.metric("Total Pemesanan", str(total_all))
        
        with col2:
            pending_all = (stats.get('pending_room', 0) + 
                          stats.get('pending_asset', 0) + 
                          stats.get('pending_vehicle', 0))
            st.metric("Menunggu Persetujuan", str(pending_all))
        
        with col3:
            # Hitung persentase yang sudah disetujui
            total_approved = total_all - pending_all if total_all > 0 else 0
            approved_rate = round((total_approved / total_all * 100) if total_all > 0 else 0, 1)
            st.metric("Tingkat Persetujuan", f"{approved_rate}%")
        
        with col4:
            # Rating berdasarkan jumlah pemesanan yang disetujui
            if total_approved > 20:
                rating = 4.8
            elif total_approved > 10:
                rating = 4.5
            elif total_approved > 5:
                rating = 4.2
            elif total_approved > 0:
                rating = 4.0
            else:
                rating = 0.0
            st.metric("Kepuasan Pengguna", f"{rating}", "/ 5.0")
    
    except:
        # Data default jika error
        with col1:
            st.metric("Total Pemesanan", "0")
        with col2:
            st.metric("Menunggu Persetujuan", "0")
        with col3:
            st.metric("Tingkat Persetujuan", "0%")
        with col4:
            st.metric("Kepuasan Pengguna", "0", "/ 5.0")

# ============================================================================
# MAIN ROUTING
# ============================================================================
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        page = st.session_state.page
        
        if page == 'home':
            show_home()
        elif page == 'booking':
            show_booking()
        elif page == 'jadwal':
            show_jadwal()
        elif page == 'riwayat':
            show_riwayat()
        elif page == 'profil':
            show_profil()
        elif page == 'admin':
            show_admin()
        elif page == 'statistik':
            show_statistik()
        else:
            show_home()

if __name__ == "__main__":
    main()
import pandas as pd
from sqlalchemy import create_engine
import os


DB_CONNECTION = "postgresql+psycopg2://neondb_owner:npg_uvp8yjWcd3CY@ep-super-dew-a4n08cv4-pooler.\
us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require" 

def get_base_dir():
    # Logika Path Robust (Local & Airflow Friendly)
    if os.getenv("AIRFLOW_HOME"):
        return "/opt/airflow"
    
    # Fallback Local: Ambil lokasi script ini, naik 2 level ke root project
    # scripts/3_load.py -> scripts -> project_root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load():
    print("=== LOAD: Upload ke Neon DB (Pandas) ===")
    
    # Validasi Config
    if "PASTE_YOUR" in DB_CONNECTION:
        print("❌ ERROR CRITICAL: Anda belum mengisi DB_CONNECTION di script 3_load.py!")
        print("   Silakan edit file ini dan masukkan URL Database Neon Anda.")
        return

    base_dir = get_base_dir()
    processed_dir = os.path.join(base_dir, "data", "processed")
    print(f"Reading data from: {processed_dir}")
    
    # Tes Koneksi Dulu
    try:
        engine = create_engine(DB_CONNECTION)
        with engine.connect() as conn:
            print("✓ Koneksi Database Berhasil (Neon DB Connected)")
    except Exception as e:
        print(f"❌ Koneksi Gagal: {e}")
        print("   Cek URL, Password, atau Firewall Anda.")
        return

    # Urutan Load (Parent Table dulu, baru Child Table)
    tables = [
        "dim_city", 
        "dim_merchant", 
        "dim_date", 
        "dim_user",       # Foreign Key ke City
        "dim_card",       # Foreign Key ke User
        "fact_transaction" # Foreign Key ke semua di atas
    ]
    
    for table_name in tables:
        file_path = os.path.join(processed_dir, f"{table_name}.csv")
        
        if not os.path.exists(file_path):
            print(f"⚠️ SKIP: {table_name}.csv tidak ditemukan.")
            continue
            
        print(f"Processing {table_name}...")
        
        # Batch reading dari CSV (Hemat RAM Laptop)
        # 50k baris per batch baca CSV
        csv_chunk_size = 50000 
        
        try:
            with pd.read_csv(file_path, chunksize=csv_chunk_size) as reader:
                for i, chunk in enumerate(reader):
                    # Progress indicator yang rapi (overwrite line)
                    print(f"  -> Uploading batch {i+1}...", end="\r")
                    
                    # Upload ke SQL
                    chunk.to_sql(
                        name=table_name,
                        con=engine,
                        if_exists='append', # Menambahkan data ke tabel yg sudah ada
                        index=False,
                        method='multi',     # Insert banyak baris sekaligus (INSERT INTO VALUES (...), (...))
                        chunksize=500       # 500 baris per satu query INSERT (Biar gak timeout)
                    )
            print(f"\n✓ Sukses upload: {table_name}")
            
        except Exception as e:
            print(f"\n❌ Error upload {table_name}: {e}")
            # Opsional: Uncomment baris bawah jika ingin stop total saat ada error
            # return 

if __name__ == "__main__":
    load()
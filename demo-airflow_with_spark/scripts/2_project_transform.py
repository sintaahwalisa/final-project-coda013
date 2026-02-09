import pandas as pd
import numpy as np
import os
import shutil

def get_base_dir():
    # 1. Cek apakah kita sedang di dalam Airflow Container?
    # Biasanya Airflow punya env var 'AIRFLOW_HOME' = /opt/airflow
    if os.getenv("AIRFLOW_HOME"):
        return "/opt/airflow"
    
    # 2. Cek apakah kita di dalam Docker image tertentu?
    # Kita bisa set ENV sendiri di Dockerfile, misal APP_ENV=docker
    if os.getenv("APP_ENV") == "docker":
        return "/opt/airflow"
    
    # 3. Fallback ke Local PC (Windows/Mac)
    # Patokannya adalah lokasi file script ini berada.
    # Naik 1 level dari folder 'scripts' ke root project.
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def transform():
    print("=== TRANSFORM: Data Modeling (Pandas Version) ===")
    
    base_dir = get_base_dir()
    input_path = os.path.join(base_dir, "data", "credit_card_transactions.csv")
    output_dir = os.path.join(base_dir, "data", "processed")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print("Reading CSV data...")
    
    df = pd.read_csv(input_path, parse_dates=['trans_date_trans_time', 'dob'])

    # ==========================================
    # 1. Dimensi Date (Calendar 2018-2026)
    # ==========================================
    print("Processing Dim Date...")
    # Generate range tanggal
    dates = pd.date_range(start='2019-01-01', end='2026-12-31')
    dim_date = pd.DataFrame({'full_date': dates})
    
    # Extract komponen tanggal
    dim_date['date_id'] = dim_date['full_date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['day_name'] = dim_date['full_date'].dt.day_name()
    dim_date['day_of_week'] = dim_date['full_date'].dt.dayofweek + 1 # Pandas 0=Monday
    dim_date['day_of_month'] = dim_date['full_date'].dt.day
    dim_date['month_name'] = dim_date['full_date'].dt.month_name()
    dim_date['month'] = dim_date['full_date'].dt.month
    dim_date['year'] = dim_date['full_date'].dt.year
    dim_date['quarter'] = dim_date['full_date'].dt.quarter
    dim_date['is_weekend'] = dim_date['day_of_week'].isin([6, 7]) # 6=Sat, 7=Sun

    # ==========================================
    # 2. Dimensi City
    # ==========================================
    print("Processing Dim City...")
    # Ambil kolom unik
    dim_city = df[['city', 'state', 'city_pop']].drop_duplicates().reset_index(drop=True)
    dim_city = dim_city.rename(columns={'city': 'city_name', 'city_pop': 'population'})
    # Generate ID (1, 2, 3...)
    dim_city['city_id'] = dim_city.index + 1

    # ==========================================
    # 3. Dimensi User
    # ==========================================
    print("Processing Dim User...")
    user_cols = ['first', 'last', 'dob', 'job', 'gender', 'street', 'zip', 'city', 'state']
    dim_user = df[user_cols].drop_duplicates().reset_index(drop=True)
    
    # Join ke City untuk dapat city_id
    dim_user = dim_user.merge(dim_city, left_on=['city', 'state'], right_on=['city_name', 'state'], how='left')
    
    # Rename & Select
    dim_user = dim_user.rename(columns={
        'first': 'first_name', 'last': 'last_name', 'zip': 'zip_code'
    })
    dim_user = dim_user[['first_name', 'last_name', 'dob', 'job', 'gender', 'street', 'zip_code', 'city_id']]
    # Generate ID
    dim_user['user_id'] = dim_user.index + 1

    # ==========================================
    # 4. Dimensi Merchant
    # ==========================================
    print("Processing Dim Merchant...")
    merch_cols = ['merchant', 'merch_lat', 'merch_long', 'merch_zipcode']

    # Bersihkan prefix "fraud_"
    df['merchant'] = df['merchant'].str.replace('fraud_', '', regex=False)
    
    # Ambil unik
    dim_merchant = df[merch_cols].drop_duplicates()
    
    # PENTING: Karena kita join pakai nama 'merchant', 
    # satu nama merchant TIDAK BOLEH punya banyak baris (misal beda lokasi dianggap beda merchant).
    # Untuk simplifikasi Data Warehouse, kita ambil satu saja per nama.
    dim_merchant = dim_merchant.drop_duplicates(subset=['merchant']) 
    
    dim_merchant = dim_merchant.reset_index(drop=True)
    dim_merchant = dim_merchant.rename(columns={'merchant': 'merch_name'})
    dim_merchant['merch_id'] = dim_merchant.index + 1

    # ==========================================
    # 5. Dimensi Card
    # ==========================================
    print("Processing Dim Card...")
    card_cols = ['cc_num', 'first', 'last', 'dob']
    dim_card = df[card_cols].drop_duplicates().reset_index(drop=True)
    
    # Join ke User untuk dapat user_id
    # Hati-hati: Merge di pandas butuh nama kolom kiri & kanan
    dim_card = dim_card.merge(
        dim_user, 
        left_on=['first', 'last', 'dob'], 
        right_on=['first_name', 'last_name', 'dob'], 
        how='left'
    )
    
    dim_card = dim_card[['cc_num', 'user_id']].rename(columns={'cc_num': 'cc_number'})
    # Card ID pakai cc_number asli (sudah unique di source)

    # ==========================================
    # 6. Fact Transaction
    # ==========================================
    print("Processing Fact Transaction...")
    # Kita copy df biar aman
    fact = df.copy()
    
    #Convert is_fraud to boolean
    fact['is_fraud'] = fact['is_fraud'].astype(bool) 

    # Join Merchant ID
    fact = fact.merge(dim_merchant, left_on='merchant', right_on='merch_name', how='left')
    
    # Generate Date ID (YYYYMMDD)
    fact['date_id'] = fact['trans_date_trans_time'].dt.strftime('%Y%m%d').astype(int)
    
    # Select & Rename
    fact_final = fact[[
        'trans_num', 'trans_date_trans_time', 'date_id', 'cc_num', 
        'merch_id', 'amt', 'is_fraud', 'category', 'lat', 'long'
    ]].rename(columns={
        'trans_num': 'trx_id',
        'trans_date_trans_time': 'trx_timestamp',
        'cc_num': 'cc_number',
        'merch_id': 'merchant_id',
        'lat': 'latitude',
        'long': 'longitude'
    })

    # ==========================================
    # Saving
    # ==========================================
    def save_csv(dataframe, filename):
        path = os.path.join(output_dir, filename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"Saving {filename}...")
        dataframe.to_csv(path, index=False)

    save_csv(dim_city, "dim_city.csv")
    save_csv(dim_user, "dim_user.csv")
    save_csv(dim_merchant, "dim_merchant.csv")
    save_csv(dim_card, "dim_card.csv")
    save_csv(dim_date, "dim_date.csv")
    save_csv(fact_final, "fact_transaction.csv")
    
    print(f"✓ Transform selesai. Output di: {output_dir}")

if __name__ == "__main__":
    transform()
import os
import pandas as pd
import kagglehub

# ================= CONFIG =================
DATASET_NAME = "priyamchoksi/credit-card-transactions-dataset"
CSV_FILENAME = "credit_card_transactions.csv"  # ⚠️ sesuaikan jika nama berbeda


OUTPUT_DIR = os.getenv("AIRFLOW_DATA_DIR", "/opt/airflow/data")
DATASET_ROOT_DIR = OUTPUT_DIR
OUTPUT_FILE = f"{OUTPUT_DIR}/extract_result_credit_card_pipeline.csv"


# ================= EXTRACT FUNCTION =================
def extract_data(output_path: str) -> pd.DataFrame:
    """
    Extract credit card transaction dataset from Kaggle
    """

    # 1. Download dataset
    dataset_path = kagglehub.dataset_download(DATASET_NAME)
    print("📂 Dataset downloaded to:", dataset_path)

    # 2. Prepare local dataset directory
    os.makedirs(DATASET_ROOT_DIR, exist_ok=True)
    os.system(f"cp -r {dataset_path}/* {DATASET_ROOT_DIR}")

    # 3. Read CSV
    file_path = os.path.join(DATASET_ROOT_DIR, CSV_FILENAME)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ CSV file not found: {file_path}")


# ================= MAIN =================
if __name__ == "__main__":
    extract_data(OUTPUT_FILE)

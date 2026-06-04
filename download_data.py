import os
import gdown

# Direct download URL (works with all gdown versions)
FILE_ID    = "1ss4ehLrhb5_X_RlEK7npanh5wfwEIm1V"
GDRIVE_URL = f"https://drive.google.com/uc?id={FILE_ID}"
OUTPUT_PATH = "data/top50_us.csv"

def download():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(OUTPUT_PATH):
        print(f"Dataset already exists at {OUTPUT_PATH}. Skipping download.")
        return
    print("Downloading dataset from Google Drive...")
    try:
        # Try with fuzzy first (gdown >= 4.4.0)
        gdown.download(GDRIVE_URL, OUTPUT_PATH, fuzzy=True, quiet=False)
    except TypeError:
        # Fallback for older gdown versions
        gdown.download(GDRIVE_URL, OUTPUT_PATH, quiet=False)
    print(f"Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    download()
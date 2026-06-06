import os
import zipfile
import glob

BASE_DIR = "/home/cbwinslow/workspace/government/financial-disclosures"
EXTRACT_DIR = os.path.join(BASE_DIR, "extracted")

def extract_zips():
    if not os.path.exists(EXTRACT_DIR):
        os.makedirs(EXTRACT_DIR)

    zip_files = glob.glob(os.path.join(BASE_DIR, "*FD.zip"))
    
    if not zip_files:
        print("No *FD.zip files found in", BASE_DIR)
        return

    print(f"Found {len(zip_files)} zip files. Extracting...")
    
    for zip_path in zip_files:
        filename = os.path.basename(zip_path)
        year = filename.replace("FD.zip", "")
        
        target_dir = os.path.join(EXTRACT_DIR, year)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        print(f"Extracting {filename} to {target_dir}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        except Exception as e:
            print(f"Error extracting {filename}: {e}")
            
    print("Extraction complete!")

if __name__ == "__main__":
    extract_zips()

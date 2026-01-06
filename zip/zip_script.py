import os
import zipfile

def zipSfEgres():
    folder = os.path.dirname(os.path.dirname(__file__))
    zip_path = os.path.join(os.path.dirname(__file__), "sf_egres_blender.zip")
    sf_egres_path = os.path.join(folder, "sf_egres_blender")

    if not os.path.isdir(sf_egres_path):
        raise Exception("Not found:", sf_egres_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(sf_egres_path):
            if "__pycache__" in file_name: continue
            real_path = os.path.join(sf_egres_path, file_name)
            relative_path = os.path.join("sf_egres_blender", file_name)
            zipf.write(real_path, relative_path)
            print(f"Wrote {relative_path}")

if __name__ == "__main__":
    zipSfEgres()

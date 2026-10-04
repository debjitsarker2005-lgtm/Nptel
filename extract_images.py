from pypdf import PdfReader
import os

os.makedirs("assignments/extracted_images", exist_ok=True)

for fname in ["Ml_Assignment2.pdf", "ML Solution_1.pdf"]:
    reader = PdfReader(f"assignments/{fname}")
    img_count = 0
    for page_idx, page in enumerate(reader.pages):
        for img_name, img_obj in page.images.items():
            img_count += 1
            safe_name = img_name.replace("/", "_").replace("\\", "_")
            out_path = f"assignments/extracted_images/{fname}_{page_idx+1}_{safe_name}.png"
            with open(out_path, "wb") as f:
                f.write(img_obj.data)
    print(f"{fname}: extracted {img_count} images")

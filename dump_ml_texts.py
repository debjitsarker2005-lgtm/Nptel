import os
import sys
import docx
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

for fname in ["Assignment 5.pdf", "Assignment 6.pdf", "Assignment 7.pdf", "Assignment 8_ML.pdf", "ML_Assignment4.docx"]:
    path = os.path.join("assignments", fname)
    out_name = fname.replace(".pdf", ".txt").replace(".docx", ".txt")
    if fname.endswith(".docx"):
        doc = docx.Document(path)
        content = "\n".join([p.text for p in doc.paragraphs])
    else:
        reader = PdfReader(path)
        content = "\n".join([(p.extract_text() or "") for p in reader.pages])
    
    with open(f"assignments/{out_name}", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Dumped {out_name} ({len(content)} chars)")

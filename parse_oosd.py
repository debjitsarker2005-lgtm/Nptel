import re
import json

with open("assignments/OOSD_2026_All_Assignments_Interactive_Quiz_MCQ_MSQ.html", "r", encoding="utf-8") as f:
    text = f.read()

match = re.search(r'const\s+QUESTIONS\s*=\s*(\[\s*\{.*?\}\s*\]);\s*const\s+STORAGE_KEY', text, re.DOTALL)
if match:
    raw_json = match.group(1)
    questions = json.loads(raw_json)
    print(f"Successfully extracted {len(questions)} OOSD questions!")
    with open("data_oosd.json", "w", encoding="utf-8") as out:
        json.dump(questions, out, indent=2)
else:
    idx = text.find("const QUESTIONS = ")
    print("Found idx:", idx)
    if idx != -1:
        end = text.find(";\nconst STORAGE_KEY", idx)
        if end == -1:
            end = text.find(";\r\nconst STORAGE_KEY", idx)
        raw_json = text[idx + len("const QUESTIONS = "):end]
        questions = json.loads(raw_json)
        print(f"Fallback extracted {len(questions)} OOSD questions!")
        with open("data_oosd.json", "w", encoding="utf-8") as out:
            json.dump(questions, out, indent=2)

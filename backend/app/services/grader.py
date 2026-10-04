from typing import Dict, Any, Union, List

def grade_question(q: Dict[str, Any], selected: Union[List[str], float, str, None]) -> Dict[str, Any]:
    marks = q.get("marks", 1.0)
    neg = q.get("negative_marks", 0.0)
    q_type = q.get("type", "MCQ")
    correct = q.get("correct", [])

    if selected is None:
        return {"is_correct": False, "marks_awarded": 0.0, "status": "skipped"}

    if q_type == "MCQ" or q_type == "TRUE_FALSE":
        user_choice = selected[0] if isinstance(selected, list) and len(selected) > 0 else selected
        target = correct[0] if len(correct) > 0 else None
        if user_choice == target:
            return {"is_correct": True, "marks_awarded": marks, "status": "correct"}
        return {"is_correct": False, "marks_awarded": -neg, "status": "incorrect"}

    if q_type == "MSQ":
        user_set = set(selected) if isinstance(selected, list) else {selected}
        target_set = set(correct)
        
        # In NPTEL MSQ: Any wrong option chosen gives 0 or negative
        if user_set - target_set:
            return {"is_correct": False, "marks_awarded": -neg, "status": "incorrect"}
        
        # If perfect match
        if user_set == target_set:
            return {"is_correct": True, "marks_awarded": marks, "status": "correct"}
        
        # Partial marking if subset of correct options chosen with no wrong ones
        partial = marks * (len(user_set) / max(1, len(target_set)))
        return {"is_correct": False, "marks_awarded": round(partial, 2), "status": "partial"}

    if q_type == "NUMERIC":
        try:
            val = float(selected)
            target = q.get("numeric_answer", {}).get("value", 0.0)
            tol = q.get("numeric_answer", {}).get("tolerance", 0.0)
            if abs(val - target) <= tol:
                return {"is_correct": True, "marks_awarded": marks, "status": "correct"}
            return {"is_correct": False, "marks_awarded": 0.0, "status": "incorrect"}
        except (ValueError, TypeError):
            return {"is_correct": False, "marks_awarded": 0.0, "status": "incorrect"}

    return {"is_correct": False, "marks_awarded": 0.0, "status": "unsupported"}

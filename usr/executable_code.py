def scholarship_priority(student):
    if student.get("minority_group") == "X":
        return "Priority"
    elif student.get("minority_group") == "Y":
        return "Standard"
    return None

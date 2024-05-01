marathi_marks = {
    'student_a': 30,
    'student_b': 40,
    'student_c': 50,
}

english_marks = {
    'student_b': 60,
    'student_a': 50,
    'student_c': 20,
}

hindi_marks = {
    'student_c': 30,
    'student_a': 10,
    'student_b': 20,
}

total_marks = {
    'student_a': marathi_marks.get("student_a") + english_marks.get("student_a") + hindi_marks.get("student_a"),
    'student_b': marathi_marks.get("student_b") + english_marks.get("student_b") + hindi_marks.get("student_b"),
    'student_c': marathi_marks.get("student_c") + english_marks.get("student_c") + hindi_marks.get("student_c"),
}


print("total_marks",total_marks)
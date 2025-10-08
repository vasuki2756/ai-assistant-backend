#!/usr/bin/env python3

students_db = [
    {
        'name': 'Alice Johnson',
        'regNo': 'CS2024001',
        'reg_no': 'CS2024001',
        'regno': 'CS2024001',
        'photoPath': 'photos/alice.jpg',
        'photo_path': 'photos/alice.jpg',
        'major': 'Computer Science',
        'year': '3rd Year'
    },
    {
        'name': 'Bob Smith',
        'regNo': 'EE2024002',
        'reg_no': 'EE2024002',
        'regno': 'EE2024002',
        'photoPath': 'photos/bob.jpg',
        'photo_path': 'photos/bob.jpg',
        'major': 'Electrical Engineering',
        'year': '2nd Year'
    },
    {
        'name': 'Carol Davis',
        'regNo': 'ME2024003',
        'reg_no': 'ME2024003',
        'regno': 'ME2024003',
        'photoPath': 'photos/carol.jpg',
        'photo_path': 'photos/carol.jpg',
        'major': 'Mechanical Engineering',
        'year': '4th Year'
    },
    {
        'name': 'David Wilson',
        'regNo': 'CS2024004',
        'reg_no': 'CS2024004',
        'regno': 'CS2024004',
        'photoPath': 'photos/david.jpg',
        'photo_path': 'photos/david.jpg',
        'major': 'Computer Science',
        'year': '1st Year'
    },
    {
        'name': 'Emma Brown',
        'regNo': 'BT2024005',
        'reg_no': 'BT2024005',
        'regno': 'BT2024005',
        'photoPath': 'photos/emma.jpg',
        'photo_path': 'photos/emma.jpg',
        'major': 'Biotechnology',
        'year': '2nd Year'
    }
]

def get_student_by_regno(regno: str):
    for student in students_db:
        if student.get('regNo') == regno or student.get('reg_no') == regno or student.get('regno') == regno:
            return student
    return None

def get_student_by_name(name: str):
    for student in students_db:
        if student.get('name', '').lower() == name.lower():
            return student
    return None

def add_student(student_data: dict):
    students_db.append(student_data)

def update_student_stress(regno: str, stress_level: float, category: str):
    student = get_student_by_regno(regno)
    if student:
        student['last_stress'] = {
            'level': stress_level,
            'category': category,
            'timestamp': __import__('time').time()
        }

if __name__ == '__main__':
    print(f"Loaded {len(students_db)} students:")
    for student in students_db:
        print(f"- {student['name']} ({student['regNo']})")

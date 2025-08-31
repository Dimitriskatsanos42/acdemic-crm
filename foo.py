import csv
from courses.models import Course
import os
from django.conf import settings

# File path
file_path = os.path.join(settings.BASE_DIR, 'courses', 'data', 'dit_courses.txt')

# Open and read the file
with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        semester_label = "winter" if int(row[1]) % 2 == 1 else "spring"
        Course.objects.update_or_create(
            code=row[0],
            defaults={
                'semester': int(row[1]),
                'semester_label': semester_label,
                'name': row[2],
                'credits': int(row[3]),
            }
        )
print("Courses successfully loaded!")
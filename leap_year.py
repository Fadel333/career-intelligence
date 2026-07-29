def course(course_name):
    return course_name.lower() == "discrete math"

course_name = input("Enter your course name: ")

if course(course_name):
    print("You entered Discrete Math.")
else:
    print("W’akyi gu hɔ bro.")

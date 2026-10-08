class Student:
    def __init__(self, roll_no, name, marks1, marks2, marks3):
        self.roll_no = roll_no
        self.name = name
        self.marks1 = marks1
        self.marks2 = marks2
        self.marks3 = marks3
    
    def calculate_total(self):
        return self.marks1 + self.marks2 + self.marks3

    def calculate_percentage(self):
        total = self.calculate_total()
        perc = (total / 300) * 100
        return perc
    
    def calculate_grade(self):
        perc = self.calculate_percentage()
        if perc >= 90:
            return "A+"
        elif perc >= 75:
            return "A"
        elif perc >= 60:
            return "B"
        elif perc >= 50:
            return "C"
        else:
            return "Fail"
    
    def display_student(self):
        total = self.calculate_total()
        percentage = self.calculate_percentage()
        grade = self.calculate_grade()

        print("-"*45)
        print(f"Roll number : {self.roll_no}")
        print(f"Name        : {self.name}")
        print(f"Marks       : Sub1 = {self.marks1}, Sub2 = {self.marks2}, Sub3 = {self.marks3}")
        print(f"Total Marks : {total} / 300")
        print(f"Percentage  : {percentage:.2f}%")
        print(f"Grade       : {grade}")
        print("-"*45)
    
if __name__ == "__main__":
    print("=" * 45)
    print("      STUDENT RESULT MANAGEMENT SYSTEM      ")
    print("=" * 45)

    student1 = Student(roll_no=101, name="Aarav Sharma", marks1=95, marks2=92, marks3=88)
    student2 = Student(roll_no=102, name="Priya Patel",  marks1=78, marks2=82, marks3=74)
    student3 = Student(roll_no=103, name="Rohan Verma",  marks1=45, marks2=52, marks3=48)
    student4 = Student(roll_no=104, name="Ananya Gupta", marks1=35, marks2=42, marks3=38)
    
    # List of students
    students = [student1, student2, student3, student4]
    
    # Displaying results for all students
    for student in students:
        student.display_student()



# INHERITENCE with Object-Orientated Programming. 
class Person: # Parent class
    def __init__(self, name, age):
        self.m_first_name = name
        self.m_age = age

    def print_name(self):
        return self.m_first_name
    
    def get_age(self):
        return self.m_age
        # print(self.m_first_name, self.m_age)


class Employee(Person):
    def __init__(self, name, age, hourly_salary, employeeID):
        super().__init__(name, age)

        self.m_hourly_salary = hourly_salary
        self.m_employeeID = employeeID

    def print_name_and_salary(self):
        print(f"{self.m_first_name} : £{self.m_hourly_salary}")


class Supervisor(Employee):
    def __init__(self, name, age, hourly_salary, employeeID):
        super().__init__(name, age, hourly_salary, employeeID)
        
        self.m_employeeID = employeeID

    def print_employeeID(self):
        print(f"Employee id: {self.m_employeeID}")


def main():
    
    employee_rigging = Employee("James", 22, 20.50, 197704)
    # employee_rigging.m_first_name = "James" 
    # employee_rigging.m_age = 21 
    print(f"Employee age = {employee_rigging.get_age()}")
    employee_rigging.print_name_and_salary()
    employee_supe = Supervisor("James", 22, 20.50, 197704)
    employee_supe.print_employeeID()

    '''  
    Output:
        Employee age = 22
        James : £20.5
        Employee id: 197704
    '''

main()
# INHERITENCE with Object-Orientated Programming. 
class Person: # Parent class
    def __init__(self, fname, lname):
        self.first_name = fname
        self.last_name = lname

    def print_name(self):
        print(self.first_name, self.last_name)


class Student(Person): # Child class, inherits properties of 'Person' class
    def __init__(self, fname, lname, year): # __init__() overrides the inheritence of the parent's __init__() func. 
        super().__init__(fname, lname) # 'super().' function makes the child class inherite all the methods & properties from its parent. 
        self.graduation_year = year
    
    def welcome(self):
        print(f"Welcome {self.first_name} {self.last_name} to the class of {self.graduation_year}!")


# Calling the 'Student' object
x = Student("James", "Vilela-Slater", 2022)
# Execute the 'print_name()' function/method of the object 'x'
x.print_name()
# Execute the 'welcome()' function/method of the object 'x'
x.welcome()


# --- Polymorphic & Inheritance with OOP ---
''' 
Uaing a simple example of vehicles (Car, Boat, Plane) that all share common 
behaviour but have their own specific properties.

*Use polymorphism when different object types should share a common interface but behave differently.*
-> shares the arguments and behaves differently with 'self.traversal'

'''
class Vehicle():
    def __init__(self, brand, model, name=None):
        self.brand = brand
        self.model = model
        self.name = name
        ''' Each child-class sets self.traversal differently.'''
        self.traversal = ""
    
    ''' 
    Parent method, accesses the atttribute and acts polymorphically. 
    meaning the output differes depending on the type of vehicle - without 
    needing to override 'move()' in each child-class. 
    '''
    def move(self):
        if self.name == None:
            print(f"{self.traversal} the {self.brand} {self.model}!")
        else:
            print(f"{self.traversal} the {self.brand} {self.model} known as the {self.name}!")        
       
''' Avoid code duplication by using Inheritance. Share the method move() '''
class Car(Vehicle):
    def __init__(self, brand, model, name=None):
        super().__init__(brand, model, name)
        self.traversal = "Drive"
        

class Boat(Vehicle):
    def __init__(self, brand, model, name=None):
        super().__init__(brand, model, name)
        self.traversal = "Sail"
   

class Plane(Vehicle):
    def __init__(self, brand, model, name=None):
        super().__init__(brand, model, name)
        self.traversal = "Fly"
  
'''
Example use:
'''
car_1 = Car("Ford", "Mustang")
boat_1 = Boat("White Star Line", "Olympic-class Ocean Liner", "Titanic")
plane_1 = Plane("Supermarine", "Single-seat Fighter Aircraft", "Spitfire")

for x in (car_1, boat_1, plane_1):
   x.move()
# Output: 
    # Drive the Ford Mustang!
    # Sail the White Star Line Olympic-class Ocean Liner known as the Titanic!
    # Fly the Supermarine Single-seat Fighter Aircraft known as the Spitfire!
def add(a,b):
    "adding two numbers"

    return a + b

 

def multiply(a,b):
    "multiplying two numbers"

    return a * b

def main():
    "Main function to run the program"""

num1 = int(input("Enter first number: "))
num2 = int(input("Enter second number: "))
 



 
print("The sum of the two numbers is:", add(num1,num2))
print("The product of the two numbers is:", multiply(num1,num2))

if __name__ == "__main__":
    main
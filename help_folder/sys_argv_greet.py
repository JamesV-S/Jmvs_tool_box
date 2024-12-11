import sys

def greet():
    if len(sys.argv) < 2:
        print("Usage: python greet.py [name]")
        sys.exit(1)

    name = sys.argv[1]
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()

# to run this: `python greet.py Lilirose`
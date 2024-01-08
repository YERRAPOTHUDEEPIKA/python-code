import time

def print_with_delay(text, delay):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def animate_love():
    print("\n\n")
    for _ in range(3):
        print("   ♥    ♥  ")
        time.sleep(0.5)
        print("♥      ♥     ")
        time.sleep(0.5)
        print("   ♥    ♥  ")
        time.sleep(0.5)

def main():
    print_with_delay("Happy Birthday Madhana", 0.1)
    animate_love()
    print("\n\n")

if __name__ == "__main__":
    main()

import sys

def reverse_string(s: str) -> str:
    """
    Return the reverse of the input string `s`.

    Parameters:
        s (str): The string to reverse.

    Returns:
        str: The reversed string.
    """
    return s[::-1]

def main() -> None:
    """
    Main entry point of the script.
    Prompts the user for a string, reverses it, and prints both the original
    and reversed strings.
    """
    if len(sys.argv) > 1:
        # If a string is provided as a command-line argument, use it.
        input_str = " ".join(sys.argv[1:])
    else:
        # Otherwise, prompt the user for input.
        input_str = input("Enter a string to reverse: ")

    reversed_str = reverse_string(input_str)

    print("\n=== String Reversal ===")
    print(f"Original string: {input_str}")
    print(f"Reversed string: {reversed_str}")

if __name__ == "__main__":
    main()

import argparse

def main() -> None:
    """Entry point for the C10 solution."""
    parser = argparse.ArgumentParser(description="C10 solution.")
    parser.add_argument("file_path", help="Path to the input file.")
    args = parser.parse_args()

    unique_numbers = set()
    with open(args.file_path, "r") as f:
        for line in f:
            try:
                unique_numbers.add(int(line.strip()))
            except ValueError:
                # Ignore lines that are not valid integers
                pass

    sorted_numbers = sorted(list(unique_numbers))

    for number in sorted_numbers:
        print(number)

if __name__ == "__main__":
    main()

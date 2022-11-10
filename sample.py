from differ_for_code import differ
import re

def tokenize(code):
    # This tokenization is only for sample.
    # This is insufficient for real-world source code.
    return [ re.split(r"(\s)", line) for line in code.split("\n") ]

def main():
    # read sample source code
    with open("sample_before.py") as f:
        before_code = f.read()
    with open("sample_after.py") as f:
        after_code = f.read()
   
    # tokenize sample source code
    before_tokens = tokenize(before_code)
    after_tokens = tokenize(after_code)

    # calculate difference
    diff = differ.diff(before_tokens, after_tokens)

    # print results
    print("-" * 100)
    print(before_code)
    print("-" * 50)
    print(after_code)
    print("-" * 50)
    print(diff)
    print("-" * 50)
    diff.visualize()
    print("-" * 50)
    distance = diff.get_distance()
    similarity = diff.get_similarity()
    print(f"Distance: {distance}, Similarity: {similarity}")
    print("-" * 100)

if __name__ == "__main__":
    main()

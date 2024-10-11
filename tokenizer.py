from tabulate import tabulate

# Define tokens
KEYWORDS = {
    'if', 'else', 'for', 'while', 'return', 'int', 'float', 'char', 'double', 'void', 'public', 'private', 'class',
    'False', 'await', 'import', 'pass', 'None',	'break', 'except', 'in', 'raise', 'True', 'finally', 'is',
    'and', 'continue', 'for', 'lambda', 'try', 'as', 'def', 'from', 'nonlocal', 'assert', 'del', 'global', 'not', 'with',
    'async', 'elif', 'or', 'yield', 'range'
}

OPERATORS = {
    '+', '-', '*', '**', '/', '//', '%', '@', '=',
    '<<', '>>', '&', '|', '^', '~', ':=', '<', '>', '<=', '>=', '==', '!=', '+=',
    '-=', '*=', '/=', '//=', '%=', '@=', '&=', '|=', '^=', '>>=', '<<=', '**='
}

DELIMITERS = {
    '(', ')', '[', ']', '{', '}', ',', ':', '!', '.', ';', '->'
}

# Helper functions


def is_whitespace(char):
    return char in ' \t\n\r'


def is_letter(char):
    return char.isalpha() or char == '_'


def is_digit(char):
    return char.isdigit()


def is_operator_start(char):
    # Operators can be one or more characters
    operator_chars = set('+-*/%=!&|^~<>')
    return char in operator_chars


def is_delimiter(char):
    return char in DELIMITERS


def remove_comments(code):
    """Remove comments from code."""
    result = []
    i = 0
    n = len(code)
    in_multiline_comment = False
    multiline_quote = ''

    while i < n:
        if not in_multiline_comment:
            # Check for single-line comment
            if code[i] == '#':
                # Skip until the end of the line
                while i < n and code[i] != '\n':
                    i += 1
            # Check for start of multi-line comment
            elif code[i:i+3] in ("'''", '"""'):
                in_multiline_comment = True
                multiline_quote = code[i:i+3]
                i += 3
            else:
                # Not part of a comment, add to result
                result.append(code[i])
                i += 1
        else:
            # Inside a multi-line comment, look for the closing triple quotes
            if code[i:i+3] == multiline_quote:
                in_multiline_comment = False
                multiline_quote = ''
                i += 3
            else:
                # Skip characters inside multi-line comment
                i += 1

    return ''.join(result)


def remove_extra_whitespace(code):
    """Remove whitespace from each line."""
    lines = code.split('\n')
    stripped_lines = [line.lstrip() for line in lines if line.strip()]
    formatted_code = '\n'.join(stripped_lines)
    return formatted_code


def format_code(code):
    """Remove comments and whitespace from the code."""
    code_no_comments = remove_comments(code)
    formatted_code = remove_extra_whitespace(code_no_comments)
    return formatted_code


def tokenize(code):
    """Tokenize the input code into a list of (lexeme, token type) tuples."""
    tokens = []
    i = 0
    n = len(code)

    while i < n:
        current_char = code[i]

        # Skip whitespace
        if is_whitespace(current_char):
            i += 1
            continue

        # Handle identifiers and keywords
        if is_letter(current_char):
            start = i
            while i < n and (is_letter(code[i]) or is_digit(code[i])):
                i += 1
            word = code[start:i]
            if word in KEYWORDS:
                tokens.append((word, 'KEYWORD'))
            else:
                tokens.append((word, 'IDENTIFIER'))
            continue

        # Handle numeric literals
        if is_digit(current_char):
            start = i
            has_dot = False
            while i < n and (is_digit(code[i]) or (code[i] == '.' and not has_dot)):
                if code[i] == '.':
                    has_dot = True
                i += 1
            number = code[start:i]
            tokens.append((number, 'LITERAL'))
            continue

        # Handle string literals (single, double, and triple quotes)
        if current_char in ('"', "'"):
            quote_char = current_char
            start = i
            i += 1
            string_literal = ''
            triple_quote = False

            # Check for triple quotes
            if i + 1 < n and code[i] == quote_char and code[i + 1] == quote_char:
                triple_quote = True
                string_literal += quote_char * 2
                i += 2

            while i < n:
                if triple_quote:
                    if code[i] == quote_char and i + 2 < n and code[i + 1] == quote_char and code[i + 2] == quote_char:
                        string_literal += quote_char * 3
                        i += 3
                        break
                else:
                    if code[i] == '\\' and i + 1 < n:
                        string_literal += code[i] + code[i + 1]
                        i += 2
                        continue
                    if code[i] == quote_char:
                        i += 1
                        break
                string_literal += code[i]
                i += 1

            full_string = quote_char + string_literal
            tokens.append((full_string, 'LITERAL'))
            continue

        # Handle operators (including multi-character operators)
        if is_operator_start(current_char):
            # Try to match the longest possible operator
            max_op_length = max(len(op) for op in OPERATORS)
            matched = False
            for op_length in range(max_op_length, 0, -1):
                if i + op_length <= n:
                    potential_op = code[i:i+op_length]
                    if potential_op in OPERATORS:
                        tokens.append((potential_op, 'OPERATOR'))
                        i += op_length
                        matched = True
                        break
            if matched:
                continue

        # Handle delimiters
        if is_delimiter(current_char):
            tokens.append((current_char, 'DELIMITER'))
            i += 1
            continue

        # If character does not match any token type
        tokens.append((current_char, 'UNKNOWN'))
        i += 1

    return tokens


def display_tokens(tokens):
    """Display tokens in a table format and print the total number of tokens."""
    headers = ["Lexeme", "Token"]
    table = tokens
    print(tabulate(table, headers, tablefmt="fancy_grid"))
    print(f"\nTotal: {len(tokens)}\n")
    print("="*60 + "\n")


def display_formatted_code(formatted_code):
    """Print the formatted code."""
    print("="*60 + "\n")
    print("Formatted Code:\n")
    print(formatted_code)
    print("\n" + "="*60 + "\n")


def read_file(filename):
    """Open and read file, and return code contained in file."""
    f = open(filename, "r")
    code = f.read()
    f.close()
    return code


def main():
    # Read code in .txt file to tokenize
    code = read_file('tests.txt')

    # Remove comments and indentation, then print the formatted code
    formatted_code = format_code(code)
    display_formatted_code(formatted_code)

    # Tokenize code and display tokenized table
    tokens = tokenize(formatted_code)
    display_tokens(tokens)


if __name__ == "__main__":
    main()

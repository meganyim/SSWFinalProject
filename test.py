#SSWFinalProject 
#!/usr/bin/env python3
import sys

VALID_TAGS = {
    "INDI": [0],
    "FAM" : [0],
    "HEAD": [0],
    "TRLR": [0],
    "NOTE": [0],
    "NAME": [1],
    "SEX" : [1],
    "BIRT": [1],
    "DEAT": [1],
    "FAMC": [1],
    "FAMS": [1],
    "MARR": [1],
    "HUSB": [1],
    "WIFE": [1],
    "CHIL": [1],
    "DIV" : [1],
    "DATE": [2],
}

def parse_line(line):
    """
    Given a raw line from a GEDCOM file (no trailing newline),
    return a tuple: (level, tag, arguments).
    """
    tokens = line.split(" ")
    level = tokens[0]

    if level == "0":
        if len(tokens) >= 3 and tokens[2] in ("INDI", "FAM"):
            tag = tokens[2]
            arguments = tokens[1]
        else:
            tag = tokens[1]
            arguments = " ".join(tokens[2:]) if len(tokens) > 2 else ""
    else:
        tag = tokens[1]
        arguments = " ".join(tokens[2:]) if len(tokens) > 2 else ""

    return level, tag, arguments

def is_valid_tag(level_str, tag):
    """
    Returns 'Y' if the given tag is in VALID_TAGS and the numeric
    level matches one of the allowed levels for that tag; otherwise 'N'.
    """
    try:
        lvl = int(level_str)
    except ValueError:
        return "N"

    allowed = VALID_TAGS.get(tag, [])
    return "Y" if lvl in allowed else "N"

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <gedcom_file>")
        sys.exit(1)

    gedcom_path = sys.argv[1]
    try:
        with open(gedcom_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                if not line:
                    continue

                print(f"-->{line}")

                level, tag, arguments = parse_line(line)
                valid_flag = is_valid_tag(level, tag)

                print(f"<-- {level}|{tag}|{valid_flag}|{arguments}")
    except FileNotFoundError:
        print(f"Error: File '{gedcom_path}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()

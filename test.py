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
    Parse into (level:int, tag:str, arguments:str).
    Handles both “0 @I1@ INDI” and “0 I1 INDI” syntaxes.
    Returns (None, None, None) for blank/malformed lines.
    """
    parts = line.strip().split()
    if len(parts) < 2:
        return None, None, None

    # try to parse level
    try:
        level = int(parts[0])
    except ValueError:
        return None, None, None

    # special case at level 0: either “@ID@ TAG” or “ID TAG”
    if level == 0 and len(parts) >= 3 and parts[2] in ("INDI", "FAM"):
        # parts[1] is the ID, parts[2] is the tag
        return level, parts[2], parts[1]

    # otherwise, normal <level> <tag> <arguments...>
    tag = parts[1]
    arguments = " ".join(parts[2:]) if len(parts) > 2 else ""
    return level, tag, arguments


def is_valid_tag(level, tag):
    #Returns "Y" if (tag, level) is valid per VALID_TAGS, else "N".
    if tag not in VALID_TAGS:
        return "N"
    return "Y" if level in VALID_TAGS[tag] else "N"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test.py <filename.ged>")
        sys.exit(1)

    gedcom_path = sys.argv[1]
    #save parsed ind and fam
    individuals = []  # list of dicts
    families = []     # list of dicts

    # Temporary references for “current”
    current_ind = None
    current_fam = None
    expecting_date_for = None  # either "BIRT", "DEAT", "MARR", or "DIV"

    try:
        with open(gedcom_path, "r") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue

                # Print input 
                #print(f"-->{line}")

                level, tag, arguments = parse_line(line)
                if tag is None:
                    continue
                valid_flag = is_valid_tag(level, tag)

                # Print parsed 
                #print(f"<-- {level}|{tag}|{valid_flag}|{arguments}")

                # Build Ind.
                if level == 0 and tag == "INDI":
                    person_id = arguments 
                    current_ind = {
                        "id": person_id,
                        "name": "",
                        "sex": "",
                        "birth": "",
                        "alive": "",
                        "death": "",
                        "famc": "",   # family as child
                        "fams": "",   # family as spouse
                    }
                    individuals.append(current_ind)
                    current_fam = None
                    expecting_date_for = None
                    continue

                if current_ind is not None and level == 1:
                    # ind record fields
                    if tag == "NAME":
                        current_ind["name"] = arguments
                    elif tag == "SEX":
                        current_ind["sex"] = arguments
                    elif tag == "FAMC":
                        current_ind["famc"] = arguments
                    elif tag == "FAMS":
                        current_ind["fams"] = arguments
                    elif tag in ("BIRT", "DEAT"):
                        expecting_date_for = tag
                    else:
                        expecting_date_for = None
                    continue

                if current_ind is not None and level == 2 and tag == "DATE" and expecting_date_for:
                    if expecting_date_for == "BIRT":
                        current_ind["birth"] = arguments
                    elif expecting_date_for == "DEAT":
                        current_ind["death"] = arguments
                        current_ind["alive"] == 'N'
                    expecting_date_for = None
                    continue

                #Build families
                if level == 0 and tag == "FAM":
                    # Start a new family record
                    fam_id = arguments  # e.g. "@F1@"
                    current_fam = {
                        "id": fam_id,
                        "husband": "",
                        "wife": "",
                        "children": [],  # collect multiple children
                        "married": "",
                        "divorced": "",
                    }
                    families.append(current_fam)
                    current_ind = None
                    expecting_date_for = None
                    continue

                if current_fam is not None and level == 1:
                    # Fmaily fields 
                    if tag == "HUSB":
                        current_fam["husband"] = arguments
                    elif tag == "WIFE":
                        current_fam["wife"] = arguments
                    elif tag == "CHIL":
                        current_fam["children"].append(arguments)
                    elif tag in ("MARR", "DIV"):
                        expecting_date_for = tag
                    else:
                        expecting_date_for = None
                    continue

                if current_fam is not None and level == 2 and tag == "DATE" and expecting_date_for:
                    if expecting_date_for == "MARR":
                        current_fam["married"] = arguments
                    elif expecting_date_for == "DIV":
                        current_fam["divorced"] = arguments
                    expecting_date_for = None
                    continue

               
        #create tables and assign columns individual and family data
        from prettytable import PrettyTable
        INDV_Table = PrettyTable()
        INDV_Table.field_names = ["ID", "Name", "Gender", "Birthday", "Alive", "Death", "Child", "Spouse"]
        FAM_Table = PrettyTable()
        FAM_Table.field_names = ["ID", "Husband ID", "Wife ID", "Children", "Married", "Divorced"]
            
        #print tables
        for person in individuals:
            INDV_Table.add_row([
                    person["id"],
                    person["name"],
                    person["sex"],
                    person["birth"],
                    "N" if person["death"] else "Y", #alive if no death
                    person["death"],
                    person["famc"],
                    person["fams"]
                ])
       
        for fam in families:
            FAM_Table.add_row([
        fam["id"],
        fam["husband"],
        fam["wife"],
        ", ".join(fam["children"]),
        fam["married"],
        fam["divorced"]
    ])
        print(INDV_Table)
        print(FAM_Table) 

    except FileNotFoundError:
        print(f"Error: File '{gedcom_path}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()

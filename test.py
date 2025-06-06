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
    Parse into level, tag, arguments
    If there is an “@…@ tag” at level 0 (e.g. “0 @I1@ INDI”), 
    it returns tag="INDI" and arguments="@I1@".
    """
    parts = line.strip().split()
    if len(parts) < 2:
        return None, None, None

    level = parts[0]
    # special case: “0 @X@ TAG”
    if level == "0" and parts[1].startswith("@") and parts[1].endswith("@"):
        arguments = parts[1]
        tag = parts[2]
    else:
        tag = parts[1]
        arguments = " ".join(parts[2:]) if len(parts) > 2 else ""
    return int(level), tag, arguments

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

    #Set up pretty table modules and assign column titles for individual and family data sets
    from prettytable import PrettyTable
    INDV_Table = PrettyTable()
    INDV_Table.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]
    FAM_Table = PrettyTable()
    FAM_Table.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children"]

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
                        "death": "",
                        "famc": "",   # family as child
                        "fams": "",   # family as spouse
                    }
                    individuals.append(current_ind)
                    INDV_Table.add_row([current_ind]) #create a new row of individual data in pretty table module
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
                    FAM_Table.add_row([current_fam]) #create a new row of family data in pretty table module
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
      
        #print tables
        print(INDV_Table)
        print(FAM_Table) 
               
        #print
        #print("\n=== Parsed Individuals ===")
        #for person in individuals:
            #print(person)

        #print("\n=== Parsed Families ===")
        #for fam in families:
            #print(fam)

    except FileNotFoundError:
        print(f"Error: File '{gedcom_path}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()

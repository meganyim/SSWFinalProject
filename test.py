#SSWFinalProject
#!/usr/bin/env python3
import sys
from datetime import datetime


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
#date helper year-mon-day format all in numbers
def reformat_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%d %b %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str  # return unchanged if format doesn't match

#US42 check if correct number of days for each month
def valid_date(date_str2):
    dt2 = datetime.strptime(date_str2, "%d %b %Y")
    #print(dt2)
    month_number = dt2.month
    day = dt2.day
    #print(month_number)
    year = dt2.year
    thirty_one_days = [1,3,5,7,8,10,12]
    thirty_days = [4,6,9,11]
    return_val = True

#determine whether dates from input data have correct number of days for that month
    if month_number in thirty_one_days:
        if day > 31 or day < 1:
            return_val = False

    elif month_number in thirty_days:
        if day > 30 or day < 1:
            return_val = False

    elif month_number == 2:
        if year%4 == 0:                 #leap year is every 4 years
            if day > 29 or day < 1:
                return_val = False
        else:
            if day > 28 or day < 1:
                return_val = False
    else:
        return_val = False

    return return_val

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
    #map ind id to name 
    id_to_name = {}  

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
                    id_to_name[person_id] = "" #initalize id
                    individuals.append(current_ind)
                    current_fam = None
                    expecting_date_for = None
                    continue

                if current_ind is not None and level == 1:
                    # ind record fields
                    if tag == "NAME":
                        current_ind["name"] = arguments
                        id_to_name[current_ind["id"]] = arguments
                    elif tag == "SEX":
                        current_ind["sex"] = {arguments}
                    elif tag == "FAMC":
                        current_ind["famc"] = {arguments}
                    elif tag == "FAMS":
                        current_ind["fams"] = {arguments}
                    elif tag in ("BIRT", "DEAT"):
                        expecting_date_for = tag
                    else:
                        expecting_date_for = None
                    continue

                if current_ind is not None and level == 2 and tag == "DATE" and expecting_date_for:
                    formatted_date = reformat_date(arguments)
                    validated = valid_date(arguments)  #check to see if DATE is legitimate
                    if not validated:
                        print("Date Not Valid: " + arguments)
                        #sys.exit(1)
                    #else:
                        #print("Dates are valid")
                    
                    if expecting_date_for == "BIRT":
                        current_ind["birth"] = formatted_date
                    elif expecting_date_for == "DEAT":
                        current_ind["death"] = formatted_date
                        current_ind["alive"] = 'N'
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
                    # Family fields 
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
                    formatted_date = reformat_date(arguments)
                    validated = valid_date(arguments)  #check to see if DATE is legitimate
                    if not validated:
                        print("Date Not Valid: " + arguments)
                        #sys.exit(1)
                    #else:
                        #print("Dates are valid")
                    
                    if expecting_date_for == "MARR":
                        current_fam["married"] = formatted_date
                    elif expecting_date_for == "DIV":
                        current_fam["divorced"] = formatted_date
                    expecting_date_for = None
                    continue
       
                

                     
        # US04: marriage must occur before divorce (and you can’t divorce if you never married)
        for fam in families:
            if fam["divorced"]:
                if not fam["married"]:
                    print(f"Error: Family {fam['id']} has divorce on {fam['divorced']} but no marriage date.")
                else:
                    # parse the two dates
                    marr = datetime.strptime(fam["married"], "%Y-%m-%d")
                    div  = datetime.strptime(fam["divorced"], "%Y-%m-%d")
                    if div < marr:
                        print(f"Error: Family {fam['id']} divorce ({fam['divorced']}) occurs before marriage ({fam['married']}).")

        # US05: marriage must occur before death of either spouse
        for fam in families:
            if fam["married"]:
                marr = datetime.strptime(fam["married"], "%Y-%m-%d")
                # check husband's death
                husband = next((ind for ind in individuals if ind["id"] == fam["husband"]), None)
                if husband and husband.get("death"):
                    death_h = datetime.strptime(husband["death"], "%Y-%m-%d")
                    if marr > death_h:
                        print(f"Error: Family {fam['id']} marriage ({fam['married']}) occurs after husband's death ({husband['death']}).")
             
                # US42: Check if Husband is male
                if husband and husband.get("sex"):    
                    sex_h = husband["sex"]
                    if sex_h != {'M'}:
                        print(f"Wrong gender for role: Husband {fam['husband']} is {husband['sex']}")
                    
                # check wife's death
                wife = next((ind for ind in individuals if ind["id"] == fam["wife"]), None)
                if wife and wife.get("death"):
                    death_w = datetime.strptime(wife["death"], "%Y-%m-%d")
                    if marr > death_w:
                        print(f"Error: Family {fam['id']} marriage ({fam['married']}) occurs after wife's death ({wife['death']}).")
            
                # US42: Check if Wife is female
                if wife and wife.get("sex"):          
                    sex_w = wife["sex"]
                    if sex_w != {'F'}:
                        print(f"Wrong gender for role: Wife {fam['wife']} is {wife['sex']}")

     
        #create tables and assign columns individual and family data
        from prettytable import PrettyTable
        INDV_Table = PrettyTable()
        INDV_Table.field_names = ["ID", "Name", "Gender", "Birthday", "Alive", "Death", "Child", "Spouse"]
        FAM_Table = PrettyTable()
        FAM_Table.field_names = ["ID", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children", "Married", "Divorced"]
            
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
                    id_to_name.get(fam["husband"], ""),
                    fam["wife"],
                    id_to_name.get(fam["wife"], ""),
                    ", ".join(fam["children"]),
                    fam["married"],
                    fam["divorced"]
                ])

 # US02: Birth before marriage
        divorce_errors = 0
        for fam in families:
            if fam["divorced"]:
                divorce_errors += 1

                if not fam["married"]:
                    print(f"Error US02: Family {fam['id']} has divorce on {fam['divorced']} but no marriage date.")

                else:
                    marr = datetime.strptime(fam["married"], "%Y-%m-%d")
                    div  = datetime.strptime(fam["divorced"], "%Y-%m-%d")

                    if div < marr:
                        print(f"Error US02: Family {fam['id']} divorce ({fam['divorced']}) occurs before marriage ({fam['married']}).")
        
        if divorce_errors == 0:
            print("No US02 errors found.")
            
    # US03: Birth before death  
        death_errors = 0
        for fam in families:
            if fam["married"]:
                marr = datetime.strptime(fam["married"], "%Y-%m-%d")
                husband = next((ind for ind in individuals if ind["id"] == fam["husband"]), None)

                if husband and husband.get("death"):
                    death_h = datetime.strptime(husband["death"], "%Y-%m-%d")

                    if marr > death_h:
                        print(f"Error US03: Family {fam['id']} marriage ({fam['married']}) occurs after husband's death ({husband['death']}).")
                        death_errors += 1
                        
                wife = next((ind for ind in individuals if ind["id"] == fam["wife"]), None)

                if wife and wife.get("death"):
                    death_w = datetime.strptime(wife["death"], "%Y-%m-%d")

                    if marr > death_w:
                        print(f"Error US03: Family {fam['id']} marriage ({fam['married']}) occurs after wife's death ({wife['death']}).")
                        death_errors += 1
        
        if death_errors == 0: 
            print("No US03 errors found.")
        
        print(INDV_Table)
        print(FAM_Table) 
    
    except FileNotFoundError:
        print(f"Error: File '{gedcom_path}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()

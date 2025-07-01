#SSWFinalProject
#!/usr/bin/env python3
import sys
from datetime import datetime, timedelta


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

def _same_id(a, b):
    """Return True if GEDCOM IDs match, ignoring surrounding @ symbols."""
    return a.strip("@") == b.strip("@")

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




    
       # US015: Familes must have fewer than 15 siblings    
            sibs = len(fam["children"])
            #print(sibs)
            if sibs >= 15:
                print(f"Error US15: Family {fam['id']} has {sibs} children")

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


        # US01: Dates before current date
        from datetime import date      # already imported earlier, but harmless

        today = date.today()           # YYYY-MM-DD for comparison
        today = date.today()

        # individuals
        for ind in individuals:
            for field in ("birth", "death"):
                if ind[field]:
                    d = datetime.strptime(ind[field], "%Y-%m-%d").date()
                    if d > today:
                        print(f"Error US01: {field.title()} date ({ind[field]}) "
                            f"of Individual {ind['id']} occurs in the future.")

        # US07: Check if any indiviuals have lived 150 yrs or more
        for ind in individuals:        
                if ind["birth"] and not ind["death"]:
                    birthday = datetime.strptime(ind['birth'], "%Y-%m-%d")
                    #print(birthday)
                    alive = datetime.today() - timedelta(days = 365.25*150)
                    #print(alive)

                    if birthday < alive:
                        print(f"Error US07: {ind['id']} has lived 150 yrs or more")
                    
                    #elif birthday > alive:
                        #print(f"Good US07: {ind['id']} has lived less than 150 yrs")

                if ind["birth"] and ind["death"]:
                    birthday = datetime.strptime(ind['birth'], "%Y-%m-%d")
                    #print(birthday)
                    deathday = datetime.strptime(ind['death'], "%Y-%m-%d")
                    #print(deathday)
                    
                    if deathday - birthday >= timedelta(days = 365.25*150):
                        print(f"Error US07: {ind['id']} lived 150 yrs or more")

                    #if deathday - birthday < timedelta(days = 365.25*150):
                        #print(f"Good US07: {ind['id']} did not lived 150 yrs or more")

        # families
        for fam in families:
            for field in ("married", "divorced"):
                if fam[field]:
                    d = datetime.strptime(fam[field], "%Y-%m-%d").date()
                    if d > today:
                        print(f"Error US01: {field.title()} date ({fam[field]}) "
                            f"of Family {fam['id']} occurs in the future.")

        # US06: Divorce before death of either spouse
        for fam in families:
            if not fam["divorced"]:
                continue                           # nothing to check

            div_dt = datetime.strptime(fam["divorced"], "%Y-%m-%d")

            husband = next((ind for ind in individuals
                            if ind["id"] == fam["husband"]), None)
            wife    = next((ind for ind in individuals
                            if ind["id"] == fam["wife"]), None)

            # Husband died first?
            if husband and husband.get("death"):
                death_h = datetime.strptime(husband["death"], "%Y-%m-%d")
                if div_dt > death_h:
                    print(f"Error US06: Divorce ({fam['divorced']}) in Family {fam['id']} "
                        f"occurs after husband's death ({husband['death']}).")

            # Wife died first?
            if wife and wife.get("death"):
                death_w = datetime.strptime(wife["death"], "%Y-%m-%d")
                if div_dt > death_w:
                    print(f"Error US06: Divorce ({fam['divorced']}) in Family {fam['id']} "
                        f"occurs after wife's death ({wife['death']}).")
                    
        # 
        # US08 – Birth after parents’ marriage (and ≤ 9 months after divorce)
        # 
        for fam in families:
            if not fam["children"]:
                continue

            marr_dt = datetime.strptime(fam["married"], "%Y-%m-%d") \
                    if fam["married"] else None
            div_dt  = datetime.strptime(fam["divorced"], "%Y-%m-%d") \
                    if fam["divorced"] else None

            for child_id in fam["children"]:
                child = next((ind for ind in individuals
                            if _same_id(ind["id"], child_id)), None)
                if not child or not child["birth"]:
                    continue
                child_birth_dt = datetime.strptime(child["birth"], "%Y-%m-%d")

                # Child born before marriage
                if marr_dt and child_birth_dt < marr_dt:
                    print(f"Error US08: Child {child_id} born {child['birth']} "
                        f"before parents' marriage {fam['married']} "
                        f"in family {fam['id']}.")

                # Child born 9 months after divorce
                if div_dt and child_birth_dt > div_dt + timedelta(days=270):
                    print(f"Error US08: Child {child_id} born {child['birth']} "
                        f"more than 9 months after parents' divorce "
                        f"{fam['divorced']} in family {fam['id']}.")                       
                
        # 
        # US12 – Parents not too old (mother < 60 yrs older, father < 80 yrs older)
        # 
        for fam in families:
            mom = next((ind for ind in individuals
                if _same_id(ind["id"], fam["wife"])), None)
            dad = next((ind for ind in individuals
                if _same_id(ind["id"], fam["husband"])), None)
            if not mom or not dad or not mom["birth"] or not dad["birth"]:
                continue  # missing parent birthdates

            mom_birth_dt = datetime.strptime(mom["birth"], "%Y-%m-%d")
            dad_birth_dt = datetime.strptime(dad["birth"], "%Y-%m-%d")

            for child_id in fam["children"]:
                child = next((ind for ind in individuals
                            if _same_id(ind["id"], child_id)), None)
                if not child or not child["birth"]:
                    continue
                child_birth_dt = datetime.strptime(child["birth"], "%Y-%m-%d")

                # age differences in years
                mom_age_diff = (child_birth_dt - mom_birth_dt).days / 365.25
                dad_age_diff = (child_birth_dt - dad_birth_dt).days / 365.25

                if mom_age_diff >= 60:
                    print(f"Error US12: Mother ({mom['id']}) is "
                        f"{int(mom_age_diff)} years older than child {child_id} "
                        f"(limit < 60).")
                if dad_age_diff >= 80:
                    print(f"Error US12: Father ({dad['id']}) is "
                        f"{int(dad_age_diff)} years older than child {child_id} "
                        f"(limit < 80).")
     
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

        us02_errors = 0
        for person in individuals:
            if person["birth"] and person["fams"]:
                fams_id = str(person["fams"]).strip("{}'")
                for fam in families:
                    if fam["id"] == fams_id and fam["married"]:
                        if person["birth"] > fam["married"]:
                            print(f"US02 Error Detected: {person['name']} ({person['id']}) birth after marriage")
                            us02_errors += 1
        
        if us02_errors == 0:
            print("No US02 errors found. All births occur before marriages")

# US03: Birth before death  

        us03_errors = 0
        for person in individuals:
            if person["birth"] and person["death"]:
                if person["birth"] > person["death"]:
                    print(f"US03 Error Detected: {person['name']} ({person['id']}) birth after death")
                    us03_errors += 1


        # US14: Multiple births <= 5
        for fam in families:
            if not fam["children"]:
                continue
            
            birth_date_groups = {}
            for child_id in fam["children"]:
                child = next((ind for ind in individuals if ind["id"] == child_id), None)
                if child and child["birth"]:
                    birth_date = child["birth"]
                    
                    if birth_date not in birth_date_groups:
                        birth_date_groups[birth_date] = []
                    birth_date_groups[birth_date].append(child_id)
            
            for birth_date, children_on_date in birth_date_groups.items():
                if len(children_on_date) > 5:
                    print(f"US14 Error Detected: Family {fam['id']} has {len(children_on_date)} children born on {birth_date}")

        # US22: Unique IDs
        found_duplicate_individuals = False

        for i in range(len(individuals)):
            current_id = individuals[i]["id"]
            
            for j in range(i + 1, len(individuals)):
                other_id = individuals[j]["id"]
                
                if current_id == other_id:
                    print(f"US22 Error Detected: Duplicate individual ID {current_id}")
                    found_duplicate_individuals = True
                    
        found_duplicate_families = False
                        
        for i in range(len(families)):
            current_id = families[i]["id"]
            
            for j in range(i + 1, len(families)):
                other_id = families[j]["id"]
                
                if current_id == other_id:
                    print(f"US22 Error Detected: Duplicate family ID {current_id}")
                    found_duplicate_families = True
        
        # US16: All male members of a family should have the same last name
        for fam in families:
            surname = None
            male_ids = []

            # Add husband to male list
            if fam["husband"]:
                male_ids.append(fam["husband"])

            # Add male children
            for child_id in fam["children"]:
                child = next((ind for ind in individuals if ind["id"] == child_id), None)
                if child and child.get("sex") == {'M'}:
                    male_ids.append(child["id"])

            # Check last names
            for mid in male_ids:
                name = id_to_name.get(mid, "")
                if "/" in name:
                    last = name.split("/")[1].strip()
                    if surname is None:
                        surname = last
                    elif last != surname:
                        print(f"Error US16: In Family {fam['id']}, male individual {mid} has inconsistent last name '{last}' (expected '{surname}')")

                # US10: Marriage after 14
        us10_errors = 0
        for fam in families:
            if not fam["married"]:
                continue

            marriage_date = datetime.strptime(fam["married"], "%Y-%m-%d")
            
            # Get husband and wife
            husband = next((ind for ind in individuals if ind["id"] == fam["husband"]), None)
            wife = next((ind for ind in individuals if ind["id"] == fam["wife"]), None)

            # Check husband's age at marriage
            if husband and husband.get("birth"):
                birth_h = datetime.strptime(husband["birth"], "%Y-%m-%d")
                age_h = (marriage_date - birth_h).days / 365.25
                if age_h < 14:
                    print(f"Error US10: Husband {husband['id']} was younger than 14 at marriage in Family {fam['id']}")
                    us10_errors += 1

            # Check wife's age at marriage
            if wife and wife.get("birth"):
                birth_w = datetime.strptime(wife["birth"], "%Y-%m-%d")
                age_w = (marriage_date - birth_w).days / 365.25
                if age_w < 14:
                    print(f"Error US10: Wife {wife['id']} was younger than 14 at marriage in Family {fam['id']}")
                    us10_errors += 1

        if us10_errors == 0:
            print("No US10 errors found. All marriages occurred when spouses were at least 14 years old.")

        print(INDV_Table)
        print(FAM_Table) 
    
    except FileNotFoundError:
        print(f"Error: File '{gedcom_path}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()  # run GEDCOM file normally
    else:
        import unittest
        unittest.main(module='testus10_16', exit=False)


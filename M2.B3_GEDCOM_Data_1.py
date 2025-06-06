#Read text file with GEDCOM data and assign to variable
gedcom_data = open("gedcom_data.txt", "r")

#Define accepted tags
tag_list = ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]
special_list = ["INDI", "FAM"]

#Import pretty table module and assign column names
#from prettytable import PrettyTable
#INDV_Table = PrettyTable()
#INDV_Table.field_names = ["TAG", "VALID", "AG1", "AG2", "AG3"]

for line in gedcom_data.readlines():
   line_tokens = line.split()
   padding = ' '

   while len(line_tokens) < 5:
      line_tokens.append(padding)

   #print(line_tokens)

   level = line_tokens[0]
   #print(level)
   secondToken = line_tokens[1]
   thirdToken = line_tokens[2]

   if thirdToken in special_list:
        id = line_tokens[1]
        tag = line_tokens[2]
        arugument = line_tokens[3]
        valid = "Y"
        print(level + "|" + tag + "|" + valid + "|" + id)
        continue

   elif secondToken in tag_list:
     
       valid = 'Y'
   else:
       valid = "N"
       
    
   tag = line_tokens[1]
   arugument = line_tokens[2]
   argument2 = line_tokens[3]
   argument3 = line_tokens[4]
   
   #INDV_Table.add_row([tag, valid, arugument, argument2, argument3])
   print(level + "|" + tag + "|" + valid + "|" + arugument + " " + argument2 + " "+ argument3)
         
   
#print(INDV_Table)
gedcom_data.close()
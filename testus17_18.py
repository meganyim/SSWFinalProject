# testus17_18.py
import unittest
import subprocess
import tempfile
import os

class TestUserStories(unittest.TestCase):
    def create_temp_gedcom(self, content):
        temp = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.ged')
        temp.write(content)
        temp.close()
        return temp.name

    def test_us17_cant_marry_kids(self):
        gedcom_data = """
0 I1 INDI
1 NAME Seeyu /Choy/
1 SEX M
1 BIRT
2 DATE 1 JAN 1940
1 DEAT
2 DATE 1 JUN 2000
1 FAMS F1
1 FAMS F2
0 I4 INDI
1 NAME Nathan /Choy/
1 SEX F
1 BIRT
2 DATE 15 AUG 1950
1 FAMS F2
1 FAMC F1
0 I7 INDI
1 NAME Alison /Yim/
1 SEX M
1 BIRT
2 DATE 5 MAY 1987
1 FAMC F3
1 FAMS F4
0 I8 INDI
1 NAME Annabel /Yim/
1 SEX F
1 BIRT
2 DATE 12 DEC 1990
1 FAMC F3
1 FAMS F4
0 F1 FAM
1 MARR
2 DATE 5 MAY 1960
1 HUSB I1
1 WIFE I2
1 CHIL I3
1 CHIL I4
0 F2 FAM
1 MARR
2 DATE 15 SEP 1975
1 HUSB I1
1 WIFE I4
1 CHIL I5
0 F3 FAM
1 MARR
2 DATE 20 JUN 1985
1 HUSB I3
1 WIFE I6
1 CHIL I7
1 CHIL I8
1 CHIL I9
1 CHIL I10
0 F4 FAM
1 MARR
2 DATE 20 JUL 2002
1 HUSB I7
1 WIFE I8
0 TRLR
"""
        temp_file = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp_file], capture_output=True, text=True)
        os.unlink(temp_file)
        self.assertIn("Error US17", result.stdout)

    def test_us18_cant_marry_siblings_(self):
        gedcom_data = """
0 I1 INDI
1 NAME Seeyu /Choy/
1 SEX M
1 BIRT
2 DATE 1 JAN 1940
1 DEAT
2 DATE 1 JUN 2000
1 FAMS F1
1 FAMS F2
0 I4 INDI
1 NAME Nathan /Choy/
1 SEX F
1 BIRT
2 DATE 15 AUG 1950
1 FAMS F2
1 FAMC F1
0 I7 INDI
1 NAME Alison /Yim/
1 SEX M
1 BIRT
2 DATE 5 MAY 1987
1 FAMC F3
1 FAMS F4
0 I8 INDI
1 NAME Annabel /Yim/
1 SEX F
1 BIRT
2 DATE 12 DEC 1990
1 FAMC F3
1 FAMS F4
0 F1 FAM
1 MARR
2 DATE 5 MAY 1960
1 HUSB I1
1 WIFE I2
1 CHIL I3
1 CHIL I4
0 F2 FAM
1 MARR
2 DATE 15 SEP 1975
1 HUSB I1
1 WIFE I4
1 CHIL I5
0 F3 FAM
1 MARR
2 DATE 20 JUN 1985
1 HUSB I3
1 WIFE I6
1 CHIL I7
1 CHIL I8
1 CHIL I9
1 CHIL I10
0 F4 FAM
1 MARR
2 DATE 20 JUL 2002
1 HUSB I7
1 WIFE I8
0 TRLR
"""
"""
        temp_file = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp_file], capture_output=True, text=True)
        os.unlink(temp_file)
        self.assertIn("Error US18", result.stdout)

if __name__ == '__main__':
    unittest.main()

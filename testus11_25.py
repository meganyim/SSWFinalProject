# testus11_25.py
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

    def test_us11_no_bigamy(self):
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
0 I2 INDI
1 NAME Stephen /Choy/
1 SEX F
1 BIRT
2 DATE 2 FEB 1942
1 DEAT
2 DATE 3 MAR 1980
1 FAMS F1
0 I4 INDI
1 NAME Nathan /Choy/
1 SEX F
1 BIRT
2 DATE 15 AUG 1950
1 FAMS F2
0 F1 FAM
1 MARR
2 DATE 5 MAY 1960
1 HUSB I1
1 WIFE I2
0 F2 FAM
1 MARR
2 DATE 15 SEP 1975
1 HUSB I1
1 WIFE I4
0 TRLR
"""
        temp_file = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp_file], capture_output=True, text=True)
        os.unlink(temp_file)
        self.assertIn("Error US11", result.stdout)

    def test_us25_unique_first_names(self):
        gedcom_data = """
0 I1 INDI
1 NAME Father /Test/
1 SEX M
1 BIRT
2 DATE 1 JAN 1960
1 FAMS F1
0 I2 INDI
1 NAME Mother /Test/
1 SEX F
1 BIRT
2 DATE 1 JAN 1962
1 FAMS F1
0 I3 INDI
1 NAME Alison /Test/
1 SEX F
1 BIRT
2 DATE 5 MAY 1987
1 FAMC F1
0 I4 INDI
1 NAME Alison /Test/
1 SEX F
1 BIRT
2 DATE 5 MAY 1987
1 FAMC F1
0 I5 INDI
1 NAME Robert /Test/
1 SEX M
1 BIRT
2 DATE 10 JUN 1990
1 FAMC F1
0 I6 INDI
1 NAME Robert /Test/
1 SEX M
1 BIRT
2 DATE 10 JUN 1990
1 FAMC F1
0 F1 FAM
1 MARR
2 DATE 20 JUN 1985
1 HUSB I1
1 WIFE I2
1 CHIL I3
1 CHIL I4
1 CHIL I5
1 CHIL I6
0 TRLR
"""
        temp_file = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp_file], capture_output=True, text=True)
        os.unlink(temp_file)
        self.assertIn("Error US25", result.stdout)

if __name__ == '__main__':
    unittest.main()
# testus07_15.py
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

    def test_us07_less_than_150yrs(self):
        gedcom_data = """
0 @I1@ INDI
1 NAME John /Young/
1 SEX M
1 BIRT
2 DATE 1 JAN 1870
1 FAMS @F1@
0 @I2@ INDI
1 NAME Jane /Young/
1 SEX F
1 BIRT
2 DATE 1 JAN 2010
1 FAMS @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 1 JAN 2022
0 TRLR
"""
        temp_file = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp_file], capture_output=True, text=True)
        os.unlink(temp_file)
        self.assertIn("Error US07", result.stdout)

    def test_us15_less_than_15siblings_(self):
        gedcom_data = """
0 @I1@ INDI
1 NAME John /Smith/
1 SEX M
1 BIRT
2 DATE 1 JAN 1980
1 FAMS @F1@
0 @I2@ INDI
1 NAME James /Doe/
1 SEX M
1 BIRT
2 DATE 1 JAN 2005
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 CHIL @I2@
0 TRLR
"""
        temp_file = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp_file], capture_output=True, text=True)
        os.unlink(temp_file)
        self.assertIn("Error US15", result.stdout)

if __name__ == '__main__':
    unittest.main()

# testus14_22.py
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

    def test_us14_multiple_births(self):
        gedcom_data = """
0 @I30@ INDI
1 NAME Twin1 /Test/
1 SEX M
1 BIRT
2 DATE 1 JAN 2020
0 @I31@ INDI
1 NAME Twin2 /Test/
1 SEX F
1 BIRT
2 DATE 1 JAN 2020
0 @I32@ INDI
1 NAME Twin3 /Test/
1 SEX M
1 BIRT
2 DATE 1 JAN 2020
0 @I33@ INDI
1 NAME Twin4 /Test/
1 SEX F
1 BIRT
2 DATE 1 JAN 2020
0 @I34@ INDI
1 NAME Twin5 /Test/
1 SEX M
1 BIRT
2 DATE 1 JAN 2020
0 @I35@ INDI
1 NAME Twin6 /Test/
1 SEX F
1 BIRT
2 DATE 1 JAN 2020
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I30@
1 CHIL @I31@
1 CHIL @I32@
1 CHIL @I33@
1 CHIL @I34@
1 CHIL @I35@
0 TRLR
"""
        temp = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp], capture_output=True, text=True)
        os.unlink(temp)
        self.assertIn("US14 Error Detected", result.stdout)

    def test_us22_unique_ids(self):
        gedcom_data = """
0 @I1@ INDI
1 NAME John /Smith/
1 SEX M
1 BIRT
2 DATE 1 JAN 1980
0 @I1@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 1 JAN 1985
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 @F1@ FAM
1 HUSB @I3@
1 WIFE @I4@
0 TRLR
"""
        temp = self.create_temp_gedcom(gedcom_data)
        result = subprocess.run(['python3', 'test.py', temp], capture_output=True, text=True)
        os.unlink(temp)
        self.assertIn("US22 Error Detected", result.stdout)

if __name__ == '__main__':
    unittest.main()

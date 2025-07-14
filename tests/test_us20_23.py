import subprocess, sys, tempfile, textwrap, os, pathlib

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "test.py"

def run_validator(ged_text: str) -> str:
    
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".ged") as tmp:
        tmp.write(textwrap.dedent(ged_text))
        tmp.flush()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), tmp.name],
            capture_output=True,
            text=True,
            check=True,
        )
    os.unlink(tmp.name)
    return result.stdout


#  US23 – duplicate name + birth-date should raise an error
def test_us23_duplicate_name_birth():
    ged = """
    0 HEAD
    1 SOUR Mini
    0 @I1@ INDI
    1 NAME John /Doe/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1990
    0 @I2@ INDI
    1 NAME John /Doe/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1990
    0 TRLR
    """
    out = run_validator(ged)
    assert "Error US23" in out


#  US20 – aunt/uncle marrying niece/nephew should raise an error
def test_us20_aunt_uncle_marriage():
    ged = """
    0 HEAD
    1 SOUR Mini
    # Grandparents
    0 @I1@ INDI
    1 NAME Grandpa /Smith/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1950
    0 @I2@ INDI
    1 NAME Grandma /Smith/
    1 SEX  F
    1 BIRT
    2 DATE  1 JAN 1952

    # Their children: Uncle Bob and Mother Mary (siblings)
    0 @I3@ INDI
    1 NAME UncleBob /Smith/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1975
    0 @I4@ INDI
    1 NAME MotherMary /Smith/
    1 SEX  F
    1 BIRT
    2 DATE  1 JAN 1978

    # Mother Mary's husband and their daughter (niece)
    0 @I5@ INDI
    1 NAME Dad /Jones/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1975
    0 @I6@ INDI
    1 NAME NieceNancy /Jones/
    1 SEX  F
    1 BIRT
    2 DATE  1 JAN 2000

    # F1: grandparents + kids
    0 @F1@ FAM
    1 HUSB @I1@
    1 WIFE @I2@
    1 CHIL @I3@
    1 CHIL @I4@

    # F2: parents of niece
    0 @F2@ FAM
    1 HUSB @I5@
    1 WIFE @I4@
    1 CHIL @I6@

    # F3: invalid—uncle marries niece
    0 @F3@ FAM
    1 HUSB @I3@
    1 WIFE @I6@
    0 TRLR
    """
    out = run_validator(ged)
    assert "Error US20" in out
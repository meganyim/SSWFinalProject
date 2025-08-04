import subprocess, sys, tempfile, textwrap, os, pathlib, re

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "test.py"

def run_validator(ged_text: str) -> str:
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".ged") as tmp:
        tmp.write(textwrap.dedent(ged_text))
        tmp.flush()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), tmp.name],
            capture_output=True, text=True, check=True
        )
    os.unlink(tmp.name)
    return result.stdout

def test_us28_children_sorted_oldest_first():
    ged = """
    0 HEAD
    0 @I1@ INDI
    1 NAME Oldest /Kid/
    1 SEX M
    1 BIRT
    2 DATE  1 JAN 2000
    0 @I2@ INDI
    1 NAME Middle /Kid/
    1 SEX M
    1 BIRT
    2 DATE  1 JAN 2005
    0 @I3@ INDI
    1 NAME Youngest /Kid/
    1 SEX F
    1 BIRT
    2 DATE  1 JAN 2010
    0 @I4@ INDI
    1 NAME Dad /Parent/
    1 SEX M
    1 BIRT
    2 DATE  1 JAN 1970
    0 @I5@ INDI
    1 NAME Mom /Parent/
    1 SEX F
    1 BIRT
    2 DATE  1 JAN 1972
    0 @F1@ FAM
    1 HUSB @I4@
    1 WIFE @I5@
    # scrambled input order
    1 CHIL @I3@
    1 CHIL @I1@
    1 CHIL @I2@
    0 TRLR
    """
    out = run_validator(ged)

    
    def pos(token: str) -> int:
        m = re.search(rf'@?{re.escape(token)}@?', out)
        return m.start() if m else -1

    p1, p2, p3 = pos("I1"), pos("I2"), pos("I3")
    assert p1 != -1 and p2 != -1 and p3 != -1
    assert p1 < p2 < p3   
# tests
import subprocess, sys, tempfile, textwrap, os, pathlib

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "test.py"

def run_validator(gedcom_text: str) -> str:
   
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".ged") as tmp:
        tmp.write(textwrap.dedent(gedcom_text))
        tmp.flush()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), tmp.name],
            capture_output=True,
            text=True,
            check=True
        )
    os.unlink(tmp.name)
    return result.stdout

def test_us08_birth_before_marriage():
    """Child born before parents' marriage should trigger US08 error."""
    gedcom_snippet = """
    0 HEAD
    1 SOUR Mini
    0 @I1@ INDI
    1 NAME Dad /Test/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1970
    0 @I2@ INDI
    1 NAME Mom /Test/
    1 SEX  F
    1 BIRT
    2 DATE  1 JAN 1972
    0 @I3@ INDI
    1 NAME Kid /Test/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1990
    0 @F1@ FAM
    1 HUSB @I1@
    1 WIFE @I2@
    1 MARR
    2 DATE  1 JAN 2000
    1 CHIL I3
    0 TRLR
    """
    out = run_validator(gedcom_snippet)
    assert "Error US08" in out
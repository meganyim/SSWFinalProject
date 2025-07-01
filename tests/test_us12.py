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

def test_us12_father_too_old():
    """Father ≥ 80 yrs older than child should trigger US12 error."""
    gedcom_snippet = """
    0 HEAD
    1 SOUR Mini
    0 @I10@ INDI
    1 NAME Old /Father/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1900
    0 @I11@ INDI
    1 NAME Young /Mother/
    1 SEX  F
    1 BIRT
    2 DATE  1 JAN 1970
    0 @I12@ INDI
    1 NAME Baby /Test/
    1 SEX  M
    1 BIRT
    2 DATE  1 JAN 1985
    0 @F9@ FAM
    1 HUSB @I10@
    1 WIFE @I11@
    1 MARR
    2 DATE  1 JAN 1979
    1 CHIL I12
    0 TRLR
    """
    out = run_validator(gedcom_snippet)
    assert "Error US12" in out

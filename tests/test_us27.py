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

def _split_cols(line: str):
    parts = [c.strip() for c in line.split("|")]
    return parts[1:-1] if len(parts) >= 3 else []

def _get_table(out: str, header_must_include: list[str]):
   
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        if "|" not in ln:
            continue
        header = _split_cols(ln)
        if all(h in header for h in header_must_include):
            rows = []
            j = i + 1
            while j < len(lines):
                cur = lines[j]
                if "|" in cur:
                    cols = _split_cols(cur)
                    if cols and cols != header:        
                        rows.append(cols)
                elif cur.strip().startswith("+") or cur.strip() == "":
                    
                    pass
                else:
                    
                    break
                j += 1
            return header, rows
    return [], []

def _normalize_id(s: str) -> str:
    return s.replace("@", "").strip()

def test_us27_age_shown_for_alive_and_dead():
    ged = """
    0 HEAD
    0 @I1@ INDI
    1 NAME A /One/
    1 SEX F
    1 BIRT
    2 DATE  1 JAN 2000
    0 @I2@ INDI
    1 NAME B /Two/
    1 SEX M
    1 BIRT
    2 DATE  1 JAN 1980
    1 DEAT
    2 DATE  1 JAN 2020
    0 TRLR
    """
    out = run_validator(ged)

    header, rows = _get_table(out, ["ID", "Name", "Gender", "Birthday"])
    assert header, "Individuals table not found in output"
    assert "Age" in header, "Age column missing from Individuals table"

    
    rows = [r for r in rows if len(r) == len(header)]

    c_id    = header.index("ID")
    c_age   = header.index("Age")
    c_alive = header.index("Alive")

    
    ages   = {_normalize_id(r[c_id]): r[c_age]   for r in rows}
    alive  = {_normalize_id(r[c_id]): r[c_alive] for r in rows}

    
    assert alive["I1"] == "Y"
    assert re.fullmatch(r"\d{1,3}", ages["I1"])

    
    assert ages["I2"] == "40"
# %%
import re
import shutil
from io import StringIO
from pathlib import Path

import pandas as pd


MY_MOD_UNITS_PREFIX = "ruene_emp_veteran_inf"
NANU_MOD_PATH = "/home/rue/WH3-Mods/Mods/!LOOKUP/!!_nanu_dynamic_rors"


REFERENCE_TABLE_NAMES = ["nanu_dynamic_rors_emp.tsv", "nanu_dynamic_rors_dwf.tsv"]

# Define which base game units serve as template for your new custom units
UNIT_TEMPLATES = {
    f"{MY_MOD_UNITS_PREFIX}_halberdiers": "wh_main_emp_inf_halberdiers",
    f"{MY_MOD_UNITS_PREFIX}_swordsmen": "wh_main_emp_inf_swordsmen",
    f"{MY_MOD_UNITS_PREFIX}_spearmen": "wh_main_emp_inf_spearmen_1",
}
# --- Constants ---------------------------------------------------------
here = Path(__file__).parent

nanu_effects_table_name = "unit_purchasable_effect_sets_tables"
nanu_mod_reference_tables_path = Path(f"{NANU_MOD_PATH}/db/{nanu_effects_table_name}")
nanu_lua_path = Path(f"{NANU_MOD_PATH}/script/campaign/mod/nanu_dynamic_ror_data.lua")
reference_tables = [
    nanu_mod_reference_tables_path / name for name in REFERENCE_TABLE_NAMES
]


lua_template_path = here / "template_units_nanu_rors.lua"

ror_table_name = f"{MY_MOD_UNITS_PREFIX}_nanu_rors"
out_dir = here / "out"
lua_out_path = (
    out_dir / "script" / "campaign" / "mod" / f"{MY_MOD_UNITS_PREFIX}_nanu_rors.lua"
)
effects_out_dir = out_dir / "db" / nanu_effects_table_name

# Clear the output directory before every run
if out_dir.exists():
    shutil.rmtree(out_dir)
out_dir.mkdir(parents=True)


# -------------------------------------------------------------------------


# --- Constants ---------------------------------------------------------

# -------------------------------------------------------------------------


def read_tw_tsvs(paths):
    reference_lines = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 1 and lines[1].startswith("#"):
            del lines[1]
        if reference_lines:
            lines = lines[1:]  # skip header row for subsequent files
        reference_lines.extend(lines)
    df = pd.read_csv(StringIO("".join(reference_lines)), sep="\t")
    return df


def write_tw_tsv(df, filename, header_line=None):
    df.to_csv(filename, sep="\t", index=False)
    if header_line:
        with open(filename, "r+", encoding="utf-8") as f:
            content = f.readlines()
            content.insert(1, f"{header_line}\n")
            f.seek(0)
            f.writelines(content)


reference_df = read_tw_tsvs(reference_tables)


ror_df = pd.DataFrame(columns=reference_df.columns)
# Step 1: For each template unit, copy matching rows and remap unit name to the new key
template_values = list(UNIT_TEMPLATES.values())
matched = reference_df[reference_df["unit"].isin(template_values)].copy()
value_to_key = {v: k for k, v in UNIT_TEMPLATES.items()}
matched["unit"] = matched["unit"].map(value_to_key)
ror_df = pd.concat([ror_df, matched], ignore_index=True)


# Step 2: Parse nanu lua data file for keywords of each template unit, then emit lua script
with open(nanu_lua_path, "r", encoding="utf-8") as f:
    lua_content = f.read()

# Parse all unit keyword lines: ["unit_key"] = {"kw1", "kw2", ...}
lua_unit_kw_pattern = re.compile(r'\["([^"]+)"\]\s*=\s*\{([^}]+)\}')
lua_keywords: dict[str, list[str]] = {}
for m in lua_unit_kw_pattern.finditer(lua_content):
    unit_key = m.group(1)
    kws = [kw.strip().strip('"') for kw in m.group(2).split(",") if kw.strip()]
    lua_keywords[unit_key] = kws

# Build Unit_Keywords for our new units using the template unit's keywords
new_unit_keywords: dict[str, list[str]] = {}
for new_unit, template_unit in UNIT_TEMPLATES.items():
    if template_unit in lua_keywords:
        new_unit_keywords[new_unit] = lua_keywords[template_unit]
    else:
        print(f"WARNING: no keywords found for template unit '{template_unit}'")

# Render Unit_Keywords table as lua
kw_lines = []
for unit, kws in new_unit_keywords.items():
    kw_str = ", ".join(f'"{k}"' for k in kws)
    kw_lines.append(f'    ["{unit}"] = {{{kw_str}}},')
unit_keywords_lua = "\n".join(kw_lines)

with open(lua_template_path, "r", encoding="utf-8") as f:
    lua_script = f.read()

# Replace mod_name so it matches the generated script's name
lua_script = re.sub(
    r'local mod_name\s*=\s*"[^"]*"',
    f'local mod_name = "{ror_table_name}"',
    lua_script,
    count=1,
)

# Replace the Unit_Keywords block content
lua_script = re.sub(
    r"(local Unit_Keywords\s*=\s*\{)[^}]*(})",
    lambda m: m.group(1) + "\n" + unit_keywords_lua + "\n\n" + m.group(2),
    lua_script,
    count=1,
    flags=re.DOTALL,
)

lua_out_path.parent.mkdir(parents=True, exist_ok=True)
with open(lua_out_path, "w", encoding="utf-8") as f:
    f.write(lua_script)

print(f"Wrote lua script with {len(new_unit_keywords)} unit keyword entries.")


effects_out_dir.mkdir(parents=True, exist_ok=True)
out_path = effects_out_dir / f"{ror_table_name}.tsv"
header = f"#unit_purchasable_effect_sets_tables;0;db/unit_purchasable_effect_sets_tables/{ror_table_name}"
print(header)
write_tw_tsv(ror_df, out_path, header_line=header)

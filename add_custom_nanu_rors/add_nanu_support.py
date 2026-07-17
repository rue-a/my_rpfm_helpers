# %%
import os
from pathlib import Path
import pandas as pd
from io import StringIO

HERE = Path(__file__).parent


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


nanu_mod_path = "/home/rue/WH3-Mods/Mods/!LOOKUP/!!_nanu_dynamic_rors/db/unit_purchasable_effect_sets_tables"
reference_tables = ["nanu_dynamic_rors_emp.tsv", "nanu_dynamic_rors_dwf.tsv"]
reference_tables = [f"{nanu_mod_path}/{ref}" for ref in reference_tables]

reference_df = read_tw_tsvs(reference_tables)


ror_df = pd.DataFrame(columns=reference_df.columns)
# Step 1: Define which units serve as tempalte (main units)
unit_templates = {
    "ruene_kislev_techs_ksl_war_wagon_rifle_main_unit": "wh2_dlc13_emp_veh_war_wagon_0",
    "ruene_kislev_techs_ksl_war_wagon_mortar_main_unit": "wh2_dlc13_emp_veh_war_wagon_1",
    "ruene_calm_erengrad_cannon_main_unit": "wh_main_dwf_art_cannon",
    "ruene_calm_urugan_cannon_main_unit": "wh_main_dwf_art_organ_gun",
}

# Step 2: For each template unit, copy matching rows and remap unit name to the new key
template_values = list(unit_templates.values())
matched = reference_df[reference_df["unit"].isin(template_values)].copy()
value_to_key = {v: k for k, v in unit_templates.items()}
matched["unit"] = matched["unit"].map(value_to_key)
ror_df = pd.concat([ror_df, matched], ignore_index=True)


# Step 3: Parse nanu lua data file for keywords of each template unit, then emit lua script
import re

nanu_lua_path = "/home/rue/WH3-Mods/Mods/!LOOKUP/!!_nanu_dynamic_rors/script/campaign/mod/nanu_dynamic_ror_data.lua"
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
for new_unit, template_unit in unit_templates.items():
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

lua_template_path = HERE / "template_units_nanu_rors.lua"
with open(lua_template_path, "r", encoding="utf-8") as f:
    lua_script = f.read()

# Replace the Unit_Keywords block content
lua_script = re.sub(
    r"(local Unit_Keywords\s*=\s*\{)[^}]*(})",
    lambda m: m.group(1) + "\n" + unit_keywords_lua + "\n\n" + m.group(2),
    lua_script,
    count=1,
    flags=re.DOTALL,
)

lua_out_path = HERE / "custom_units_nanu_rors.lua"
with open(lua_out_path, "w", encoding="utf-8") as f:
    f.write(lua_script)

print(f"Wrote lua script with {len(new_unit_keywords)} unit keyword entries.")


ror_table_name = "ruene_kislev_merc_techs_nanu_dynamic_rors"
out_dir = HERE / "unit_purchasable_effect_sets_tables"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / f"{ror_table_name}.tsv"
header = f"#unit_purchasable_effect_sets_tables;0;db/unit_purchasable_effect_sets_tables/{ror_table_name}"
print(header)
write_tw_tsv(ror_df, out_path, header_line=header)

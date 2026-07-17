----------------------------------------------------------------------------------------------------
----------------------------------- Modded Dynamic RoR Script --------------------------------------
----------------------------------------------------------------------------------------------------
----																							----
----	This script is how you will add your Dynamic RoR effects, as well as keywords for your  ----
----    custom units, factions, and cultures. You must rename this script to a custom name.     ----
----    You also need to add a custom name to the mod_name variable below. I recommend using    ----
----    the same name as your script.                                                           ----
----																							----
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------

--replace this with the custom name you renamed this script to
local mod_name = "template_units_nanu_rors"

---------------------------------------- GLOBAL VARIABLES ------------------------------------------
---     These global variables are used by the main mod. Leave them alone and do not            ----
---     rename them.                                                                            ----
----------------------------------------------------------------------------------------------------

Dynamic_RoR_ModList = {};
Dynamic_RoR_Modded_Effect_List = {};
Dynamic_RoR_Modded_Unit_Keywords = {};
Dynamic_RoR_Modded_Faction_Keywords = {};
Dynamic_RoR_Modded_Legendary_Lord_Keywords = {};
Dynamic_RoR_Modded_Culture_Keywords = {};
Dynamic_RoR_Modded_Region_Data = {};
Dynamic_RoR_Modded_NameData = {
    ["noun"] = {},
    ["adjective"] = {}
};


------------------------------------------ EFFECT LIST ---------------------------------------------
---     If you've made any custom dynamic ror effects, put them in this local variable          ----
----------------------------------------------------------------------------------------------------

local Effect_List = {};


------------------------------------------ UNIT KEYWORDS -------------------------------------------
---     Use this list to add additional keywords to your units. These keywords are used         ----
---     for name generation.                                                                    ----
----------------------------------------------------------------------------------------------------

local Unit_Keywords = {
    ["ruene_kislev_techs_ksl_war_wagon_rifle_main_unit"] = {"empire_culture", "handgun", "powder_unit", "rifle"},
    ["ruene_kislev_techs_ksl_war_wagon_mortar_main_unit"] = {"empire_culture", "powder_unit", "artillery", "mortar"},
    ["ruene_calm_erengrad_cannon_main_unit"] = {"dwarf_culture", "powder_unit"},
    ["ruene_calm_urugan_cannon_main_unit"] = {"dwarf_culture", "powder_unit"},

};


-------------------------------------- LEGENDARY LORD KEYWORDS -------------------------------------
---     Use this list to add additional keywords to your legendary lords. These keywords are    ----
---     used for both special effects and name generation. All special effects that use these   ----
---     keywords must include "<keyword>_lord" to be picked up by the script                    ----
----------------------------------------------------------------------------------------------------

local Legendary_Lord_Keywords = {};


----------------------------------------- FACTION KEYWORDS -----------------------------------------
---     Use this list to add keywords to custom factions. These keywords are used for both      ----
---     special effects and name generation.                                                    ----
----------------------------------------------------------------------------------------------------

local Faction_Keywords = {};

----------------------------------------- CULTURE KEYWORDS -----------------------------------------
---     Use this list for custom cultures. These keywords are  used for both special effects    ----
---     and name generation. Sartosa Overhaul doesn't use custom cultures so I've added a       ----
---     template for Cataph's Southern Realms                                                   ----
----------------------------------------------------------------------------------------------------

local Culture_Keywords = {
    --["mixer_teb_southern_realms"] = {"southern_realms", "human", "order", "knight"},
};


------------------------------------------- REGION DATA --------------------------------------------
---     Use this list for custom region name data. Useful for map overhauls like IEE and the    ----
---     Old World Modd. This must be a nested array.                                            ----
----------------------------------------------------------------------------------------------------

local Region_Data = {};


-------------------------------------------- NAME DATA ---------------------------------------------
---     Custom names and adjectives go here. This table follows the same format as              ----
---     Dynamic_RoR_NameData in the main mod                                                    ----
----------------------------------------------------------------------------------------------------

local NameData = {};


------------------------------------------ DANGER ZONE ---------------------------------------------
---     If you're scrolling past here, its because you're curious how the script works. If      ----
---     you're here to make changes or otherwise alter this script scroll back up. Begone foul  ----
---     beast. No touchy.                                                                       ----
----------------------------------------------------------------------------------------------------


--------------------------------------------- SCRIPT -----------------------------------------------
---     Script to apply the data above to the mod. Do not edit it, it works as is.              ----
----------------------------------------------------------------------------------------------------

if not mod_name or mod_name == "" then
    return;
else
    Dynamic_RoR_ModList[mod_name] = false;
    core:add_listener(
        "DynamicRoR_RegisterMod_" .. mod_name,
        "DynamicRoR_RegisterMods",
        true,
        function(context)
            if not pcall(
                    function()
                        out("  DynamicRoR_RegisterMod started for mod: " .. mod_name);

                        ------- EFFECTS -------
                        for _, effect in pairs(Effect_List) do
                            table.insert(Dynamic_RoR_Modded_Effect_List, #Dynamic_RoR_Modded_Effect_List + 1, effect);
                        end

                        ------- UNIT KEYWORDS -------
                        for unit_key, keywords in pairs(Unit_Keywords) do
                            if Dynamic_RoR_Modded_Unit_Keywords[unit_key] then
                                for _, keyword in pairs(keywords) do
                                    table.insert_if_absent(Dynamic_RoR_Modded_Unit_Keywords[unit_key], keyword)
                                end
                            else
                                Dynamic_RoR_Modded_Unit_Keywords[unit_key] = keywords;
                            end
                        end

                        ------- LEGENDARY LORD KEYWORDS -------
                        for subtype_key, keywords in pairs(Legendary_Lord_Keywords) do
                            if Dynamic_RoR_Modded_Legendary_Lord_Keywords[subtype_key] then
                                for _, keyword in pairs(keywords) do
                                    table.insert_if_absent(Dynamic_RoR_Modded_Legendary_Lord_Keywords[subtype_key],
                                        keyword)
                                end
                            else
                                Dynamic_RoR_Modded_Legendary_Lord_Keywords[subtype_key] = keywords;
                            end
                        end

                        ------- FACTION KEYWORDS -------
                        for faction_key, keywords in pairs(Faction_Keywords) do
                            if Dynamic_RoR_Modded_Faction_Keywords[faction_key] then
                                for _, keyword in pairs(keywords) do
                                    table.insert_if_absent(Dynamic_RoR_Modded_Faction_Keywords[faction_key], keyword)
                                end
                            else
                                Dynamic_RoR_Modded_Faction_Keywords[faction_key] = keywords;
                            end
                        end

                        ------- CULTURE KEYWORDS -------
                        for culture_key, keywords in pairs(Culture_Keywords) do
                            if Dynamic_RoR_Modded_Culture_Keywords[culture_key] then
                                for _, keyword in pairs(keywords) do
                                    table.insert_if_absent(Dynamic_RoR_Modded_Culture_Keywords[culture_key], keyword)
                                end
                            else
                                Dynamic_RoR_Modded_Culture_Keywords[culture_key] = keywords;
                            end
                        end

                        ------- NAME DATA -------
                        if not Dynamic_RoR_Modded_NameData["noun"] then
                            Dynamic_RoR_Modded_NameData["noun"] = {};
                        end
                        if not Dynamic_RoR_Modded_NameData["adjective"] then
                            Dynamic_RoR_Modded_NameData["adjective"] = {};
                        end

                        nouns = NameData["noun"];
                        adjectives = NameData["adjective"];

                        if nouns then
                            for culture_keyword, keyword_list in pairs(nouns) do
                                if Dynamic_RoR_Modded_NameData["noun"][culture_keyword] then
                                    for keyword, word_list in pairs(keyword_list) do
                                        if Dynamic_RoR_Modded_NameData["noun"][culture_keyword][keyword] then
                                            for _, word in pairs(word_list) do
                                                table.insert(
                                                    Dynamic_RoR_Modded_NameData["noun"][culture_keyword][keyword],
                                                    #Dynamic_RoR_Modded_NameData["noun"][culture_keyword][keyword] + 1,
                                                    word);
                                            end
                                        else
                                            Dynamic_RoR_Modded_NameData["noun"][culture_keyword][keyword] = word_list
                                        end
                                    end
                                else
                                    Dynamic_RoR_Modded_NameData["noun"][culture_keyword] = keyword_list;
                                end
                            end
                        end

                        if adjectives then
                            for culture_keyword, keyword_list in pairs(adjectives) do
                                if Dynamic_RoR_Modded_NameData["adjective"][culture_keyword] then
                                    for keyword, word_list in pairs(keyword_list) do
                                        if Dynamic_RoR_Modded_NameData["adjective"][culture_keyword][keyword] then
                                            for _, word in pairs(word_list) do
                                                table.insert(
                                                    Dynamic_RoR_Modded_NameData["adjective"][culture_keyword][keyword],
                                                    #Dynamic_RoR_Modded_NameData["adjective"][culture_keyword][keyword] +
                                                    1, word);
                                            end
                                        else
                                            Dynamic_RoR_Modded_NameData["adjective"][culture_keyword][keyword] =
                                                word_list
                                        end
                                    end
                                else
                                    Dynamic_RoR_Modded_NameData["adjective"][culture_keyword] = keyword_list;
                                end
                            end
                        end


                        ------- REGION DATA -------
                        for region_key, data in pairs(Region_Data) do
                            if not Dynamic_RoR_Modded_Region_Data[region_key] then
                                Dynamic_RoR_Modded_Region_Data[region_key] = {};
                            end
                            for i, value in pairs(data) do
                                table.insert(Dynamic_RoR_Modded_Region_Data[region_key],
                                    #Dynamic_RoR_Modded_Region_Data[region_key] + 1, value);
                            end
                        end

                        out("  DynamicRoR_RegisterMod completed for mod: " .. mod_name);
                    end)
            then
                out("\t\tBIG FAT SCRIPT ERROR! DYNAMIC ROR COMPATIBLE MOD \"" .. mod_name .. "\" FAILED TO LOAD DATA!")
            end
            core:trigger_custom_event("DynamicRoRModReady", { mod_name = mod_name })
        end,
        true
    );
end

--helper functions, leave these alone too
function table.insert_if_absent(self, value)
    if not table.check_value(self, value) then
        table.insert(self, #self + 1, value);
    end
end

function table.check_value(self, value)
    for _, k in pairs(self) do
        if k == value then
            return true;
        end
    end
    return false;
end

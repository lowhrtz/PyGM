from DbDefs import Table

class occ(Table):
    table_name = 'occ'
    cols = ['name', 'skill', 'ppe']
    colDefs = ['VARCHAR(20)', 'TEXT', 'INTEGER']
    data = [
        ['Bounty Hunter', 'Rifle', 5],
        ['Techno Wizard', 'Basic Electronics', 30]
    ]

class pc(Table):
    table_name = 'pc'
    cols = ['name', 'class', 'level',]
    colDefs = ['VARCHAR(20)', 'VARCHAR(20)', 'INTEGER']
    data = [
        ['Boris', 'Fighter', 2],
        ['Galadriel', 'Elf', 1],
        ]
        
class cClass(Table):
    table_name = 'class'
    cols = ['name', 'hd', 'spellcaster']
    colDefs = ['VARCHAR(20)', 'INTEGER', 'BOOLEAN']
    data = [
        ['Fighter', 8, False],
        ['Cleric', 6, True],
        ]

class items(Table):
    table_name = 'items'
    cols = ['unique_id', 'name', 'category', 'cost', 'weight', 'count', 'capacity', 'description', 'damage', 'range', 'DC', 'dc_loc_head_helm', 'dc_loc_main_body', 'dc_loc_arm_l', 'dc_loc_arm_r', 'dc_loc_leg_l', 'dc_loc_leg_r']
    colDefs = ['VARCHAR(20) UNIQUE', 'VARCHAR(50)', 'VARCHAR(50)', 'INTEGER', 'VARCHAR(20)', 'INTEGER', 'VARCHAR(10)', 'TEXT', 'VARCHAR(20)', 'VARCHAR(20)', 'VARCHAR(5)', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER']
    display_col = 1
    data = [
    ['air_filter', 'Air Filter', 'Adventuring & Camping Equipment', 5, '< 1 oz', 12, 'NULL', 'Disposable air filter usually used to block heavy dust.', 'NULL', 'NULL', 'NA', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'],
    ['ani_trap_s', 'Animal Trap, small', 'Adventuring & Camping Equipment', 40, '10 lbs', 1, 'NULL', 'Animal trap for small game like rabbit or vole.', 'NULL', 'NULL', 'SDC', 'NULL', 5, 'NULL', 'NULL', 'NULL', 'NULL'],
    ['ani_trap_l', 'Animal Trap, large', 'Adventuring & Camping Equipment', 120, '50 lbs', 1, 'NULL', 'Animal trap for large game like bears and wolves.', 'NULL', 'NULL', 'SDC', 'NULL', 15, 'NULL', 'NULL', 'NULL', 'NULL'],
    ['backpack_l', 'Backpack, large', 'Adventuring & Camping Equipment', 150, '5 lbs', 1, 'NULL', 'Large pack for carrying equipment etc.', 'NULL', 'NULL', 'SDC', 'NULL', 5, 'NULL', 'NULL', 'NULL', 'NULL'],
    ['backpack_s', 'Backpack, small', 'Adventuring & Camping Equipment', 70, '5 lbs', 1, 'NULL', 'Small pack for carrying equipment etc.', 'NULL', 'NULL', 'SDC', 'NULL', 2, 'NULL', 'NULL', 'NULL', 'NULL'],
    ['bandages_sa', 'Bandages, Self-Adhesive', 'Adventuring & Camping Equipment', 5, '8 oz', 72, 'NULL', 'Self-adhesive bandages to treat minor injuries.', 'NULL', 'NULL', 'NA', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'],
    ['bandages_roll', "Bandages, 6'/1.8 m roll", 'Adventuring & Camping Equipment', 5, '8 oz', 1, 'NULL', 'Rolled bandage to treat minor injuries.', 'NULL', 'NULL', 'NA', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'],
    ['bandoleer', "Bandoleer", 'Adventuring & Camping Equipment', 18, '2 lbs', 1, 'NULL', 'Shoulder belt for holding ammo etc.', 'NULL', 'NULL', 'SDC', 'NULL', 2, 'NULL', 'NULL', 'NULL', 'NULL'],
    ]

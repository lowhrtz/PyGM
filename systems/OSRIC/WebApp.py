import DbQuery
import SystemSettings
from base64 import b64decode
from resources import icon_png
from urllib.parse import parse_qs


def get_index(environ):
    fields = environ['Fields']
    campaign = environ['Extern']
    if fields['Font Radio Button'] == 0:
        font_css = get_builtin_font_css(fields['BuiltIn Fonts'])
    else:
        try:
            chosen_font = [f for f in campaign['Resources'] if f['Entry_ID'] == fields['Custom Fonts']][0]
            font_css = get_custom_font_css(chosen_font['Data'])
        except IndexError:
            font_css = get_builtin_font_css('Times')
    if fields['Handouts Background Light Dark'] == 0:
        handouts_title_color = 'darkslategrey'
    else:
        handouts_title_color = 'lightgrey'
    html = '''\
<!DOCTYPE html><html>
<head>
<meta charset="utf-8"/>
<link rel="icon" type="image/png"
 href="/icon.png">
<script>
function openMenu() {
    document.getElementById("menu").style.width = "500px";
}

function closeMenu() {
    document.getElementById("menu").style.width = "0";
}

function openItem(item, post=null) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("main").innerHTML = this.responseText;
            closeMenu();
        } else if (this.status == 404) {
            closeMenu();
        }
    };
    if (post == null) {
        xhttp.open("GET", item, true);
        xhttp.send();
    } else {
        xhttp.open("POST", item, true);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.send(post);
    }
}

function createOrChooseCharacter() {
    var create_checked = document.getElementById('c').checked;
    if (create_checked) {
        openItem('create_page');
    } else {
        openItem('list_characters');
    }
}

function hoverOnCharacter(id, mouse_on) {
    var summary = document.getElementById(id + '_summary');
    if (mouse_on) {
        summary.style.maxHeight = "500px";
        summary.style.border = "5px solid gray";
    } else {
        summary.style.maxHeight = "0";
        summary.style.border = "none";
    }
}

function chooseExistingCharacter() {
    var chosen_character_id = document.querySelector('input[name="characters"]:checked').value;
    openItem('choose_character', 'character_id=' + chosen_character_id)
}

function toggleBonus(element_id) {
    bonus_element = document.getElementById(element_id);
    if (bonus_element.style.display == 'none' || bonus_element.style.display == '') {
        bonus_element.style.display = 'block';
    } else {
        bonus_element.style.display = 'none';
    }
}

function changeCharacterPage(page_id) {
    var character_pages = document.getElementsByClassName("character_page");
    for (i = 0; i < character_pages.length; i++) {
        character_pages[i].style.display = "none";
    }
    
    document.getElementById(page_id).style.display = "block";
}

function saveBackground() {
    var background = document.getElementById("background_text").value;
    var character_id = document.getElementById("character_id").value;
    openItem('save_background', 'character_id=' + character_id + '&background=' + background);
}
</script>

<style>

h1, h2, h3 {
    text-align: center;
    font-weight: normal;
}

h1 {
    font-size: 600%;
}

h2 {
    font-size: 500%;
}

h3 {
    font-size: 400%;
}

img {
    border: 5px inset lightgrey;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

legend {
    padding-left: 15px;
    padding-right: 15px;
}

fieldset {
    border: 1px solid black;
    border-radius: 15px;
    margin: 10px 5px;
}

.menuButton {
    padding: 15px;
    font-size: 60px;
    transition: 0.3s;
}

.menuButton:hover {
    color: #999;
}

#menu {
    height: 100%;
    width: 0;
    position: fixed;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: #111;
    overflow-x: hidden;
    transition: 0.5s;
    padding-top: 90px;
}

#menu a {
  padding: 8px 8px 8px 32px;
  text-decoration: none;
  font-size: 60px;
  color: #818181;
  display: block;
  transition: 0.3s;
}

#menu a:hover {
    color: #f1f1f1;
}

#menu .menuItem {
  border-bottom: 1px solid white;
}

#menu .closeButton {
  position: absolute;
  top: 0;
  right: 25px;
  font-size: 60px;
  margin-left: 50px;
}

div.character_area {
    font-size: 60px;
    text-align: center;
    margin-top: 100px;
}

div.character_area input[type=radio] {
    height:50px;
    width:50px;
}

div.character_area button {
    font-size: 60px;
    padding: 20px;
    margin-top: 20px;
}

div.character_area label.character_list {
    transition: color 0.5s;
}

div.character_area label.character_list:hover {
    color: #555;
}

div.character_summary {
    background: black;
    font-size: 35px;
    color: gray;
    width: 600px;
    max-height: 0;
    margin-left: auto;
    margin-right: auto;
    border-radius: 10%;
    overflow: hidden;
    transition: 0.5s;
}

div.character_summary img {
    margin: 15px;
    float: left;
    max-height: 200px;
    max-width: 200px;
}

div.character_sheet {
     text-align: center;
     font-size: 60px;
}

div.character_page {
    display: none;
}

div.character_menu {
    margin-top: 20px;
    line-height: 150%;
}

div.character_menu span {
    background: gray;
    border: 3px outset #cfcfcf;
    padding: 10px;
    margin: 10px;
    font-size: 20px;
}

div.character_menu span:active {
    background: #999;
}

.bonus {
    background: black;
    color: lightgray;
    padding: 5px;
    display: none;
    border: 5px outset #cfcfcf;
    border-radius: 20px;
    font-size: 30px;
}

div.more_info + div {
    display: none;
    font-size: 60%;
    border: 4px outset #cfcfcf;
    border-radius: 15px;
    background: black;
    color: lightgray;
    padding: 5px;
}

div.more_info:hover + div {
    display: block;
}

div.spell + div {
    text-align: left;
    padding: 10px;
}

'''

    background_image_css = ''
    if fields['Title BG Preview']:
        background_image_css = f'''\
    background-image: url('data:image;base64,{fields['Title BG Preview']}');
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    box-shadow:inset 0 0 10px 5px black;
'''

    html += f'''
div.title {{
{background_image_css}
}}

div.handouts {{
    width: 820px;
    margin-left: auto;
    margin-right: auto;
    margin-top: 100px;
    font-size: 400%;
    color: {handouts_title_color};
    background-image: url(data:image;base64,{fields['Handouts Background Preview']});
    padding: 30px;
    border-radius: 25px;
    border: 8px outset darkgrey;
}}

{font_css}

</style>
</head>

<body style="background: {fields['Chosen Color']}">
<span class="menuButton" onclick="openMenu()">&#9776; Menu</span>
<div id="menu">
    <a href="javascript:void(0)" class="closeButton" onclick="closeMenu()">&#x274E;</a>
    <a class="menuItem" onclick="openItem('title')">Title</a>
    <a class="menuItem" onclick="openItem('handouts')">Handouts</a>
    <a class="menuItem" onclick="openItem('character')">Character</a>
    <a class="menuItem" onclick="openItem('send_message')">Send Message</a>
</div>
<span id="main">
{get_title(environ)}
</span>
</body>
</html>
'''

    return html


def get_title(environ):
    fields = environ['Fields']
    campaign = environ['Extern']
    return f'''\
<div class="title">
<h1>{fields['Title']}</h1>
<h3>An Adventure in <i>{campaign['Setting']}</i> for the <i>{campaign['Name']}</i> campaign</h3>
</div>
'''


def get_handouts(environ):
    fields = environ['Fields']
    image_tags = ''
    for res in fields['Image Resources']:
        image_tags += f'<img width=800 src=data:image;base64,{res["Data"]} /><br />'
    if image_tags:
        html = f'<div class="handouts">Handouts{image_tags}</div>'
    else:
        html = '<h1>There are no handouts available yet.</h1>'
    return html


def get_character(environ):
    remote_addr = environ['REMOTE_ADDR']
    webapp_table = DbQuery.getTable('WebApp')
    for entry in webapp_table:
        if entry['remote_addr'] == remote_addr:
            return get_existing_character(environ, entry['character_id'])
    return get_new_character(environ)


def get_character_html(character_dict):
    get_bonus_string = SystemSettings.get_attribute_bonus_string
    class_dict = SystemSettings.get_class_dict(character_dict)
    race_dict = {}
    for race in DbQuery.getTable('Races'):
        if race['unique_id'] == character_dict['Race']:
            race_dict = race
    equip_id_list = []
    spellbook_id_list = []
    daily_spells_id_list = []
    daily_spells2_id_list = []
    daily_spells3_id_list = []
    proficiency_id_dict = {}
    gp = pp = ep = sp = cp = 0
    for meta_row in character_dict['Characters_meta']:
        if meta_row['Type'] == 'Equipment':
            equip_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'Treasure':
            if meta_row['Entry_ID'] == 'gp':
                gp = meta_row['Data']

            elif meta_row['Entry_ID'] == 'pp':
                pp = meta_row['Data']

            elif meta_row['Entry_ID'] == 'ep':
                ep = meta_row['Data']

            elif meta_row['Entry_ID'] == 'sp':
                sp = meta_row['Data']

            elif meta_row['Entry_ID'] == 'cp':
                cp = meta_row['Data']
        elif meta_row['Type'] == 'Spellbook':
            spellbook_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'DailySpells':
            daily_spells_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'DailySpells2':
            daily_spells2_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'DailySpells3':
            daily_spells3_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'Proficiency':
            proficiency_id_dict[meta_row['Entry_ID']] = meta_row['Data']

    items_table = DbQuery.getTable('Items')
    proficiency_list = []
    specialised_list = []
    double_specialised_list = []
    for prof in items_table:
        if prof['Is_Proficiency'].lower() == 'yes' and prof['unique_id'] in list(proficiency_id_dict.keys()):
            prof_level = proficiency_id_dict[prof['unique_id']]
            if prof_level == 'P':
                proficiency_list.append(prof)
            elif prof_level == 'S':
                specialised_list.append(prof)
            elif prof_level == '2XS':
                double_specialised_list.append(prof)

    indexed_items = {item['unique_id']: item for item in items_table}
    equipment_list = [indexed_items[equip_id] for equip_id in equip_id_list]

    level = character_dict['Level']
    class_abilities = {}
    if 'classes' in class_dict:
        level_list = [int(lvl) for lvl in level.split('/')]
        for i, cl in enumerate(class_dict['classes']):
            class_abilities[cl['Name']] = SystemSettings.get_class_abilities(level_list[i], character_dict, cl)
    else:
        class_abilities[class_dict['Name']] = SystemSettings.get_class_abilities(level, character_dict, class_dict)
    race_abilities = SystemSettings.get_race_abilities(race_dict)

    spells_table = DbQuery.getTable('Spells')
    spellbook = []
    daily_spells = []
    daily_spells2 = []
    daily_spells3 = []
    for spell in spells_table:
        if spell['spell_id'] in spellbook_id_list:
            spellbook.append(spell)
        if spell['spell_id'] in daily_spells_id_list:
            daily_spells.append(spell)
        if spell['spell_id'] in daily_spells2_id_list:
            daily_spells2.append(spell)
        if spell['spell_id'] in daily_spells3_id_list:
            daily_spells3.append(spell)
    ac = SystemSettings.calculate_ac(character_dict, class_dict, race_dict, equipment_list)
    saves_dict = SystemSettings.get_saves(level, character_dict, class_dict, race_dict)
    movement_tuple = SystemSettings.calculate_movement(race_dict, class_dict, character_dict, equipment_list)
    movement_rate, movement_desc = movement_tuple
    html = f'''\
<div class="character_sheet">
<input type="hidden" id="character_id" value="{character_dict['unique_id']}" />

<div class="character_page" style="display: block;" id="basic_info">
<span style="position: absolute; left: 30px;"><b>HP:</b> {character_dict['HP']}<br /><b>AC:</b> {ac}</span>
<img style="height: 600px; margin: 30px auto 30px auto;" src="data:image;base64,{character_dict['Portrait']}" />
<b>{character_dict['Name']}</b><br />
<b>Level:</b> {character_dict['Level']}<br />
<b>Class:</b> {SystemSettings.get_class_names(character_dict)}<br />
<b>Race:</b> {race_dict['Name']}<br />
<b>Alignment:</b> {character_dict['Alignment']}
</div>

<div class="character_page" id="attributes">
<table style="padding: 20px;">
<tr><th>Str:</th><td onclick="toggleBonus('str_bonus')">{character_dict['STR']}</td><td class="bonus" id="str_bonus">{get_bonus_string('STR', character_dict['STR'])}</td></tr>
<tr><th>Int:</th><td onclick="toggleBonus('int_bonus')">{character_dict['INT']}</td><td class="bonus" id="int_bonus">{get_bonus_string('INT', character_dict['INT'])}</td></tr>
<tr><th>Wis:</th><td onclick="toggleBonus('wis_bonus')">{character_dict['WIS']}</td><td class="bonus" id="wis_bonus">{get_bonus_string('WIS', character_dict['WIS'])}</td></tr>
<tr><th>Dex:</th><td onclick="toggleBonus('dex_bonus')">{character_dict['DEX']}</td><td class="bonus" id="dex_bonus">{get_bonus_string('DEX', character_dict['DEX'])}</td></tr>
<tr><th>Con:</th><td onclick="toggleBonus('con_bonus')">{character_dict['CON']}</td><td class="bonus" id="con_bonus">{get_bonus_string('CON', character_dict['CON'])}</td></tr>
<tr><th>Cha:</th><td onclick="toggleBonus('cha_bonus')">{character_dict['CHA']}</td><td class="bonus" id="cha_bonus">{get_bonus_string('CHA', character_dict['CHA'])}</td></tr>
</table>
<hr />
<b>Saving Throws</b>
<div style="font-size: 50%;">
<b>Aimed Magic Items:</b> {saves_dict['Aimed_Magic_Items']}<br />
<b>Breath Weapon:</b> {saves_dict['Breath_Weapons']}<br />
<b>Death, Paralysis, Poison:</b> {saves_dict['Death_Paralysis_Poison']}<br />
<b>Petrifaction, Polymorph:</b> {saves_dict['Petrifaction_Polymorph']}<br />
<b>Spells:</b> {saves_dict['Spells']}
</div>
</div>

<div class="character_page" id="equipment">
{''.join('<div class="more_info">' + e['Name'] + '</div><div>' + item_html(e) + '</div>' for e in equipment_list)}
<br />
<hr />
<b>PP:</b>{pp} <b>GP:</b>{gp} <b>SP:</b>{sp} <b>EP:</b>{ep} <b>CP:</b>{cp}
<hr />

</div>

<div class="character_page" id="abilities">
{class_abilities_html(class_abilities)}
{'<fieldset><legend><b>' + race_dict['Name'] + ' Abilities</b></legend>' +
 ''.join(f'<div>{ra[0]} {ra[1]} {ra[2]}</div>' for ra in race_abilities) + '</fieldset>' if race_abilities else ''}
{'<fieldset><legend><b>Spell Book</b></legend>' +
 ''.join('<div class="more_info spell">' + s['Name'] + '</div><div>' + spell_html(s) + '</div>' for s in spellbook)
 + '</fieldset>' if spellbook else ''}
{f'<fieldset><legend><b>{daily_spells[0]["Type"].title().replace("_", " ")} Daily Spells</b></legend>' +
 ''.join('<div class="more_info spell">' + s['Name'] + '</div><div>' + spell_html(s) + '</div>' for s in daily_spells)
 + '</fieldset>' if daily_spells else ''}
{f'<fieldset><legend><b>{daily_spells2[0]["Type"].title().replace("_", " ")} Daily Spells</b></legend>' +
 ''.join('<div class="more_info spell">' + s['Name'] + '</div><div>' + spell_html(s) + '</div>' for s in daily_spells2)
 + '</fieldset>' if daily_spells2 else ''}
{f'<fieldset><legend><b>{daily_spells3[0]["Type"].title().replace("_", " ")} Daily Spells</b></legend>' +
 ''.join('<div class="more_info spell">' + s['Name'] + '</div><div>' + spell_html(s) + '</div>' for s in daily_spells3)
 + '</fieldset>' if daily_spells3 else ''}
</div>

<div class="character_page" id="combat_info">
<table class="tohit-table" style="font-size: 50%; margin-top: 20px;" border=1 align=center>
<tr><td><b>Enemy AC</b></td><td align=center> -10 </td><td align=center> -9 </td><td align=center> -8 </td>
<td align=center> -7 </td><td align=center> -6 </td><td align=center> -5 </td>
<td align=center> -4 </td><td align=center> -3 </td><td align=center> -2 </td><td align=center> -1 </td>
<td align=center> 0 </td><td align=center> 1 </td><td align=center> 2 </td><td align=center> 3 </td>
<td align=center> 4 </td><td align=center> 5 </td><td align=center> 6 </td><td align=center> 7 </td>
<td align=center> 8 </td><td align=center> 9 </td><td align=center> 10 </td></tr>
<tr><td><b>To Hit</b></td>{'<td align=center>' + '</td><td align=center>'
        .join(SystemSettings.get_tohit_row(level, class_dict, race_dict)) + '</td>'}</tr>
</table>
<b>Movement Rate:</b> {movement_rate} ft/round<br />
<b>Surprise:</b> {movement_desc}<br />
<b>Non-Proficiency Penalty: </b> {SystemSettings.get_non_proficiency_penalty(class_dict, race_dict)}

{'<fieldset><legend><b>Proficiency</b></legend>' + '<br />'.join(p['Name'] for p in proficiency_list) +
'</fieldset>' if proficiency_list else ''}

{'<fieldset><legend><b>Specialised</b></legend>' + '<br />'.join(p['Name'] for p in specialised_list) +
 '</fieldset>' if specialised_list else ''}


{'<fieldset><legend><b>Double Specialised</b></legend>' + '<br />'.join(p['Name'] for p in double_specialised_list) +
 '</fieldset>' if double_specialised_list else ''}

</div>

<div class="character_page" id="personal_info">
<div style="margin: 15px 5px;">
<b>Height:</b> {character_dict['Height']} <b>Weight:</b> {character_dict['Weight']}<br />
<b>Sex:</b> {character_dict['Gender']}<br />
</div>
<b>Background</b><br />
<textarea style="font-size: 30px; margin-bottom: 35px;" id="background_text" rows=15 cols=35>
{character_dict['Background']}
</textarea><br />
<button style="font-size: 50px;" onclick="saveBackground()")">Save Background</button>
</div>

<div class="character_menu">
<span onclick="changeCharacterPage('basic_info')">Basic Info</span>
<span onclick="changeCharacterPage('attributes')">Attributes</span>
<span onclick="changeCharacterPage('equipment')">Equipment</span>
<span onclick="changeCharacterPage('abilities')">Abilities</span>
<span onclick="changeCharacterPage('combat_info')">Combat Info</span>
<span onclick="changeCharacterPage('personal_info')">Personal Info</span>
</div>
</div>
'''
    return html


def class_abilities_html(class_abilities):
    html = ''
    for ca in class_abilities:
        html += f'<div><fieldset><legend><b>{ca} Abilities</b></legend>'
        for cai in class_abilities[ca]:
            if cai[0]:
                html += f'<b>{cai[0]}:</b> {cai[1]}<br />'
            else:
                html += '<table style="font-size: 40%"><tr>'
                for caih in cai[1][0]:
                    html += f'<th>{caih}</th>'
                html += '</tr>'
                for caid in cai[1][1]:
                    html += f'<td>{caid}</td>'
                html += '</tr></table>'
        html += '</fieldset></div>'

    return html


def spell_html(spell):
    return f'''\
<b>Reversible: </b>{spell['Reversible']}<br />
<b>Level: </b>{spell['Level']}<br />
<b>Damage: </b>{spell['Damage']}<br />
<b>Range: </b>{spell['Range']}<br />
<b>Duration: </b>{spell['Duration']}<br />
<b>Area of Effect: </b>{spell['Area_of_Effect']}<br />
<b>Components: </b>{spell['Components']}<br />
<b>Casting Time: </b>{spell['Casting_Time']}<br />
<b>Saving Throw: </b>{spell['Saving_Throw']}<br />
<b>Description: </b>{spell['Description']}<br /><br />
'''


def item_html(item):
    return f'''\
{'<b>Magical</b><br />' if item['Is_Magic'].lower() == 'yes' else ''}
<b>Category:</b> {item['Category']}<br />
{'<b>Sub-Category:</b> ' + item['Subcategory'] + '<br />' if item['Subcategory'] else ''}
<b>Weight:</b> {item['Weight']}<br />
{'<b>Damage Vs S or M:</b> ' + item['Damage_Vs_S_or_M'] + '<br />' if item['Damage_Vs_S_or_M'] else ''}
{'<b>Damage Vs L:</b> ' + item['Damage_Vs_L'] + '<br />' if item['Damage_Vs_S_or_M'] else ''}
{'<b>Damage Type:</b> ' + item['Damage_Type'] + '<br />' if item['Damage_Type'] else ''}
{'<b>Rate of Fire:</b> ' + item['Rate_of_Fire'] + '<br />' if item['Rate_of_Fire'] else ''}
{'<b>Range:</b> ' + item['Range'] + '<br />' if item['Range'] else ''}
{'<b>AC Effect:</b> ' + str(item['AC_Effect']) + '<br />' if item['AC_Effect'] else ''}
{'<b>Notes:</b> ' + item['Notes'] + '<br />' if item['Notes'] else ''}
'''


def get_save_background(environ):
    raw_post = environ.get('wsgi.input', '')
    post = raw_post.read(int(environ.get('CONTENT_LENGTH', 0)))
    post_dict = parse_qs(post.decode(), True)
    character_id = post_dict.get('character_id', None)
    background = post_dict.get('background', None)
    if character_id and background:
        character_id = character_id[0]
        background = background[0]
        characters = DbQuery.getTable('Characters')
        for c in characters:
            if c['unique_id'] == character_id:
                DbQuery.update_cols('Characters', 'unique_id', character_id, ['Background'], (background, ))
                DbQuery.commit()
                return get_existing_character(environ, character_id)
    return '<h1>Problem saving background!</h1>'


def get_existing_character(_environ, character_id):
    # pcs = environ['Extern']['PCs']
    pcs = DbQuery.getTable('Characters')
    pcs_indexed = {pc['unique_id']: pc for pc in pcs}
    # for c in pcs:
    #     if c['unique_id'] == character_id:
    #         # return SystemSettings.get_character_pdf_markup(c)[1]
    #         return get_character_html(c)
    return get_character_html(pcs_indexed[character_id])
    # return '<h1>Problem!</h1>'


def get_new_character(_environ):
    # print(environ['REMOTE_ADDR'])
    return '''\
<div class="character_area">
<input type="radio" id="c" name="character" value="create" checked>
<label for="c">Create Character</label><br />
OR<br />
<input type="radio" id="r" name="character" value="register">
<label for="r">Choose Existing Character</label></input><br />
<button type="button" onclick="createOrChooseCharacter()">Next</button>
</div>
'''


def get_create_page(_environ):
    return '<h1>Not Implemented Yet!</h1>'


def get_list_character(environ):
    pcs = environ['Extern']['PCs']
    if len(pcs) == 0:
        names = 'No Characters Associated with Campaign'
    else:
        names = ''
        for i, c in enumerate(pcs):
            checked = ''
            br = '<br />'
            if i == 0:
                checked = 'checked'
            elif i == len(pcs) - 1:
                br = ''
            cn = c['Name']
            cid = c['unique_id']
            names += f'''\
<input type="radio" name="characters" value="{cid}" id="{cid}" {checked}>
<label for="{cid}" class="character_list"
onmouseover="hoverOnCharacter('{cid}', true)" onmouseout="hoverOnCharacter('{cid}', false )">{cn}</label>{br}
<div class="character_summary" id="{cid + '_summary'}"><img src="data:image;base64,{c['Portrait']}">{cn}<br />
Level {c['Level']} {SystemSettings.get_class_names(c)}</div>'''

    html = f'''\
<div class="character_area">
{names}
<button onclick="chooseExistingCharacter()">Choose</button>
</div>
'''
    return html


def get_choose_character(environ):
    if environ.get('REQUEST_METHOD', '') != 'POST':
        return ''
    raw_post = environ.get('wsgi.input', '')
    post = raw_post.read(int(environ.get('CONTENT_LENGTH', 0)))
    post_dict = parse_qs(post.decode(), True)
    character_id = post_dict.get('character_id', None)
    if character_id:
        character_id = character_id[0]
        pcs = environ['Extern'].get('PCs', [])
        for c in pcs:
            if c['unique_id'] == character_id:
                DbQuery.insertRow('WebApp', (environ['REMOTE_ADDR'], character_id))
                DbQuery.commit()
                return get_character_html(c)

    return ''


def get_builtin_font_css(font):
    return f'''
body, button {{
    font-family: {font};
}}
'''


def get_custom_font_css(font_base64):
    return f'''
@font-face {{
    font-family: CustomFont;
    src: url(data:font;base64,{font_base64});
}}

body, button {{
    font-family: CustomFont;
}}
'''


def get_favicon(_environ):
    return b64decode(icon_png)


def adventure(environ, start_response):
    status_ok = '200 OK'
    status_not_found = '404 Not Found'

    path_info = environ.get('PATH_INFO', '')
    content_type = [('Content-type', 'text/html')]

    if path_info == '' or path_info == '/':
        html = get_index(environ)
        status = status_ok
    elif path_info == '/title':
        html = get_title(environ)
        status = status_ok
    elif path_info == '/handouts':
        html = get_handouts(environ)
        status = status_ok
    elif path_info == '/character':
        html = get_character(environ)
        status = status_ok
    elif path_info == '/create_page':
        html = get_create_page(environ)
        status = status_ok
    elif path_info == '/list_characters':
        html = get_list_character(environ)
        status = status_ok
    elif path_info == '/choose_character':
        html = get_choose_character(environ)
        status = status_ok
    elif path_info == '/save_background':
        html = get_save_background(environ)
        status = status_ok
    elif path_info == '/icon.png':
        html = get_favicon(environ)
        status = status_ok
        content_type = [('Content-type', 'image/png')]
    else:
        html = '<h1>404 Page Not Found!</h1>'
        status = status_not_found

    if type(html) == str:
        html = html.encode('utf-8')

    start_response(status, content_type)
    return [html]

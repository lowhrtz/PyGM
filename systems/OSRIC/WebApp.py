import SystemSettings
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
    html = '''<!DOCTYPE html><html>
<head>
<meta charset="utf-8"/>
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

function createOrRegisterCharacter() {
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
</div>
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
<h1 background=>{fields['Title']}</h1>
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
    print(environ['REMOTE_ADDR'])
    return '''\
<div class="character_area">
<input type="radio" id="c" name="character" value="create" checked>
<label for="c">Create Character</label><br />
OR<br />
<input type="radio" id="r" name="character" value="register">
<label for="r">Register Character</label></input><br />
<button type="button" onclick="createOrRegisterCharacter()">Next</button>
</div>
'''


def get_create_page(environ):
    return ''


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
    raw_post = environ.get('wsgi.input', '')
    post = raw_post.read(int(environ.get('CONTENT_LENGTH', 0)))
    post_dict = parse_qs(post.decode(), True)
    character_id = post_dict.get('character_id', None)
    if character_id:
        character_id = character_id[0]
        pcs = environ['Extern'].get('PCs', [])
        for c in pcs:
            if c['unique_id'] == character_id:
                print(environ.get('chosen_pcs', None))
                environ['chosen_pcs'] = {environ['REMOTE_ADDR']: character_id}
                print(environ.get('chosen_pcs', None))
                return f'''<div style="font-size: 60px;">You Have Chosen: {c['Name']}</div>'''
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


def adventure(environ, start_response):
    status_ok = '200 OK'
    status_not_found = '404 Not Found'

    path_info = environ.get('PATH_INFO', '')

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
    else:
        html = '<h1>404 Page Not Found!</h1>'
        status = status_not_found

    start_response(status, [('Content-type', 'text/html')])
    return [html.encode('utf-8')]

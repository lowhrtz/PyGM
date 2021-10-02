import DbQuery
import resources
import SystemSettings
import time
from urllib.parse import parse_qs


def get_cc_html():
    return f'''\
<form id="cc_form" name="cc_form" style="text-align: center;" onkeydown="return event.key != 'Enter';">
<h1>Quick Character Creator</h1>
<hr />
<div class="page">
    <h2>Choose Race</h2>
    <select id="race" name="race">
    {get_races_html()}
    </select>
</div>

<div class="page">
    <h2>Choose Class</h2>
    <select id="classes" name="classes"></select>
</div>

<div class="page">
    <h2>Personal Information</h2>
    <input id="name" name="name" placeholder="Name" /><br /><br />
    <select id="gender" name="gender">
    {get_gender_html()}
    </select><br /><br />
    <select id="alignment" name="alignment"></select>
</div>

<div class="page">
    <h2>Portrait</h2>
    <image id="preview" name="preview" src="data:image;base64,{resources.rollBanner_jpg}" height=250 /><br /><br />
    <label for="portrait" style="font-size: 60px;">Choose Portrait</label><br />
    <input id="portrait" name="portrait" type="file" accept="image/*" style="font-size: 25px;" />
</div>

<div class="page">
    <h2>Summary</h2>
    <span id="summary" style="font-size: 60px;"></span>
</div>

<div style="overflow:auto; margin: 30px;">
    <div style="float:right;">
        <button style="font-size: 60px;" type="button" id="prevBtn">Previous</button>
        <button style="font-size: 60px;" type="button" id="nextBtn">Next</button>
    </div>
</div>
</form>

{get_script_html()}

'''


def get_races_html():
    return ' '.join([f'<option value="{i["unique_id"]}">{i["Name"]}</option>' for i in DbQuery.getTable('Races')])


def get_gender_html():
    return ' '.join([f'<option value="{g}">{g}</option>' for g in SystemSettings.gender])


def get_script_html():
    return '''\
<script id="wizardscript">
var currentPage = 0;
showPage(currentPage);

function showPage(i) {
    var pages = document.getElementsByClassName("page");
    pages[i].style.display = "block";
    
    prevBtn = document.getElementById("prevBtn")
    nextBtn = document.getElementById("nextBtn")
    if (i == 0) {
        prevBtn.style.display = "none";
    } else {
        prevBtn.style.display = "inline";
    }

    if (i == (pages.length - 1)) {
        nextBtn.innerHTML = "Finish";
    } else {
        nextBtn.innerHTML = "Next";
    }
}

function nextPrev(n) {
    var pages = document.getElementsByClassName("page");
    if (currentPage == 0) {
        selectClasses(); // This is invoked here because of the async nature of the calls
    } else if (currentPage == (pages.length - 2)) {
        fillSummary();
    }
    
    pages[currentPage].style.display = "none";
    
    currentPage += n;
    if (currentPage >= pages.length) {
        race = encodeURIComponent(document.getElementById("race").value);
        class_name = encodeURIComponent(document.getElementById("classes").value);
        name = encodeURIComponent(document.getElementById("name").value);
        gender = encodeURIComponent(document.getElementById("gender").value);
        alignment = encodeURIComponent(document.getElementById("alignment").value);
        portrait = encodeURIComponent(document.getElementById("preview").src.split(",")[1]);
        post = "race=" + race + "&classes=" + class_name + "&name=" + name +
            "&gender=" + gender + "&alignment=" + alignment + "&portrait=" + portrait;
        // console.log(post);
        openItem("/cc_submit", post);
        return false;
    }
    
    showPage(currentPage);
}

document.getElementById("prevBtn").onclick = function() {nextPrev(-1);};
document.getElementById("nextBtn").onclick = function() {nextPrev(1);};

function selectRace() {
    var race = document.getElementById("race").value;
    post = "race_id=" + race;
    // console.log(post);
    openItem("/classes_options", post, null, "classes");
}

selectRace();

document.getElementById("race").onchange = function() {selectRace();};

function selectClasses() {
    var class_name = document.getElementById("classes").value;
    post = "class_name=" + class_name;
    openItem("/alignment_options", post, null, "alignment");
}

document.getElementById("classes").onchange = function() {selectClasses();};

function setPreview() {
    var file_chooser = document.getElementById("portrait");
    var preview = document.getElementById("preview");
    file = file_chooser.files[0];
    if(file) {
        fr = new FileReader();
        fr.readAsDataURL(file);
        fr.onload = function () {
            preview.src = this.result;
        };
    }
}

document.getElementById("portrait").onchange = function() {setPreview();};

function fillSummary() {
    race_element = document.getElementById("race");
    race = race_element.options[race_element.selectedIndex].text
    class_name = document.getElementById("classes").value;
    name = document.getElementById("name").value;
    gender = document.getElementById("gender").value;
    alignment = document.getElementById("alignment").value;
    
    document.getElementById("summary").innerHTML =
    name + "<br />" +
    gender + " " + race + " " + class_name + "<br />" +
    alignment;
}
</script>
'''


def get_classes_options(environ):
    if environ.get('REQUEST_METHOD', '') != 'POST':
        return ''
    # print(f'ip = {environ["REMOTE_ADDR"]}')
    raw_post = environ.get('wsgi.input', '')
    post = raw_post.read(int(environ.get('CONTENT_LENGTH', 0)))
    post_dict = parse_qs(post.decode(), True)
    race_id = post_dict.get('race_id', None)
    if not race_id:
        return ''
    race = SystemSettings.get_race_dict({'Race': race_id[0]})
    class_options = []
    for races_meta in race['Races_meta']:
        if races_meta['Type'] == 'class' and races_meta['Subtype'] == 'permitted class options':
            class_options_string = races_meta['Modified']
            if not class_options_string:
                continue
            for class_option in class_options_string.split(','):
                class_option = class_option.strip()
                class_options.append((class_option.title().replace('_', ' '), class_option.replace('/', '_')))
    if not class_options:
        classes = DbQuery.getTable('Classes')
        class_options = [(normal_class['Name'], normal_class['unique_id']) for normal_class in classes]

    return ' '.join([f'<option value="{i[0]}">{i[0]}</option>' for i in class_options])


def get_alignment_options(environ):
    if environ.get('REQUEST_METHOD', '') != 'POST':
        return ''
    raw_post = environ.get('wsgi.input', '')
    post = raw_post.read(int(environ.get('CONTENT_LENGTH', 0)))
    post_dict = parse_qs(post.decode(), True)
    class_name = post_dict.get('class_name', None)
    if not class_name:
        return ''
    full_class = SystemSettings.get_full_class(class_name[0])
    alignment_options = SystemSettings.get_available_alignments(full_class)

    return ' '.join([f'<option value="{a}">{a}</option>' for a in alignment_options])


def cc_submit(environ):
    if environ.get('REQUEST_METHOD', '') != 'POST':
        return ''
    raw_post = environ.get('wsgi.input', '')
    post = raw_post.read(int(environ.get('CONTENT_LENGTH', 0)))
    post_dict = parse_qs(post.decode(), True)

    name = post_dict.get('name', [''])[0]
    gender = post_dict.get('gender', [''])[0]
    race_id = post_dict.get('race', [''])[0]
    class_name = post_dict.get('classes', [''])[0]
    alignment = post_dict.get('alignment', [''])[0]
    portrait = post_dict.get('portrait', [''])[0]
    full_class = SystemSettings.get_full_class(class_name)
    race = {r['unique_id']: r for r in DbQuery.getTable('Races')}[race_id]
    unique_id = f"{name.lower().replace(' ', '_')}-{full_class['unique_id']}-{time.time()}"

    if 'classes' in full_class:
        level = '/'.join('1' for _ in full_class['classes'])
        classes = '/'.join(cl['unique_id'] for cl in full_class['classes'])
        xp = '/'.join('0' for _ in full_class['classes'])
    else:
        level = '1'
        classes = full_class['unique_id']
        xp = '0'

    attr_dict = SystemSettings.roll_attributes(None, race, full_class)
    hp = SystemSettings.roll_hp(attr_dict, 1, full_class)
    age = SystemSettings.roll_age(race, full_class)
    height, weight = SystemSettings.roll_height_weight(race, gender)

    character_dict = {
        'unique_id': unique_id,
        'Name': name,
        'Level': level,
        'XP': xp,
        'Gender': gender,
        'Alignment': alignment,
        'Classes': classes,
        'Race': race_id,
        'HP': hp,
        'Age': age,
        'Height': f'{height[0]}ft {height[1]}in',
        'Weight': f'{weight} lbs',
        # 'Portrait': fields['Portrait'],
        'Portrait_Image_Type': 'jpg',
        'STR': attr_dict['STR'],
        'INT': attr_dict['INT'],
        'WIS': attr_dict['WIS'],
        'DEX': attr_dict['DEX'],
        'CON': attr_dict['CON'],
        'CHA': attr_dict['CHA'],
    }

    return f'''\
<div style="text-align: center; font-size: 50px;">
{name}<br />
{gender}<br />
{race_id}<br />
{class_name}<br />
{alignment}<br />
<image src="data:image;base64,{portrait}" style="height: 150px;" /><br />
{unique_id}
</div>
'''

def adventure(environ, start_response):
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
    html = '''<head>
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
'''
    html += f'''
div.handouts {{
    width: 820px;
    margin-left: auto;
    margin-right: auto;
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
<h1>{fields['Title']}</h1>
<h3>An Adventure in <i>{campaign['Setting']}</i> for the <i>{campaign['Name']}</i> campaign</h3>
'''
    image_tags = ''
    for res in fields['Image Resources']:
        image_tags += f'<img width=800 src=data:image;base64,{res["Data"]} /><br />'
    if image_tags:
        html += f'<div class="handouts">Handouts{image_tags}</div>'
    html += '</body>'

    start_response('200 OK', [('Content-type', 'text/html')])
    return [html.encode('utf-8')]


def get_builtin_font_css(font):
    return f'''
body {{
    font-family: {font};
}}
'''


def get_custom_font_css(font_base64):
    return f'''
@font-face {{
    font-family: CustomFont;
    src: url(data:font;base64,{font_base64});
}}

body {{
    font-family: CustomFont;
}}
'''

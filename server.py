from flask import Flask, escape, request, render_template, Markup
import re, os

VIDEOS_FOLDER = "static/videos"
FILE_IO_ERROR = "UNABLETOREADFILEFILEIOERROR"

app = Flask(__name__)

def getFile(filename):
    if os.path.exists(filename):
        f = open(filename, "r", encoding='utf8')
        return str(f.read())+"\n"
    else:
        return FILE_IO_ERROR
@app.route('/')
@app.route('/index')
def index():
    i = 0
    html = ""
    while True:
        meta = getFile(f"{VIDEOS_FOLDER}/id{i}/meta.txt")
        if meta == FILE_IO_ERROR:
            break
        else:
            result = re.search('TITLE:(.*)\n', meta)
            title = result.group(1)
            onHover = title
            if len(title) > 28:
                title = title[:25] + "..." # 25 is 3 less than 28 and "..." is three chars

            src = "/static/videos/id"+str(i)+"/thumbnail.png"
            alt = f"Video ID${i} thumbnail"
            width = 256
            height = width
            # <img src="" alt="" width="5%" height="5%">
            html += f'<div class="vidItem" title="{onHover}"><a href="play?id={i}"><img src={src} alt="{alt}" width="{width}" height="{height}">{title}</a></div>'
        i += 1
    return render_template("index.html", videos=Markup(html), title2="Press Ctrl+F to search for vid.")
@app.route("/upload")
def upload():
    html = """
    <center><h1>Upload Page</h1>

    </center>
    return render_template("index.html", videos=Markup(html), title2="title")
@app.route('/play')
def play():

    i = None
    try:
        i = int(request.args.get('id'))
    except:
        return render_template("404.html")
    id = f"id{i}"

    meta = getFile(f"{VIDEOS_FOLDER}/id{i}/meta.txt")
    if meta == FILE_IO_ERROR:
        return render_template("404.html")

    vidTitle = re.search('TITLE:(.*)\n', meta).group(1)
    vidDesc = re.search('DESCRIPTION:(.*)\n', meta).group(1)

    info = "<h3>Info About Vid:</h3>"
    try:
        info += """<p>
        Uploaded: {}</p>
        <p>Uploader: {}</p>"""
    except:
        info += "None"
    info = info.format(re.search('DATE:(.*)\n', meta).group(1), re.search('USER:(.*)\n', meta).group(1))

    # OG Vid size was w320 h240
    html = f"""<div id="playback" class="center"><video width="640" height="480" controls>
<source src="/static/videos/{id}/main_vid.mp4" type="video/mp4">
Your browser does not support the video tag.
</video><br><h3>Description:</h3><p>{vidDesc}</p>{info}</div>"""#
    return render_template("index.html", videos=Markup(html), id=id, title2=vidTitle) # note to self: IDK if id var is used ever
app.run(host='0.0.0.0', debug=True, port=80)

from flask import Flask, escape, request, render_template, Markup, redirect
from werkzeug.utils import secure_filename
import re, os, urllib.request
from sys import maxsize
from datetime import datetime

### Consts
VIDEOS_FOLDER = "static/videos"
FILE_IO_ERROR = "UNABLETOREADFILEFILEIOERROR"
#ALLOWED_EXTENSIONS = set(['mp4', 'mov'])
ALLOWED_EXTENSIONS = set(['wav', 'avi', 'mp3', 'mov', 'mp4', 'mpeg'])

### Globals
atLeast = 0

app = Flask(__name__)
def err(txt):
	return render_template("error.html", error=txt)
def mkdir(newpath):
	if not os.path.exists(newpath):
		os.makedirs(newpath)
def writeToFile(file, txt):
	with open(file, "w") as text_file:
		text_file.write(txt)
def updateleast(integer):
	global atLeast
	if integer > atLeast: atleats = integer
def getLastId():
	for i in range(atLeast, maxsize):
		if not os.path.isdir(f"{VIDEOS_FOLDER}/id{i}"):
			updateleast(i-1)
			return (i-1)
	return -1
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
			updateleast(i-1)
			break
		else:
			result = re.search('TITLE:(.*)\n', meta)
			title = result.group(1)
			onHover = title
			if len(title) > 28:
				title = title[:25] + "..." # 25 is 3 less than 28 and "..." is three chars

			src = "/static/videos/id"+str(i)+"/thumbnail.png"
			alt = f"Video ID${i} thumbnail"
			height = 256
			width = height+32
			# <img src="" alt="" width="5%" height="5%">
			html += f'<div class="vidItem" title="{onHover}"><a href="play?id={i}"><img src={src} alt="{alt}" width="{width}" height="{height}">{title}</a></div>'
		i += 1
	return render_template("index.html", videos=Markup(html), title2="Press Ctrl+F to search for vid.")


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload")
def upload_form(disabled = True):
	#if disabled: return err("The upload feature is temporarily disabled.")
	return render_template('upload.html')
@app.route("/upload//bypass")
def up_bypass():
	return upload_form(False)

@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			return err('No file part')
		if 'thumb' not in request.files:
			return err('No thumbnail part')
		file = request.files['file']
		thumb = request.files['thumb']
		if file.filename == '':
			return err("No file selected for uploading")
		if thumb.filename == '':
			return err("No thumbnail selected for uploading")
		if file and allowed_file(file.filename):
			filename = secure_filename("main_vid.mp4")
			fname_thumb = secure_filename("thumbnail.png")
			UPLOAD_FOLDER = f"{VIDEOS_FOLDER}/id{(getLastId()+1)}"
			mkdir(UPLOAD_FOLDER)
			file.save(os.path.join(f'{UPLOAD_FOLDER}/', filename))
			thumb.save(os.path.join(f'{UPLOAD_FOLDER}/', fname_thumb))
			title = request.form["title"]
			desc = request.form["desc"]
			usr = request.form["user"]
			if usr.strip() == "": usr = "None"
			if desc.strip() == "": desc = "None"
			if title.strip() == "": title = "Untitled"

			metaFile = f"""TITLE:{title}
DESCRIPTION:{desc}
DATE:{str(datetime.now().date())}
USER:{usr}
"""
			writeToFile(f"{UPLOAD_FOLDER}/meta.txt", metaFile)
			#writeToFile(f"{UPLOAD_FOLDER}/thumbnail.png", getFile(f"{VIDEOS_FOLDER}/id0/thumbnail.png"))
			return redirect('/')
		else:
			return err('Allowed file types are: '+str(ALLOWED_EXTENSIONS))
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
	upr = ""
	usr = ""
	try:
		upr = re.search('DATE:(.*)\n', meta).group(1)
	except:
		upr = "None"
	try:
		usr = re.search('USER:(.*)\n', meta).group(1)
	except:
		usr = "None"
	info += """<p>
		Uploaded: {}</p>
		<p>Uploader: {}</p>"""
	info = info.format(upr, usr)
	del upr
	del usr

	# OG Vid size was w320 h240
	html = f"""<div id="playback" class="center"><video width="640" height="480" controls>
<source src="/static/videos/{id}/main_vid.mp4" type="video/mp4">
Your browser does not support the video tag.
</video><br><h3>Description:</h3><p>{vidDesc}</p>{info}</div>"""#
	return render_template("index.html", videos=Markup(html), id=id, title2=vidTitle) # note to self: IDK if id var is used ever
if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, port=80)
#app.run(host='0.0.0.0', debug=True, port=80)

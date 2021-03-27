import os
from flask import Flask, flash, request, redirect, render_template, send_from_directory, make_response
import json
from pdfrw import PdfReader, PdfWriter
from pathlib import Path

app = Flask(
  __name__,
  template_folder='public',
  static_folder='public'
)

db = {}

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TESTING'] = True
app.config['SECRET_KEY'] = "def3e2eaf341ecd4194a30f74adba1e8a30a0c6e6d3d859a"
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def append_data(name, data):
  global db
  set_data(name, {**db[name], **data})

# data = dict
def set_data(name, data):
  global db
  db[name] = data
  with open("data.json", "w+") as f:
    json.dump(db, f)

def read_data():
  if Path("data.json").exists():
    with open("data.json", "r") as f:
      d = json.load(f)
  else:
    d = {}
  return d

@app.route('/download/<folder>', methods=['POST'])
def download_file(folder):
  global db
  folder = request.form.get("folder")
  if folder == "":
    flash("No folder specified")
    return redirect(request.url)
  if not (folder in db.keys()):
    flash("Folder doesn't exist")
    return redirect(request.url)
  data = db[folder]
  files_fn = folder+".pdf"
  files = PdfWriter(compress=True)
  folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
  res = ""
  for i in sorted(data):
    res += i
    filename = data[i]["filename"]
    path = os.path.join(folder_path, filename)
    f = PdfReader(path)
    r = data[i]["range"]
    files.addpages(f.pages[r[0]-1:r[1]])
  files.write(os.path.join(folder_path, files_fn))
  return send_from_directory(directory=folder_path, filename=files_fn, as_attachment=True, mimetype='application/pdf')

@app.route('/download', methods=['GET'])
def download_page():
  global db
  return render_template('download.html', isEmpty=(len(db.keys())==0), folders=db.keys())

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  global db
  if request.method == "POST":
    folder = request.form.get("folder")
    if folder == "custom":
      folder = request.form.get("folder-custom", "")
      if folder == '':
        flash('No folder specified')
        return redirect(request.url)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)
    if not (file and allowed_file(file.filename)):
      flash('Invalid file')
      return redirect(request.url)
    isExist = folder in db.keys()
    if isExist:
      filename = str(len(db[folder])) + ".pdf"
    else:
      filename = "0.pdf"
    form = list(request.form.to_dict().values())
    data = {}
    cnt = 1
    for i in range(2, len(form), 2):
      if form[i] == "" or not form[i+1].isnumeric() or not form[i][1:].isnumeric():
        flash('Invalid pageset format')
        return redirect(request.url)
      name = form[i].upper()
      name = name[0] + str(int(name[1:])).zfill(3)
      num = int(form[i+1])
      data[name] = {
        "range": (cnt, cnt+num-1),
        "filename": filename
      }
      cnt += num
    if cnt == 1:
      flash('Invalid pageset format')
      return redirect(request.url)
    path = os.path.join(*(f"{app.config['UPLOAD_FOLDER']},{folder},{filename}".split(",")))
    Path(os.path.join(app.config['UPLOAD_FOLDER'], folder)).mkdir(parents=True, exist_ok=True)
    file.save(path)
    try:
      f = PdfReader(path)
      print(len(f.pages))
      for p in data:
        f.pages[data[p]["range"][1]-1]
    except:
      flash('Error when parsing PDF or invalid pageset')
      os.remove(path)
      return redirect(request.url)
    if folder in db.keys():
      append_data(folder, data)
    else:
      set_data(folder, data)
    print(db[folder])
    flash('Berhasil mengupload file!')
  return render_template('upload.html', folders=db.keys())


@app.route('/check', methods=['GET', 'POST'])
def check_pengumpulan():
  global db
  data = None
  folder = ""
  if request.method == "POST":
    folder = request.form.get("folder")
    if folder == "":
      flash("No folder specified")
      return redirect(request.url)
    if not (folder in db.keys()):
      flash("Folder doesn't exist")
      return redirect(request.url)
    data = db[folder]
    print(data)
  return render_template('check.html', isEmpty=(len(db.keys())==0), folders=db.keys(), folder_data=data, folder_name=folder)

if __name__ == "__main__":
  db = read_data()
  app.run(host='0.0.0.0', port=8080)

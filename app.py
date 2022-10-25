import proc
from flask import Flask,render_template,request,jsonify
import numpy as np
import base64
import cv2

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def index():
    return render_template("index.html", title = 'Home')


@app.route('/postmethod',methods = ['POST'])
def post_data():
    imgdata = request.form["imgdata"]
    im_bytes = base64.b64decode(imgdata)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
    img = cv2.imdecode(im_arr, -1)
    data = proc.imgin(img)
    params = { "data" : data }
    return jsonify(params)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000,debug = True)

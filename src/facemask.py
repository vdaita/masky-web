import torch.backends.cudnn as cudnn

from utils import google_utils
from utils.datasets import *
from utils.utils import *

# from pathlib import Path

from imutils import build_montages
from imutils import paths
import random
import cv2

import base64

from flask import Flask
from flask import request
from flask_cors import CORS
import json

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})


def apply_cv2(input, blur=False):
    img = letterbox(input, new_shape=416)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    # print("contarray: " + str(img))

    device = "cpu"

    half = False

    model = torch.load("mask.pt", map_location=device)['model'].float()
    model.to(device).eval()
    if half:
        model.half()

    names = model.module.names if hasattr(model, 'module') else model.names

    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    t1 = torch_utils.time_synchronized()
    pred = model(img, augment=False)[0]

    # print("non-nms", pred, len(pred[0]))

    # Apply NMS
    pred = non_max_suppression(pred, 0.45, 0.5)
    t2 = torch_utils.time_synchronized()

    # print("post nms", pred)

    faces = ""
    imgs = []

    for i, det in enumerate(pred):  # detections per image

        gn = torch.tensor(img.shape)[[1, 0, 1, 0]] #normalization gain whwh
        counter = 0
        if det is not None and len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], input.shape).round()

            for *xyxy, conf, cls in det:
                label = '%s' % (names[int(cls)])
                if label == "nomask":
                    image1 = input[int(xyxy[1]):int(xyxy[3]), int(xyxy[0]):int(xyxy[2])].copy()
                    image1 = cv2.resize(image1, (200, 200))
                    if blur:
                        image1 = cv2.medianBlur(image1,15)
                    imgs.append(image1)
                    retval, buffer = cv2.imencode('.jpg', image1)
                    jpg_as_text = base64.b64encode(buffer).decode("utf-8")
                    faces += str(jpg_as_text) + ","
                    # cv2.imwrite("/Users/vijaydaita/Files/covid19/mask-detector/desktop-app/" + str(counter) + "hi" + ".jpg", image1)
                    counter += 1

    #for im in imgs:
    #   cv2.imshow("1", im)
    #    cv2.waitKey(5)
    # print(faces)
    return faces

@app.route("/detect", methods=["POST"])
def apply():
    req = request.get_json()
    req = json.loads(req['jsonData'])
    # print(req)
    im_bytes = base64.b64decode(req['img'])
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    return apply_cv2(img, req['blur'])

if __name__ == '__main__':
    app.run()
#
# image = cv2.imread("/Users/vijaydaita/Files/covid19/mask-detector/desktop-app/imgs/john-torcasio-oeGMaLjUOxQ-unsplash.jpg")
# retval, buffer = cv2.imencode('.jpg', image)
# jpg_as_text = base64.b64encode(buffer).decode("utf-8")
# print(apply(jpg_as_text))

#!/usr/bin/env python

"""Usage: python file_receiver.py

Demonstrates a server that receives a multipart-form-encoded set of files in an
HTTP POST, or streams in the raw data of a single file in an HTTP PUT.

See file_uploader.py in this directory for code that uploads files in this format.
"""

import logging

try:
    from urllib.parse import unquote
except ImportError:
    # Python 2.
    from urllib import unquote

import tornado.ioloop
import tornado.web
from tornado import options
import json
import os
import random
import string
from vertical_project_separate import hybird_separate_ex
from work_on_model import DigitalOCR

class DigitalResponseRet():
    def __init__(self):
        self.digital = ""
        self.ok = "success"
        self.reason = ""
    def to_json(self):
        ret_dict = {}
        for name,value in vars(self).items():
            ret_dict[name]=value
        return json.dumps(ret_dict)

K_UPLOAD_DIR = "./uploads"
g_ocr_obj = DigitalOCR()
class DigitalOcrHandler(tornado.web.RequestHandler):
    def check_file_type(self,file_name):
        support_type = [".jpg",".png",".bmp"]
        _,ext = os.path.splitext(os.path.basename(file_name)) 
        if ext not in support_type:
            return False
        return True
        pass

    def post(self):
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                body = info['body']
                logging.info('POST "%s" "%s" %d bytes',
                             filename, content_type, len(body))
                # only recognize one file
                self.process_ocr(filename,body)
                break
        #self.write('OK')
        pass

    def process_ocr(self,file_name,file_contents):
        # check file's type
        if not self.check_file_type(file_name):
            ret = DigitalResponseRet()
            ret.ok = "fail"
            ret.reason = "image's type is not support"
            self.write(ret.to_json())
            return
        # save file to disk
        _,ext = os.path.splitext(os.path.basename(file_name))
        random_name = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(8))
        random_name = random_name + ext
        output_file = open(K_UPLOAD_DIR+ "/" +random_name, 'wb')
        output_file.write(file_contents)
        # separate image to image object
        im_path = K_UPLOAD_DIR + "/" + random_name
        im_lists = hybird_separate_ex(im_path)
        #logging.info(im_lists)
        digital_str = ""
        for item in im_lists:
            tmp = g_ocr_obj.recognize(item)
            digital_str += tmp

        ret = DigitalResponseRet()
        ret.digital = digital_str
        self.write(ret.to_json())


def make_app():
    return tornado.web.Application([
        (r"/digital_ocr", DigitalOcrHandler),
    ])


if __name__ == "__main__":
    # Tornado configures logging.
    options.parse_command_line()
    app = make_app()
    app.listen(8888,"192.168.174.129")
    tornado.ioloop.IOLoop.current().start()

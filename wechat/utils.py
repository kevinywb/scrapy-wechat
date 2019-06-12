# -*- coding: utf-8 -*-

# Define your utils function here
import urllib
import io
from PIL import Image
import base64


class WechatUtils(object):
    def get_base64img_from_url(self, url, max_length=800):
        try:
            # get image from url
            origin_file = io.BytesIO(urllib.request.urlopen(url).read())
            img = Image.open(origin_file)
            # define maximum size
            w, h = img.size
            larger_side = max(w, h)
            if larger_side > max_length:
                img = img.resize((int(float(max_length) * w / larger_side),
                                  int(float(max_length) * h / larger_side)), Image.ANTIALIAS)
            # load image in memory
            jpeg_image_buffer = io.BytesIO()
            img.save(jpeg_image_buffer, format="JPEG")
            # convert to base64 string
            return base64.b64encode(jpeg_image_buffer.getvalue())
        except Exception as e:
            print(e)
            return ''

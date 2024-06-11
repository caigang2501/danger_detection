import cv2
import requests
import numpy as np
from hikvisionapi import Client

client = Client('http://10.83.37.30', 'admin', 'zhgd4009')

response = client.Streaming.channels[1].picture(method='get', type='opaque_data')

print(type(response),response)



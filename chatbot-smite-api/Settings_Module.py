import os
import codecs
import json

class MySettings(object):
	def __init__(self, settings_file=None):
		try:
			with codecs.open(settings_file, encoding="utf-8-sig", mode="r") as f:
				saved_settings = json.load(f, encoding="utf-8")
			self.reload(saved_settings)
		except:
			self.DevId = ''
			self.AuthKey = ''

	def reload(self, json_data):
		self.DevId = json_data['DevId']
		self.AuthKey = json_data['AuthKey']
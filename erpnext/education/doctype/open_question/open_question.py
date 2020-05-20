# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
 
class OpenQuestion(Document):
	
# TODO:Implement evaluation service for instructor or auto evaluation for attempted and personal..
	def evaluate(self, response, quiz_name):
		try:
			if response is not None and reponse != "":
				is_correct = True
				result = 100
			else:
				is_correct = False
				result = 0
		except Exception as e:
			is_correct = False
			result = 0

		score = result
		if score >= 50:
			status = "Pass"
		else:
			status = "Fail"
		return result, score, status

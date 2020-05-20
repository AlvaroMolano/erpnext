
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class OpenQuiz(Document):
	def validate(self):
		if self.passing_score > 100:
			frappe.throw(_("Passing Score value should be between 0 and 100"))

	def allowed_attempt(self, enrollment, quiz_name):
		if self.max_attempts ==  0:
			return True

		try:
			if len(frappe.get_all("Open Quiz Activity", {'enrollment': enrollment.name, 'quiz': quiz_name})) >= self.max_attempts:
				frappe.msgprint(_("Maximum attempts for this quiz reached!"))
				return False
			else:
				return True
		except Exception as e:
			return False


	def get_questions(self):
		return [frappe.get_doc('Open Question', question.question_link) for question in self.question]

	def compare_list_elementwise(*args):
		try:
			if all(len(args[0]) == len(_arg) for _arg in args[1:]):
				return all(all([element in (item) for element in args[0]]) for item in args[1:])
			else:
				return False
		except TypeError:
			frappe.throw(_("Compare List function takes on list arguments"))


# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.education.utils import get_or_create_course_enrollment, get_current_student, has_super_access
from frappe.model.document import Document
import frappe
from frappe import _

class OpenAnswer(Document):
	def get_context():
		pass
		
def get_answers(answer_email, reference_doctype, reference_name):
	doc = frappe.get_list("Open Answer",filters={'answer_email':answer_email, 'reference_name':reference_name})
	return doc

@frappe.whitelist(allow_guest=False)
def add_answer(answer, answer_email, answer_by, reference_doctype, reference_name, answer_type, route, params, parent_name, parent_doctype, course, program):

	if answer_email != frappe.session.user:
		frappe.msgprint(_('Please check your profile, and fill the gaps'))
		return 'User did not match error'

	_route = route + params
	doc_answer = None
	is_new = False
	if not frappe.db.exists('Open Answer', {'parent': reference_name, 'owner':answer_email}):
		doc_answer =  frappe.get_doc({'doctype':'Open Answer'})
		is_new = True
	else:
		doc_answer = frappe.get_doc('Open Answer', {'parent': reference_name, 'owner':answer_email})

	doc_answer.answer_by = answer_by
	doc_answer.answer_email = answer_email
	doc_answer.answer = answer
	doc_answer.reference_doctype = reference_doctype
	doc_answer.reference_name = reference_name
	doc_answer.parent = reference_name
	doc_answer.answer_type = answer_type
	doc_answer.parentfield = 'open_answer'
	doc_answer.parenttype = reference_doctype
	doc_answer.route = _route



	if is_new:
		doc_answer.insert(ignore_permissions=True)
	else:
		doc_answer.save(ignore_permissions=True)

	evaluate_open_question(doc_answer, parent_name, reference_name, course, program)

	## Get the existing open question from inside document
	# question.open_answer.append(answer)
	# question.save(ignore_permissions=True)
	# frappe.db.commit()

	# since answers are embedded in the page, clear the web cache
	if route:
		frappe.clear_cache(route)

	return 'OK'

@frappe.whitelist()
def evaluate_open_question(doc_answer, parent_name, question_name, course, program):
	student = get_current_student()
	open_question = frappe.get_doc("Open Question", question_name)
	open_quiz = frappe.get_doc("Open Quiz", parent_name)
	result, score, status = open_question.evaluate(doc_answer, parent_name)

	#if has_super_access():
	#	return {'result': result, 'score': score, 'status': status}

	if student:
		enrollment = get_or_create_course_enrollment(course, program)
		if open_quiz.allowed_attempt(enrollment, parent_name):
			enrollment.add_open_quiz_activity(open_question, open_quiz, doc_answer, result, score, status)
			return {'result': result, 'score': score, 'status': status}
		else:
			return None

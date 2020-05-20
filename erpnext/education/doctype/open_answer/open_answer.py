# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.education.utils import get_or_create_course_enrollment, get_current_student, has_super_access
from frappe.model.document import Document
import frappe
from frappe import _

class OpenAnswer(Document):
	pass

def get_context(context):
	# context.answers = get_answers(frappe.sesion.user)
	print(frappe.sesion)
	print('context open answers ******************* context open answers ******************* context **')

def get_answers(answer_email, reference_doctype, reference_name):
	doc = frappe.get_list("Open Answer",filters={'answer_email':answer_email, 'reference_name':reference_name})
	return doc

@frappe.whitelist(allow_guest=False)
def add_answer(answer, answer_email, answer_by, reference_doctype, reference_name, answer_type, route, params, parent_name, parent_doctype):
	if answer_email != frappe.session.user:
		frappe.msgprint(_('Please check your profile, and fill the gaps'))
		return 'User did not match error'

	# if len(answer) < 10:
	# 	frappe.msgprint(_('answer Should be atleast 10 characters'))
	# 	return 'field validation error'

	_route = route + params
	# get the open question
	# question = frappe.get_doc(reference_doctype, reference_name)

	# create an open answer
	# try:
	doc_answer = None
	is_new = False
	if not frappe.db.exists('Open Answer', {'parent': reference_name, 'owner':answer_email}):
		doc_answer =  frappe.get_doc({'doctype':'Open Answer'})
		is_new = True
	else:
		doc_answer = frappe.get_doc('Open Answer', {'parent': reference_name, 'owner':answer_email})
		print('is not new')


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

	## Get the existing open question from inside document
	# question.open_answer.append(answer)
	# question.save(ignore_permissions=True)
	# frappe.db.commit()

	# since answers are embedded in the page, clear the web cache
	if route:
		frappe.clear_cache(route)

	# except Exception:
	# 	frappe.db.rollback()
	# 	frappe.log_error(frappe.get_traceback())

	# content = (doc_answer.content
	# 	+ "<p><a href='{0}/desk/#Form/answer/{1}' style='font-size: 80%'>{2}</a></p>".format(frappe.utils.get_request_site_address(),
	# 		doc_answer.name, _("View answer")))

	# notify creator
	# frappe.sendmail(
	# 	recipients = frappe.db.get_value('User', doc.owner, 'email') or doc.owner,
	# 	subject = _('New answer on {0}: {1}').format(doc.doctype, doc.name),
	# 	message = content,
	# 	reference_doctype=doc.doctype,
	# 	reference_name=doc.name
	# )

	# if doc_answer.published:
	# 	# revert with template if all clear (no backlinks)
	# 	template = frappe.get_template("templates/includes/answers/doc_answer.html")

	# 	return template.render({"answer": doc_answer.as_dict()})

	# else:
	# 	return ''
	return 'OK'

@frappe.whitelist()
def evaluate_open_quiz(quiz_response, quiz_name, course, program):
	import json

	student = get_current_student()

	quiz_response = json.loads(quiz_response)
	quiz = frappe.get_doc("Open Quiz", quiz_name)
	result, score, status = quiz.evaluate(quiz_response, quiz_name)

	if has_super_access():
		return {'result': result, 'score': score, 'status': status}

	if student:
		enrollment = get_or_create_course_enrollment(course, program)
		if quiz.allowed_attempt(enrollment, quiz_name):
			enrollment.add_open_quiz_activity(quiz_name, quiz_response, result, score, status)
			return {'result': result, 'score': score, 'status': status}
		else:
			return None

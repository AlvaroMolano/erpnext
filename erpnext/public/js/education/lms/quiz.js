class Quiz {
	constructor(wrapper, options) {
		this.wrapper = wrapper;
		Object.assign(this, options);
		this.questions = []
		this.refresh();
	}

	refresh() {
		this.get_quiz();
	}

	get_quiz() {
		frappe.call('erpnext.education.utils.get_quiz_results', {
			quiz_name: this.name,
			course: this.course
		}).then(res => {
			this.make(res.message)
		});
	}

	make(data) {
		let is_complete = (data.activity && data.activity.is_complete) ? true : false
		data.questions.forEach(question_data => {
			
			let question_wrapper = document.createElement('div');
			let question = new Question({
				wrapper: question_wrapper, is_complete:is_complete,
				...question_data
			});
			this.questions.push(question)
			this.wrapper.appendChild(question_wrapper);
		})

		if (is_complete) {
			this.disable()
			let indicator = 'red'
			//TODO: add translation: __('Your are not allowed to attempt the quiz again.')
			let message = 'No puedes volver a rellenar este cuestioanario'
			if (data.activity.result == 'Pass') {
				indicator = 'green'
				//TODO: add translation: 'You have already cleared the quiz.'
				message = 'Tu ya has rellenado este cuestionario'
			}
			this.set_quiz_footer(message, indicator, data.activity.score)
		}
		else {
			this.make_actions();
		}
	}

	make_actions() {
		const button = document.createElement("button");
		button.classList.add("btn", "btn-primary", "mt-5", "mr-2");

		button.id = 'submit-button';
		// TODO: add translation submit
		button.innerText = 'Enviar';
		button.onclick = () => this.submit();
		this.submit_btn = button
		this.wrapper.appendChild(button);
	}
	message
	submit() {
		//TODO: Add translation: 'Evaluating..'
		this.submit_btn.innerText = 'Evaluando..'
		this.submit_btn.disabled = true
		this.disable()
		frappe.call('erpnext.education.utils.evaluate_quiz', {
			quiz_name: this.name,
			quiz_response: this.get_selected(),
			course: this.course,
			program: this.program
		}).then(res => {
			this.submit_btn.remove()
			if (!res.message) {
				//TODO: add translation: "Something went wrong while evaluating the quiz."
				frappe.throw("Algo ha ido mal al evaluar el cuestionario")
			}

			let indicator = 'red'
			// TODO: add translation Fail
			let message = 'Suspendido'
			if (res.message.status == 'Pass') {
				indicator = 'green'
				//TODO: add translation : Congratulations, you cleared the quiz
				message = 'Felicidades, completaste el cuestionario.'
			}

			this.set_quiz_footer(message, indicator, res.message.score)
		});
	}

	set_quiz_footer(message, indicator, score) {
		const div = document.createElement("div");
		div.classList.add("mt-5");
		div.innerHTML = `<div class="row">
							<div class="col-md-8">
								<h4>${message}</h4>
								<h5 class="text-muted"><span class="indicator ${indicator}">Score: ${score}/100</span></h5>
							</div>
							<div class="col-md-4">
								<a href="${this.next_url}" class="btn btn-primary pull-right">${this.quiz_exit_button}</a>
							</div>
						</div>`

		this.wrapper.appendChild(div)
	}
	

	get_selected() {
		let que = {}
		this.questions.forEach(question => {
			que[question.name] = question.get_selected()
		})
		return que
	}
}

class Question {
	constructor(opts) {
		Object.assign(this, opts);
		this.make();
	}
	
	make() {
		this.make_question()
		this.make_options()
	}
	is_multiple() {
		return this.type == 'Multiple Correct Answer';
	}
	get_selected() {
		let selected = this.options.filter(opt => opt.input.checked)
		if (this.type == 'Single Correct Answer') {
			if (selected[0]) return selected[0].name
		}
		if (this.type == 'Multiple Correct Answer') {
			return selected.map(opt => opt.name)
		}
		return null
	}

	disable() {
		let selected = this.options.forEach(opt => opt.input.disabled = true)
	}

	make_question() {
		let question_wrapper = document.createElement('h5');
		question_wrapper.classList.add('mt-3');
		question_wrapper.innerText = this.question;
		this.wrapper.appendChild(question_wrapper);
	}

	make_options() {

		let make_input = (name, value, marked, answer) => {
						let input = document.createElement('input');
			input.id = name;
			input.name = this.name;
			input.value = value;
			input.type = 'radio';

			if (is_multiple()){
				input.type = 'checkbox';
			}
			if (marked) {
				input.checked = true;
				if(answer && answer == 'WRONG'){
					input.indeterminate = true;
				}
			}
			input.classList.add('form-check-input');
			return input;
		}

		let make_label = function (name, value, marked, answer) {
			let label = document.createElement('label');
			label.classList.add('form-check-label');
			
			if (marked && answer){
				if(answer == 'WRONG'){
					label.classList.add('text-warning')
				} else if (answer == 'OK'){
					label.classList.add('text-success')	
				}
			}
			label.htmlFor = name;
			label.innerText = value;
			return label
		}

		let is_multiple = function(){
			return this.type == 'Multiple Correct Answer';
		}

		let make_option = function (wrapper, option, result, is_multiple) {
			
			let marked_option = false;
			let selected_option = false;
			let answer = undefined;
			let quiz_result = undefined;
			function isCorrect(_iterator){
				quiz_result = result.quiz_result;
				marked_option = (String(_iterator).trim().includes(String(option.option).trim())) ? true : false
				
				if (marked_option == true ){
					if(quiz_result == 'Correct'){
						answer='OK'
					}else{
						answer='WRONG'
					}
				}
			}
			if (result && result.selected_option){
				selected_option = is_multiple ? result.selected_option.split(',') : result.selected_option
				
				if (is_multiple){
					for (const iterator of selected_option) {
						isCorrect(iterator)
						}
				} else {
					isCorrect(selected_option)
				}
			}

			let option_div = document.createElement('div')
			option_div.classList.add('form-check', 'pb-1')
			

			let input = make_input(option.name, option.option, marked_option, answer);
			let label = make_label(option.name, option.option, marked_option, answer);
			option_div.appendChild(input)
			option_div.appendChild(label)
			wrapper.appendChild(option_div)
			return { input: input, ...option }
		}

		let options_wrapper = document.createElement('div')
		options_wrapper.classList.add('ml-2')
		let option_list = []
		let result = (this._result && this._result) ? this._result : null
		this.options.forEach(opt => option_list.push(make_option(options_wrapper, opt, result, this.is_multiple())))
		this.options = option_list
		this.wrapper.appendChild(options_wrapper)

	}
}

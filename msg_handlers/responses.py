responses = {
    'setup': {
        'greet': 'Hi {}, thank you for using Schej! Schej will help you schedule you life and classes! Please enter your email so that we can send you a calendar.',
        'city': 'Which city so you live in? (We need to find your timezone for your calendar)',
        'reenter_email': [':(','That doesn\'t look like an email to me.', 'Please enter your email again.'],
        'timezone_error': ['Sorry, we couldn\'t find that city\'s timezone.', 'Please try again.'],
        'done': ['Woohoo!!!', 'Your calendar has been created. Please check your email for the invite. :)'],
        'start': 'To get started, lets add a term. What is the term name?',
    },
    'help': ['Here are the commands you can use:',  'To add an item, say \'add <item>\'. You can add a term, subject, class, homework, exam, activity and meeting'],
    'cancel': {
        'insult': ['👿','Do you talk to your mother with that mouth??'],
        'try_again': 'No problem, try again!',
        'exit': 'Cancelling action.'    
    },
    'email': {
        'invalid': '{} does not seem like a valid email. Please try again.',
    },
    'term': {
        'name': 'What is the term name?',
        'no_term': 'There are no terms, please add a term first.',
        'start': 'When does the term start?',
        'end': 'When does the term end?',
        'invalid_date': 'That is an invalid date, please try again.',
        'success': 'Term added! 😄',
        'post': 'Do you want to add a subject?',
        'error': 'Term could not be added.'
    },
    'subject': {
        'what': 'What is the subject?',
        'term': 'What term is the subject in?',
        'success': 'Subject added! 😄',
        'post': 'Do you want to add a class?',
        'no_subject': 'No subjects found. Please add a subject to add a class.',
    },
    'class': {
        'link': 'Please create the class by clicking the link:',
        'add': 'Add a Class',
        'verify': 'Is this ok:\n\nsubject: {} \nmodule: {} \nstart time: {} \nend time: {}\ndays: {}\nlocation: {}',
        'success': 'Class added! 😊',
        'post': 'Do you want to add another class?'
    },
    'task': {
        'link': 'Please create the task by clicking the link:',
        'add': 'Add a Task',
        'verify': 'Is this ok:\n\ntask: {}\nsubject: {}\ndue date: {} {}\ntime left: {}',
        'success': 'Task added! I will remind you to complete the task hehehe.',
        'post': ''
    },
    'notification': {
        'single_event': 'Hi, you have {} at {}.',
        'multiple_events': 'Hi, you have a few events coming up: {}.'
    },
    'error': {
        'general': [':(', 'Oops! Something went wrong.'],
        'not_Implemented': 'Option to update coming soon!'
    },
    'report': {
        'pre': ['I am extremely sorry :(', 'What is the issue?'],
        'success': ['Thank you very much for reporting the issue!', 'I will try my best to fix this asap!'],
        'error': 'Whoops! There is an issue with reporting issues. 🙃',  
    },
    'emoji': {
        'sad': ':('
    }
    
}
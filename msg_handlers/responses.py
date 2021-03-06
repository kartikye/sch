import pendulum

def print_human_date(date):
    
    num_days = pendulum.now(date.timezone).diff(date).in_days()
    
    if num_days < 7:
        return date.format('%A')
    else:
        return date.format('%-d%t of %B')
    

responses = {
    'setup': {
        'greet': 'Hi {}, thank you for using Schej! Schej will help you schedule you life and classes! Please enter your email so that we can send you a calendar.',
        'city': ['Great','Which city so you live in? (We need to find your timezone for your calendar)'],
        'reenter_email': [':(','That doesn\'t look like an email to me.', 'Please enter your email again.'],
        'timezone_error': ['Sorry, we couldn\'t find that city\'s timezone.', 'Please try again.'],
        'done': ['Woohoo!!!', 'Your calendar has been created. Please check your email for the invite. :)'],
        'start': 'To get started, lets add a term. What is the term name?',
    },
    'help': ['Here are the commands you can use:',  'To add an item, say \'add <item>\'. You can add a term, subject, class and task (coming soon: exam, activity and meeting)', 'To report an issue, say \'report an issue\''],
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
        'not_found': 'Sorry that subject was not found.'
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
        'post': '',
        'no_task': 'No tasks found.',
        'tasks_due': 'The following tasks are due:',
        'task_due': '{}: {} is due on {} ({}min left)',
        'which_task': 'Which task would you like to complete?'
    },
    'notification': {
        'single_event': 'Hi, you have {} at {}.',
        'multiple_events': 'Hi, you have a few events coming up: {}.'
    },
    'error': {
        'general': [':(', 'Oops! Something went wrong.'],
        'not_Implemented': 'This feature is in the works!',
        'do_not_understand': 'Sorry, I don\'t understand what you are asking for.'
    },
    'report': {
        'pre': ['I am extremely sorry :(', 'What is the issue?'],
        'success': ['Thank you very much for reporting the issue!', 'I will try my best to fix this asap!'],
        'error': 'Whoops! There is an issue with reporting issues. 🙃',  
    },
    'request_feature': {
        'pre': 'What features would you like to see?',
        'success': 'Yay, the feature has been requested.',
        'error': 'Whoops! There was an issue :('
    },
    'emoji': {
        'sad': ':('
    },
    'print_human_date': print_human_date
}


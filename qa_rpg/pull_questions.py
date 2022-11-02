import sys
import os

sys.path.insert(0, 'path') # Django setting file path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()

from django.contrib.auth.models import User
from qa_rpg.models import Question, Choice

import random
import urllib.request, json
import html

CATEGORY = ''
DAMAGE = 20
OPENTDB_API = "" # Trivia API URL

all_question = json.load(urllib.request.urlopen(OPENTDB_API))
print(all_question)

admin = User.objects.get(pk=2) # Admin User

for question in all_question['results']:
    question_text = html.unescape(question['question'])
    question_model = Question.objects.create(question_text=question_text,
                                             damage=DAMAGE,
                                             category=CATEGORY,
                                             owner=admin)
    question_model.save()

    choices = question['incorrect_answers']
    choices.append(question['correct_answer'])
    for _ in range(4):
        choice = random.choice(choices)
        choices.remove(choice)
        correct = (choice == question['correct_answer'])
        choice_model = Choice.objects.create(choice_text=html.unescape(choice),
                                             correct_answer=correct,
                                             question=question_model)
        choice_model.save()






from django.contrib import admin
from .models import Question, Choice, Player

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Question detail', {'fields': ['damage', 'currency'],
                              }),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'damage', 'currency',
                    'owner', 'enable', 'report', 'commend', 'correct_choice')
    list_filter = ['owner', 'enable', 'damage', 'currency', 'report', 'commend']
    search_fields = ['question_text', 'owner']


admin.site.register(Question, QuestionAdmin)
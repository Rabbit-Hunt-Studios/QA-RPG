from django.contrib import admin
from .models import Question, Choice, Player

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Question detail', {'fields': ['damage', 'currency',
                                        'category', 'owner'],}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'damage', 'currency',
                    'owner', 'category', 'enable', 'correct_choice')
    list_filter = ['owner', 'enable', 'damage', 'currency',
                   'category']
    search_fields = ['question_text', 'owner']


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Player Info', {'fields': ['player_name', 'user',
                                    'max_hp', 'currency', 'luck']}),
        ('Action', {'fields': ['activity']}),
    ]
    readonly_fields = ('player_name', 'user', 'max_hp',
                       'currency', 'luck')
    list_display = ('player_name', 'user', 'max_hp',
                    'currency', 'luck', 'activity')
    list_filter = ['max_hp', 'currency', 'activity']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Player, PlayerAdmin)
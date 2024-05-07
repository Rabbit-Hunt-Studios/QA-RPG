from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Question, Choice, Player, Log, Inventory, ReportAndCommend


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'id')
    readonly_fields = ('id',)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Question detail', {'fields': ['damage', 'currency',
                                        'category', 'owner', 'enable'],}),
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
                                    'max_hp', 'currency', 'luck', 'awake']}),
        ('Action', {'fields': ['activity']}),
    ]
    readonly_fields = ('player_name', 'user', 'luck')
    list_display = ('player_name', 'user', 'max_hp',
                    'currency', 'luck', 'activity')
    list_filter = ['max_hp', 'currency', 'activity']


class LogAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Text Log Info', {'fields': ['log_text', 'player']}),
        ('Question Log Info', {'fields': ['log_questions', 'log_report_question']})
    ]
    readonly_fields = ('player',)
    list_display = ('player',)
    list_filter = ['player']


class InventoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Inventory Info', {'fields': ['player', 'player_inventory',
                                       'dungeon_inventory', 'max_inventory']}),
        ('Template Info', {'fields': ['question_template']})
    ]
    readonly_fields = ('player',)
    list_display = ('player', 'max_inventory')
    list_filter = ['player', 'max_inventory']


class ReportCommendAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Report and Commend Info', {'fields': ['question', 'user', 'vote']}),
    ]
    readonly_fields = ('question', 'user', 'vote')
    list_display = ('question', 'user', 'vote')
    list_filter = ['question', 'user', 'vote']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(ReportAndCommend, ReportCommendAdmin)

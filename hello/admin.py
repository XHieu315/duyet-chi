from django.contrib import admin
from .models import ExpenseRequest


@admin.register(ExpenseRequest)
class ExpenseRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'expense_type', 'status', 'created_at')
    list_filter = ('status', 'expense_type', 'employee')
    search_fields = ('employee__username', 'reason')

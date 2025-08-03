from django.contrib import admin

from .forms import CashFlowStatementForm
from .models import CashFlowStatement, Category, Status, Subcategory, Type


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    """Админ-класс для модели типа операции"""

    list_display = ("id", "name", "user")
    search_fields = ("name",)
    fields = ("name", "user")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    """Админ-класс для модели статуса операции"""

    list_display = ("id", "name", "user")
    search_fields = ("name",)
    fields = ("name", "user")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-класс для модели категории"""

    list_display = ("id", "name", "type", "user")
    list_filter = ("type", "user")
    search_fields = ("name",)
    fields = ("name", "user", "type")


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Админ-класс для модели подкатегории"""

    list_display = ("id", "name", "category", "user")
    list_filter = ("category", "user")
    search_fields = ("name",)
    fields = ("name", "user", "category")


@admin.register(CashFlowStatement)
class CashFlowStatementAdmin(admin.ModelAdmin):
    """Админ-класс для модели записи ДДС"""

    form = CashFlowStatementForm

    list_display = (
        "custom_date",
        "amount",
        "type",
        "category",
        "subcategory",
        "status",
        "user",
    )
    list_filter = ("type", "category", "subcategory", "status", "user")
    search_fields = ("comment",)
    date_hierarchy = "custom_date"
    readonly_fields = ("created_at",)

    def get_fields(self, request, obj=None):
        # Если объект только создаётся, реальная дата создания не показывается, она заполнится автоматически
        if obj is None:
            return (
                "user",
                "custom_date",
                "amount",
                "type",
                "category",
                "subcategory",
                "status",
                "comment",
            )
        # Если редактируется, показываем, она будет доступна только для чтения
        else:
            return (
                "user",
                "custom_date",
                "created_at",
                "amount",
                "type",
                "category",
                "subcategory",
                "status",
                "comment",
            )

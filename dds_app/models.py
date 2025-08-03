from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Type(models.Model):
    """Модель типа операции"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="types",
        verbose_name="Пользователь",
    )
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        unique_together = ("user", "name")
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операции"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Status(models.Model):
    """Модель статуса"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="statuses",
        verbose_name="Пользователь",
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        unique_together = ("user", "name")
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Пользователь",
    )
    name = models.CharField(max_length=100, verbose_name="Название")
    type = models.ForeignKey(
        Type, on_delete=models.CASCADE, related_name="categories", verbose_name="Тип"
    )

    class Meta:
        unique_together = ("name", "type", "user")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Модель категории"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Пользователь",
    )
    name = models.CharField(max_length=100, verbose_name="Название")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Категория",
    )

    class Meta:
        unique_together = ("name", "category", "user")
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class CashFlowStatement(models.Model):
    """Модель записи о движении денежных средств"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="statements",
        verbose_name="Пользователь",
    )
    created_at = models.DateField(
        auto_now_add=True, verbose_name="Реальная дата создания"
    )  # Реальное время создания записи
    custom_date = models.DateField(
        blank=True, null=True, verbose_name="Пользовательское время создания"
    )  # Пользовательское временная метка записи
    type = models.ForeignKey(Type, on_delete=models.PROTECT, verbose_name="Тип")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        Subcategory, models.PROTECT, verbose_name="Подкатегория"
    )
    status = models.ForeignKey(Status, models.PROTECT, verbose_name="Статус")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ("-custom_date",)

    # Заполним кастомное поле при создании записим текущей датой
    def save(self, *args, **kwargs):
        if not self.custom_date:
            self.custom_date = timezone.now().date()
        super().save(*args, **kwargs)

    def clean(self):
        # Проверка соответсвия категории и подкатегории
        if self.subcategory and self.subcategory.category != self.category:
            raise ValidationError(
                "Выбранная подкатегория не принадлежит указанной категории"
            )
        # Проверка соответсвия категории и типа
        if self.category and self.category.type != self.type:
            raise ValidationError("Выбранная категория не принадлежит указанному типу")

    def __str__(self):
        return f"Дата создания операции: {self.custom_date} | Тип: {self.type} | Категория: {self.category} | Подкатегория: {self.subcategory} | Сумма: {self.amount} ₽"

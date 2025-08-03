from dal import autocomplete
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)

from .forms import (CashFlowStatementFilterForm, CashFlowStatementForm,
                    get_reference_form)
from .models import CashFlowStatement, Category, Subcategory


class ReferenceDeleteView(LoginRequiredMixin, DeleteView):
    """Универсальное представление удаления справочника"""

    template_name = "dds_app/ref_delete.html"
    context_object_name = "ref"

    def get_queryset(self):
        model = apps.get_model("dds_app", self.kwargs["model"])
        return model.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("reference-list", kwargs={"model": self.kwargs["model"]})

    def get_context_data(self, **kwargs):
        # Передаём имя модели для отображения
        context = super().get_context_data(**kwargs)
        context["model"] = self.kwargs["model"]
        context["model_verbose"] = apps.get_model(
            "dds_app", self.kwargs["model"]
        )._meta.verbose_name
        return context


class ReferenceUpdateView(LoginRequiredMixin, UpdateView):
    """Универсальное представление редактирования справочника"""

    template_name = "dds_app/ref_form.html"

    def get_form_class(self):
        return get_reference_form(self.kwargs["model"])

    def get_object(self, queryset=None):
        model = apps.get_model("dds_app", self.kwargs["model"])
        return get_object_or_404(model, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Безопасно подаём user в форму
        kwargs["initial"] = kwargs.get("initial", {})
        kwargs["initial"]["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        # Передаём имя модели для отображения
        context = super().get_context_data(**kwargs)
        context["model"] = self.kwargs["model"]
        context["model_verbose"] = apps.get_model(
            "dds_app", self.kwargs["model"]
        )._meta.verbose_name
        return context

    def get_success_url(self):
        return reverse_lazy("reference-list", kwargs={"model": self.kwargs["model"]})


class ReferenceCreateView(LoginRequiredMixin, CreateView):
    """Универсальное представление создания справочника"""

    template_name = "dds_app/ref_form.html"

    def form_valid(self, form):
        # Вручную установим пользователя
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_class(self):
        return get_reference_form(self.kwargs["model"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Безопасно подаём user в форму
        kwargs["initial"] = kwargs.get("initial", {})
        kwargs["initial"]["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        # Передаём имя модели для отображения
        context = super().get_context_data(**kwargs)
        context["model"] = self.kwargs["model"]
        context["model_verbose"] = apps.get_model(
            "dds_app", self.kwargs["model"]
        )._meta.verbose_name
        return context

    def get_success_url(self):
        return reverse_lazy("reference-list", kwargs={"model": self.kwargs["model"]})


class ReferenceListView(LoginRequiredMixin, ListView):
    """Отображение любой из модели справочников"""

    template_name = "dds_app/ref_list.html"
    context_object_name = "ref_list"

    def get_queryset(self):
        model = apps.get_model("dds_app", self.kwargs["model"])
        return model.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Передаём имя модели для отображения
        context = super().get_context_data(**kwargs)
        model = apps.get_model("dds_app", self.kwargs["model"])
        context["model"] = self.kwargs["model"]
        context["model_verbose"] = apps.get_model(
            "dds_app", self.kwargs["model"]
        )._meta.verbose_name_plural
        # Убираем лишние поля в отображении
        context["fields"] = [
            field
            for field in model._meta.fields
            if field.name != "user" and field.name != "id"
        ]
        return context


class ReferencesView(LoginRequiredMixin, TemplateView):
    """Навигационная страничка справочников"""

    template_name = "dds_app/references.html"


class DeleteCashFlowStatementView(LoginRequiredMixin, DeleteView):
    """Удаление ДДС-записи"""

    model = CashFlowStatement
    template_name = "dds_app/delete_dds.html"
    success_url = reverse_lazy("dds-list")
    context_object_name = "entry"


class UpdateCashFlowStatementView(LoginRequiredMixin, UpdateView):
    """Редактирование ДДС-записи"""

    model = CashFlowStatement
    form_class = CashFlowStatementForm
    template_name = "dds_app/update_dds.html"
    success_url = reverse_lazy("dds-list")


class CreateCashFlowStatementView(LoginRequiredMixin, CreateView):
    """Создание ДДС-записи"""

    model = CashFlowStatement
    form_class = CashFlowStatementForm
    template_name = "dds_app/create_dds.html"
    success_url = reverse_lazy("dds-list")

    def form_valid(self, form):
        # Вручную установим пользователя
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передаём user для формы
        kwargs["user"] = self.request.user
        return kwargs


class CashFlowStatementFilterReset(LoginRequiredMixin, View):
    """Сброс фильтров"""

    def get(self, request):
        # Очищаем сессию и редерикс на главную
        self.request.session["dds_filter"] = {}
        return redirect("dds-list")


class CashFlowStatementFilterListView(LoginRequiredMixin, ListView):
    """Отображение списка ДДС-записей с фильтрацией"""

    model = CashFlowStatement
    template_name = "dds_app/dds_list.html"
    context_object_name = "dds_list"
    paginate_by = 10  # По умолчанию

    def get_paginate_by(self, queryset):
        # Считываем пользовательское количество записей на странице
        try:
            per_page = int(self.request.GET.get("per_page", self.paginate_by))
            return max(per_page, 1)  # Минимум 1
        except ValueError:
            return self.paginate_by

    def get_queryset(self):
        user = self.request.user
        qs = (
            CashFlowStatement.objects.filter(user=user)
            .select_related("status", "category", "type", "subcategory")
            .order_by("-custom_date")
        )

        # Получим данные фильтрации -> они будут из запроса или из сессии -> или пустой словарь
        data = self.request.GET or self.request.session.get("dds_filter", {})

        # Получаем из формы данные для фильтрации
        form = CashFlowStatementFilterForm(data=data, user=user)
        if form.is_valid():
            custom_date_from = form.cleaned_data.get("custom_date_from")
            custom_date_to = form.cleaned_data.get("custom_date_to")
            type = form.cleaned_data.get("type")
            category = form.cleaned_data.get("category")
            subcategory = form.cleaned_data.get("subcategory")
            status = form.cleaned_data.get("status")
            amount_min = form.cleaned_data.get("amount_min")
            amount_max = form.cleaned_data.get("amount_max")
            comment = form.cleaned_data.get("comment")

            # Фильтруем поля
            if custom_date_from:
                qs = qs.filter(custom_date__gte=custom_date_from)
            if custom_date_to:
                qs = qs.filter(custom_date__lte=custom_date_to)
            if type:
                qs = qs.filter(type=type)
            if category:
                qs = qs.filter(category=category)
            if subcategory:
                qs = qs.filter(subcategory=subcategory)
            if status:
                qs = qs.filter(status=status)
            if amount_min:
                qs = qs.filter(amount__gte=amount_min)
            if amount_max:
                qs = qs.filter(amount__lte=amount_max)
            if comment:
                qs = qs.filter(comment__icontains=comment)

            # Сохраняем фильтры в сессию
            self.request.session["dds_filter"] = self.request.GET.dict()

        self.filter_form = form
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передадим в шаблон фильтрационную форму или создадим новую пустую
        context["filter_form"] = getattr(
            self, "filter_form", CashFlowStatementFilterForm(user=self.request.user)
        )
        return context


# Фильтрует список подкатегорий в зависимости от категории
class SubcategoryAutocomplete(autocomplete.Select2QuerySetView):
    """Динамическая подгрузка подкатегорий"""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Subcategory.objects.none()

        qs = Subcategory.objects.filter(user=self.request.user)
        category_id = self.forwarded.get("category", None)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


# Фильтрует список категорий в зависимости от типа
class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    """Динамическая подгрузка категорий"""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Category.objects.none()

        qs = Category.objects.filter(user=self.request.user)
        type_id = self.forwarded.get("type", None)
        if type_id:
            qs = qs.filter(type_id=type_id)
        return qs


class RegisterView(CreateView):
    """Кастомный класс регистрации"""

    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

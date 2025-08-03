from dal import autocomplete
from django import forms

from .models import CashFlowStatement, Category, Status, Subcategory, Type


def get_reference_form(model_name):
    """Функция динамической сборки формы с нужно моделью"""
    models_map = {
        "type": Type,
        "category": Category,
        "subcategory": Subcategory,
        "status": Status,
    }
    model_class = models_map[model_name]

    class ReferenceForm(forms.ModelForm):
        """Динамическая форма для справочников"""

        class Meta:
            model = model_class
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Фильтруем связанные объекты
            user = self.initial.get("user") or kwargs.get("initial", {}).get("user")
            if model_class == Category and "type" in self.fields:
                self.fields["type"].queryset = Type.objects.filter(user=user)
            if model_class == Subcategory and "category" in self.fields:
                self.fields["category"].queryset = Category.objects.filter(user=user)

            # Пользователь задаётся в представлении
            if "user" in self.fields:
                self.fields.pop("user")

            # Динамически задаём класс
            for field in self.fields.values():
                field.widget.attrs.update({"class": "form-gold"})

    return ReferenceForm


class CashFlowStatementFilterForm(forms.Form):
    """Форма для фильтрации записей ДДС"""

    custom_date_from = forms.DateField(
        required=False,
        label="Дата от",
        widget=forms.DateInput(
            attrs={"type": "date", "placeholder": "ДД.ММ.ГГГГ", "class": "form-gold"}
        ),
    )
    custom_date_to = forms.DateField(
        required=False,
        label="Дата до",
        widget=forms.DateInput(
            attrs={"type": "date", "placeholder": "ДД.ММ.ГГГГ", "class": "form-gold"}
        ),
    )
    type = forms.ModelChoiceField(
        queryset=Type.objects.all(),
        required=False,
        label="Тип",
        widget=forms.Select(attrs={"class": "form-gold"}),
    )
    category = forms.ModelChoiceField(
        label="Категория",
        queryset=Category.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(
            url="category-autocomplete",
            forward=["type"],
            attrs={
                "data-theme": "bootstrap5",
                "data-placeholder": "--------",
                "class": "form-gold",
            },
        ),
    )
    subcategory = forms.ModelChoiceField(
        label="Подкатегория",
        queryset=Subcategory.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(
            url="subcategory-autocomplete",
            forward=["category"],
            attrs={
                "data-theme": "bootstrap5",
                "data-placeholder": "--------",
                "class": "form-gold",
            },
        ),
    )
    status = forms.ModelChoiceField(
        queryset=Status.objects.none(),
        required=False,
        label="Статус",
        widget=forms.Select(attrs={"class": "form-gold"}),
    )
    amount_min = forms.DecimalField(
        required=False,
        label="Сумма от",
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-gold", "type": "number", "placeholder": "$$$$$"}
        ),
    )
    amount_max = forms.DecimalField(
        required=False,
        label="Сумма до",
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-gold", "type": "number", "placeholder": "$$$$$"}
        ),
    )
    comment = forms.CharField(
        required=False,
        label="Комментарий содержит",
        widget=forms.TextInput(attrs={"class": "form-gold", "placeholder": "..."}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # После создания полей отфильтруем некоторые их них по пользователю
        if user is not None:
            self.fields["type"].queryset = Type.objects.filter(user=user)
            self.fields["category"].queryset = Category.objects.filter(user=user)
            self.fields["subcategory"].queryset = Subcategory.objects.filter(user=user)
            self.fields["status"].queryset = Status.objects.filter(user=user)


class CashFlowStatementForm(forms.ModelForm):
    """Форма для создания новой ДДС записи"""

    custom_date = forms.DateField(
        required=False,
        label="Дата",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-gold"}),
    )
    category = forms.ModelChoiceField(
        label="Категория",
        queryset=Category.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="category-autocomplete",
            forward=["type"],
            attrs={
                "data-theme": "bootstrap5",
                "data-placeholder": "--------",
                "class": "form-gold",
            },
        ),
    )
    subcategory = forms.ModelChoiceField(
        label="Подкатегория",
        queryset=Subcategory.objects.all(),
        widget=autocomplete.ModelSelect2(
            url="subcategory-autocomplete",
            forward=["category"],
            attrs={
                "data-theme": "bootstrap5",
                "data-placeholder": "--------",
                "class": "form-gold",
            },
        ),
    )
    type = forms.ModelChoiceField(
        queryset=Type.objects.all(),
        label="Тип",
        widget=forms.Select(attrs={"class": "form-gold"}),
    )
    status = forms.ModelChoiceField(
        queryset=Status.objects.none(),
        label="Статус",
        widget=forms.Select(attrs={"class": "form-gold"}),
    )
    amount = forms.DecimalField(
        label="Сумма",
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-gold", "type": "number", "placeholder": "$$$$$"}
        ),
    )
    comment = forms.CharField(
        required=False,
        label="Комментарий",
        widget=forms.TextInput(attrs={"class": "form-gold", "placeholder": "..."}),
    )

    class Meta:
        model = CashFlowStatement
        fields = [
            "custom_date",
            "status",
            "type",
            "category",
            "subcategory",
            "amount",
            "comment",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["type"].queryset = Type.objects.filter(user=user)
            self.fields["category"].queryset = Category.objects.filter(user=user)
            self.fields["subcategory"].queryset = Subcategory.objects.filter(user=user)
            self.fields["status"].queryset = Status.objects.filter(user=user)

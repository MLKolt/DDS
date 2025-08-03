from django.urls import path

from .views import (CashFlowStatementFilterListView,
                    CashFlowStatementFilterReset, CategoryAutocomplete,
                    CreateCashFlowStatementView, DeleteCashFlowStatementView,
                    ReferenceCreateView, ReferenceDeleteView,
                    ReferenceListView, ReferencesView, ReferenceUpdateView,
                    SubcategoryAutocomplete, UpdateCashFlowStatementView)

urlpatterns = [
    path(
        "category-autocomplete/",
        CategoryAutocomplete.as_view(),
        name="category-autocomplete",
    ),
    path(
        "subcategory-autocomplete/",
        SubcategoryAutocomplete.as_view(),
        name="subcategory-autocomplete",
    ),
    path("", CashFlowStatementFilterListView.as_view(), name="dds-list"),
    path(
        "reset-filters/", CashFlowStatementFilterReset.as_view(), name="reset-filters"
    ),
    path("create-dds/", CreateCashFlowStatementView.as_view(), name="create-dds"),
    path(
        "update-dds/<int:pk>/", UpdateCashFlowStatementView.as_view(), name="update-dds"
    ),
    path(
        "delete-dds/<int:pk>/", DeleteCashFlowStatementView.as_view(), name="delete-dds"
    ),
    path("references/", ReferencesView.as_view(), name="references"),
    path("reference/<str:model>", ReferenceListView.as_view(), name="reference-list"),
    path(
        "reference/<str:model>/create",
        ReferenceCreateView.as_view(),
        name="reference-create",
    ),
    path(
        "reference/<str:model>/<int:pk>/update",
        ReferenceUpdateView.as_view(),
        name="reference-update",
    ),
    path(
        "reference/<str:model>/<int:pk>/delete",
        ReferenceDeleteView.as_view(),
        name="reference-delete",
    ),
]

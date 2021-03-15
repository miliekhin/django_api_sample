from django.urls import path
from goods.views import *

urlpatterns = [
    path('products/', ProductsView.as_view()),
    path('products/<int:id>/', ProductsByIdView.as_view()),
    path('products/<str:name>/', ProductsByNameView.as_view()),
    path('categories/', CategoriesView.as_view()),
    path('categories/<int:id>/', CategoriesByIdView.as_view()),
]

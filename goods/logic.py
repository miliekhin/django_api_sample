from .models import *
from django.forms.models import model_to_dict
from django.http import QueryDict


def product_categories(product: Product) -> list:
    """Перегоняем все категории в словарь"""
    categories_list = []
    for c in product.category.all():
        categories_list.append(model_to_dict(c))
    return categories_list


def product_as_dict(product: Product) -> dict:
    """Товар конвертируем в словарь"""
    product_dict = model_to_dict(product)
    product_dict['category'] = product_categories(product)
    return product_dict


def all_goods() -> list:
    """Все товары конвертируем в список словарей"""
    all_products = Product.objects.all()
    resp = []
    for p in all_products:
        resp.append(product_as_dict(p))
    return resp


def get_filters(request_params: map) -> map:
    """Сборка фильтра из параметров запроса"""
    filters = {}
    if 'name' in request_params:
        filters['name__icontains'] = request_params['name']
    if 'category_id' in request_params:
        filters['category__id__in'] = request_params['category_id'].split(',')
    if 'category_name' in request_params:
        filters['category__name__icontains'] = request_params['category_name']
    if 'price' in request_params:
        filters['price__range'] = request_params['price'].split(',')
    if 'is_published' in request_params:
        filters['is_published'] = bool(int(request_params['is_published']))
    if 'is_deleted' in request_params:
        filters['is_deleted'] = bool(int(request_params['is_deleted']))
    return filters


def check_category_list_length(category_list: list) -> None:
    """Проверка количества категорий для товара"""
    cll = len(category_list)
    if cll < 2 or cll > 10:
        raise ValueError('Only 2 to 10 categories allowed.')


def create_product(request_data: map) -> Product:
    """Создание товара"""
    category_list = request_data.getlist('category')
    check_category_list_length(category_list)
    product = Product.objects.create(name=request_data['name'], price=request_data['price'])

    for category_name in category_list:
        category, is_created = Category.objects.get_or_create(name=category_name)
        product.category.add(category)
    return product


def edit_product(request_params: QueryDict, product_id: int) -> Product:
    """Редактирование товара"""
    params = {}
    if 'name' in request_params:
        params['name'] = request_params['name']
    if 'price' in request_params:
        params['price'] = request_params['price']
    if 'is_published' in request_params:
        params['is_published'] = bool(int(request_params['is_published']))
    if 'is_deleted' in request_params:
        params['is_deleted'] = bool(int(request_params['is_deleted']))

    Product.objects.filter(pk=product_id).update(**params)
    product = Product.objects.get(pk=product_id)
    if 'category_id' in request_params:
        category_list = request_params.getlist('category_id')
        check_category_list_length(category_list)
        product.category.through.objects.filter(product_id=product_id).delete()
        product.category.add(*Category.objects.filter(pk__in=category_list))

    return product
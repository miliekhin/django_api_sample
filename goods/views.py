from django.http import JsonResponse
from .models import *
from .logic import *
from django.views import View
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict


@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(View):
    """
    Отдача списка всех товаров с фильтрацией по имени поля в параметрах запроса.
    Создание товара.
    """
    def get(self, request):
        response = []
        if not request.GET:
            response = all_goods()
        else:
            try:
                for p in Product.objects.filter(**get_filters(request.GET)):
                    response.append(product_as_dict(p))
            except Exception as exc:
                return JsonResponse({'error': str(exc)}, status=400)

        return JsonResponse(response, status=200, safe=False)

    def post(self, request):
        try:
            product = create_product(request.POST)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(product_as_dict(product), status=201, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ProductsByIdView(View):
    """Отдача товара по его id, редактирование, удаление. """
    def get(self, request, id):
        try:
            p = Product.objects.get(pk=id)
        except ObjectDoesNotExist as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(product_as_dict(p), status=200, safe=False)

    def put(self, request, id):
        try:
            product = edit_product(QueryDict(request.body), id)
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(product_as_dict(product), status=200, safe=False)

    def delete(self, request, id):
        try:
            Product.objects.filter(pk=id).update(is_deleted=True)
        except ObjectDoesNotExist as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse({}, status=200)


class ProductsByNameView(View):
    """Отдача списка всех товаров по совпадению с именем"""
    def get(self, request, name):
        resp = []
        for p in Product.objects.filter(name__iexact=name):
            resp.append(product_as_dict(p))
        return JsonResponse(resp, status=200, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(View):
    """Отдача списка всех категорий и создание категории"""
    def get(self, request):
        all_categories = Category.objects.all()
        resp = []
        for c in all_categories:
            resp.append(model_to_dict(c))

        return JsonResponse(resp, status=200, safe=False)

    def post(self, request):
        try:
            new_category, is_created = Category.objects.get_or_create(name=request.POST['name'])
        except Exception as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        return JsonResponse(model_to_dict(new_category), status=201, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesByIdView(View):
    """Отдача и удаление категории по id"""
    def get(self, request, id):
        try:
            c = Category.objects.get(pk=id)
        except ModuleNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        return JsonResponse(model_to_dict(c), status=200, safe=False)

    def delete(self, request, id):
        try:
            c = Category.objects.get(pk=id)
            if not Product.objects.filter(category__pk=c.pk).exists():
                c.delete()
            else:
                return JsonResponse({'error': 'Unable to delete category. It has a relations.'}, status=400)

        except ObjectDoesNotExist as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse({}, status=200)

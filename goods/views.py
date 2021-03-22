from django.http import JsonResponse
from .models import *
from .logic import *
from django.views import View
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict


class ViewsExceptionsHandler(View):
    """ Глобальный обработчик исключений """
    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception as e:
            return self._response({'error': str(e)}, status=400)

        if isinstance(response, (dict, list)):
            return self._response(response)
        else:
            return response

    @staticmethod
    def _response(data, *, status=200):
        return JsonResponse(
            data,
            status=status,
            safe=not isinstance(data, list),
            json_dumps_params={'ensure_ascii': False}
        )


@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(ViewsExceptionsHandler):
    """
    Отдача списка всех товаров с фильтрацией по имени поля в параметрах запроса.
    Создание товара.
    """
    def get(self, request):
        response = []
        if not request.GET:  # Если нет параметров в запросе
            response = all_goods()
        else:
            for p in Product.objects.filter(**get_filters(request.GET)):
                response.append(product_as_dict(p))

        return JsonResponse(response, status=200, safe=False)

    def post(self, request):
        product = create_product(request.POST)
        return JsonResponse(product_as_dict(product), status=201, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class ProductsByIdView(ViewsExceptionsHandler):
    """Отдача товара по его id, редактирование, удаление. """
    def get(self, request, id):
        p = Product.objects.get(pk=id)
        return JsonResponse(product_as_dict(p), status=200, safe=False)

    def put(self, request, id):
        product = edit_product(QueryDict(request.body), id)
        return JsonResponse(product_as_dict(product), status=200, safe=False)

    def delete(self, request, id):
        Product.objects.filter(pk=id).update(is_deleted=True)
        return JsonResponse({}, status=200)


class ProductsByNameView(ViewsExceptionsHandler):
    """Отдача списка всех товаров по совпадению с именем"""
    def get(self, request, name):
        resp = []
        for p in Product.objects.filter(name__iexact=name):
            resp.append(product_as_dict(p))
        return JsonResponse(resp, status=200, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesView(ViewsExceptionsHandler):
    """Отдача списка всех категорий и создание категории"""
    def get(self, request):
        all_categories = Category.objects.all()
        resp = []
        for c in all_categories:
            resp.append(model_to_dict(c))

        return JsonResponse(resp, status=200, safe=False)

    def post(self, request):
        new_category, is_created = Category.objects.get_or_create(name=request.POST['name'])
        return JsonResponse(model_to_dict(new_category), status=201, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CategoriesByIdView(ViewsExceptionsHandler):
    """Отдача и удаление категории по id"""
    def get(self, request, id):
        c = Category.objects.get(pk=id)
        return JsonResponse(model_to_dict(c), status=200, safe=False)

    def delete(self, request, id):
        c = Category.objects.get(pk=id)
        if not Product.objects.filter(category__pk=c.pk).exists():
            c.delete()
        else:
            return JsonResponse({'error': 'Unable to delete category. It has a relations.'}, status=400)
        return JsonResponse({}, status=200)

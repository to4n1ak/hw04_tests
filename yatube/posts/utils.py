from django.core.paginator import Paginator


def page_num(request, objects, pages: int):
    paginator = Paginator(objects, pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

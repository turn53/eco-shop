from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Category, Product
import re


class ProductListView(ListView):
    """Список всех товаров"""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images')

        # Фильтр по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Поиск с нормализацией (игнорируем регистр, дефисы, множественные пробелы)
        search_query = self.request.GET.get('q')
        if search_query:
            # Нормализуем поисковый запрос: заменяем дефисы на пробелы, убираем множественные пробелы
            normalized_query = re.sub(r'[-_/\\]', ' ', search_query)
            normalized_query = re.sub(r'\s+', ' ', normalized_query).strip()

            # Разбиваем на отдельные слова для более гибкого поиска
            words = normalized_query.split()

            # Создаем фильтры для каждого слова
            q_filter = Q()
            for word in words:
                if len(word) > 1:  # Игнорируем слишком короткие слова
                    q_filter &= (
                        Q(name__icontains=word) |
                        Q(description__icontains=word) |
                        Q(material__icontains=word) |
                        Q(short_description__icontains=word)
                    )

            if q_filter:
                queryset = queryset.filter(q_filter)

        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_available=True).select_related('category').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Похожие товары
        from recommendations.utils import get_similar_products, get_frequently_bought_together
        context['similar_products'] = get_similar_products(product, limit=4)
        context['bought_together'] = get_frequently_bought_together(product, limit=4)

        # Отзывы
        context['reviews'] = product.reviews.filter(is_approved=True).select_related('user')[:5]

        return context


class CategoryDetailView(DetailView):
    """Список товаров категории"""
    model = Category
    template_name = 'shop/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context['products'] = Product.objects.filter(
            category=category,
            is_available=True
        ).prefetch_related('images')
        return context


def product_detail(request, slug):
    """Функция-представление для детальной страницы товара"""
    product = get_object_or_404(Product, slug=slug, is_available=True)

    # Похожие товары
    from recommendations.utils import get_similar_products, get_frequently_bought_together
    similar_products = get_similar_products(product, limit=4)
    bought_together = get_frequently_bought_together(product, limit=4)

    # Отзывы
    reviews = product.reviews.filter(is_approved=True).select_related('user')[:5]

    context = {
        'product': product,
        'similar_products': similar_products,
        'bought_together': bought_together,
        'reviews': reviews,
    }
    return render(request, 'shop/product_detail.html', context)


def about(request):
    """Страница О компании"""
    return render(request, 'pages/about.html')


def contact(request):
    """Страница Контакты"""
    return render(request, 'pages/contact.html')

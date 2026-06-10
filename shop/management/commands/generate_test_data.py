from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, ProductImage
from recommendations.models import RecommendationStats
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Генерация тестовых данных для магазина'

    def handle(self, *args, **options):
        self.stdout.write('Начало генерации тестовых данных...')

        # Создать категории
        categories_data = [
            {'name': 'Эко-посуда', 'description': 'Экологичная посуда из бамбука и других натуральных материалов'},
            {'name': 'Эко-косметика', 'description': 'Натуральная косметика без вредных химикатов'},
            {'name': 'Эко-текстиль', 'description': 'Одежда и текстиль из органических материалов'},
            {'name': 'Товары для дома', 'description': 'Экологичные товары для дома'},
            {'name': 'Аксессуары', 'description': 'Эко-аксессуары и мелочи'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'is_active': True}
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {category.name}'))

        # Создать товары с изображениями
        products_data = [
            # Эко-посуда (категория 0)
            {'name': 'Бамбуковая тарелка', 'category': 0, 'price': 450, 'material': 'Бамбук',
             'description': 'Экологичная тарелка из бамбукового волокна. Прочная, легкая и безопасная для здоровья.',
             'short_description': 'Экологичная тарелка из бамбука',
             'image_url': 'https://plus.unsplash.com/premium_photo-1736505437580-7d2dfc89994e?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'
             },
            {'name': 'Набор бамбуковых столовых приборов', 'category': 0, 'price': 890, 'material': 'Бамбук',
             'description': 'Полный набор столовых приборов из натурального бамбука. Включает вилку, нож, ложку и палочки для еды.',
             'short_description': 'Полный набор столовых приборов',
             'image_url': 'https://plus.unsplash.com/premium_photo-1664007654191-75992ed6627b?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Эко-кружка из бамбука', 'category': 0, 'price': 650, 'material': 'Бамбук',
             'description': 'Многоразовая кружка для напитков с крышкой. Идеальна для кофе на ходу.',
             'short_description': 'Многоразовая кружка для напитков',
             'image_url': 'https://plus.unsplash.com/premium_photo-1661341463079-ade00961385a?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Набор бамбуковых мисок', 'category': 0, 'price': 1250, 'material': 'Бамбук',
             'description': 'Комплект из 4 мисок разного размера из натурального бамбука. Подходят для салатов и супов.',
             'short_description': 'Комплект из 4 бамбуковых мисок',
             'image_url': 'https://plus.unsplash.com/premium_photo-1736505437580-7d2dfc89994e?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковая разделочная доска', 'category': 0, 'price': 780, 'material': 'Бамбук',
             'description': 'Прочная разделочная доска из цельного бамбука с желобком для сока.',
             'short_description': 'Разделочная доска из бамбука',
             'image_url': 'https://plus.unsplash.com/premium_photo-1667506422352-32aec976293a?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Набор соломинок из бамбука', 'category': 0, 'price': 320, 'material': 'Бамбук',
             'description': 'Многоразовые соломинки для напитков. В наборе 6 шт и щеточка для чистки.',
             'short_description': 'Многоразовые бамбуковые соломинки',
             'image_url': 'https://plus.unsplash.com/premium_photo-1673242573251-636883bf9ef7?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Ланч-бокс из бамбука', 'category': 0, 'price': 950, 'material': 'Бамбук',
             'description': 'Контейнер для еды с двумя отделениями. Герметичная крышка.',
             'short_description': 'Контейнер для еды из бамбука',
             'image_url': 'https://plus.unsplash.com/premium_photo-1669137055808-6534e6cb8d60?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковая подставка под горячее', 'category': 0, 'price': 280, 'material': 'Бамбук',
             'description': 'Термостойкая подставка для горячих блюд и напитков.',
             'short_description': 'Подставка под горячее',
             'image_url': 'https://plus.unsplash.com/premium_photo-1675183556347-02f4377edd5f?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            # Эко-косметика (категория 1)
            {'name': 'Натуральное мыло ручной работы', 'category': 1, 'price': 290, 'material': 'Натуральные масла',
             'description': 'Органическое мыло без SLS и парабенов. Подходит для чувствительной кожи.',
             'short_description': 'Органическое мыло ручной работы',
             'image_url': 'https://plus.unsplash.com/premium_photo-1677776519079-184fdc8f5c6d?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковая зубная щетка', 'category': 1, 'price': 180, 'material': 'Бамбук',
             'description': 'Биоразлагаемая зубная щетка с мягкой щетиной. Упаковка из переработанного картона.',
             'short_description': 'Биоразлагаемая зубная щетка',
             'image_url': 'https://plus.unsplash.com/premium_photo-1679750867594-6dbd6a8ad203?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Органический шампунь', 'category': 1, 'price': 520, 'material': 'Натуральные компоненты',
             'description': 'Шампунь без парабенов и сульфатов. С эфирными маслами лаванды и розмарина.',
             'short_description': 'Шампунь без парабенов',
             'image_url': 'https://plus.unsplash.com/premium_photo-1681154819686-43fcc4dc4df3?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Твердый кондиционер для волос', 'category': 1, 'price': 450, 'material': 'Натуральные масла',
             'description': 'Экономичный твердый кондиционер без пластиковой упаковки.',
             'short_description': 'Твердый кондиционер',
             'image_url': 'https://plus.unsplash.com/premium_photo-1679046948871-f90da6e2c2bb?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Набор многоразовых ватных дисков', 'category': 1, 'price': 380, 'material': 'Органический хлопок',
             'description': 'Комплект из 10 многоразовых дисков для снятия макияжа. Можно стирать.',
             'short_description': '10 многоразовых ватных дисков',
             'image_url': 'https://plus.unsplash.com/premium_photo-1664007603175-1b11f8154bde?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Дезодорант кристалл-алунит', 'category': 1, 'price': 340, 'material': 'Натуральный минерал',
             'description': 'Натуральный дезодорант без алюминия и спирта. Хватает на год использования.',
             'short_description': 'Натуральный дезодорант',
             'image_url': 'https://plus.unsplash.com/premium_photo-1661962383651-cf85d9312169?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Органическое кокосовое масло', 'category': 1, 'price': 590, 'material': 'Кокосовое масло',
             'description': 'Универсальное масло для ухода за кожей и волосами. 200 мл.',
             'short_description': 'Кокосовое масло 200 мл',
             'image_url': 'https://plus.unsplash.com/premium_photo-1661454115552-def6952a1de3?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковая щетка для тела', 'category': 1, 'price': 420, 'material': 'Бамбук',
             'description': 'Массажная щетка для сухого массажа и пилинга.',
             'short_description': 'Массажная щетка для тела',
             'image_url': 'https://plus.unsplash.com/premium_photo-1677849925689-4abcf415c5f2?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Твердый шампунь с крапивой', 'category': 1, 'price': 410, 'material': 'Натуральные компоненты',
             'description': 'Твердый шампунь для укрепления волос. Без упаковки.',
             'short_description': 'Твердый шампунь с крапивой',
             'image_url': 'https://plus.unsplash.com/premium_photo-1677776519079-184fdc8f5c6d?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            # Эко-текстиль (категория 2)
            {'name': 'Хлопковая эко-сумка', 'category': 2, 'price': 350, 'material': 'Органический хлопок',
             'description': 'Многоразовая сумка для покупок. Выдерживает до 20 кг.',
             'short_description': 'Многоразовая сумка для покупок',
             'image_url': 'https://plus.unsplash.com/premium_photo-1681324227573-953664cf9b32?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Эко-футболка из органического хлопка', 'category': 2, 'price': 1290, 'material': 'Органический хлопок',
             'description': 'Футболка из 100% органического хлопка. Без синтетических красителей.',
             'short_description': 'Футболка из органического хлопка',
             'image_url': 'https://plus.unsplash.com/premium_photo-1718913936342-eaafff98834b?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Набор сетчатых сумок для овощей', 'category': 2, 'price': 490, 'material': 'Органический хлопок',
             'description': 'Комплект из 3 сумок разного размера для покупки овощей и фруктов.',
             'short_description': '3 сетчатые сумки',
             'image_url': 'https://plus.unsplash.com/premium_photo-1664300998837-ca31b3ae46df?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Льняное полотенце', 'category': 2, 'price': 850, 'material': 'Лен',
             'description': 'Банное полотенце из 100% льна. Быстро сохнет и не впитывает запахи.',
             'short_description': 'Банное полотенце из льна',
             'image_url': 'https://plus.unsplash.com/premium_photo-1678304223927-f24dc489bdfa?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Органическое постельное белье', 'category': 2, 'price': 3500, 'material': 'Органический хлопок',
             'description': 'Комплект постельного белья из сертифицированного органического хлопка. 2-спальный.',
             'short_description': 'Постельное белье 2-спальное',
             'image_url': 'https://plus.unsplash.com/premium_photo-1701157946903-57c2821d71b7?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковые носки', 'category': 2, 'price': 420, 'material': 'Бамбуковое волокно',
             'description': 'Комплект из 3 пар носков из бамбукового волокна. Антибактериальные.',
             'short_description': '3 пары бамбуковых носков',
             'image_url': 'https://plus.unsplash.com/premium_photo-1727286320353-815a792ca2da?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            # Товары для дома (категория 3)
            {'name': 'Восковые салфетки для хранения продуктов', 'category': 3, 'price': 790, 'material': 'Хлопок, пчелиный воск',
             'description': 'Альтернатива пищевой пленке. Набор из 3 салфеток разного размера.',
             'short_description': 'Альтернатива пищевой пленке',
             'image_url': 'https://plus.unsplash.com/premium_photo-1664283229660-465903fdc87d?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковые бумажные полотенца', 'category': 3, 'price': 420, 'material': 'Бамбук',
             'description': 'Многоразовые бумажные полотенца. Можно стирать до 100 раз.',
             'short_description': 'Многоразовые бумажные полотенца',
             'image_url': 'https://plus.unsplash.com/premium_photo-1677450087617-359d6a4e6abb?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Соевые свечи ручной работы', 'category': 3, 'price': 650, 'material': 'Соевый воск',
             'description': 'Натуральные свечи с эфирными маслами. Горят до 40 часов.',
             'short_description': 'Натуральные соевые свечи',
             'image_url': 'https://plus.unsplash.com/premium_photo-1666632532494-3780d6cae861?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Джутовый коврик для ванной', 'category': 3, 'price': 1100, 'material': 'Джут',
             'description': 'Экологичный коврик из натурального джута. Быстро сохнет.',
             'short_description': 'Коврик для ванной из джута',
             'image_url': 'https://plus.unsplash.com/premium_photo-1746025617305-047aace5c902?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Набор щеток для уборки из натуральных материалов', 'category': 3, 'price': 890, 'material': 'Дерево, натуральная щетина',
             'description': 'Комплект из 3 щеток для уборки дома. Без пластика.',
             'short_description': '3 щетки для уборки',
             'image_url': 'https://plus.unsplash.com/premium_photo-1684407617001-6a20d1798917?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Эко-губки для мытья посуды', 'category': 3, 'price': 320, 'material': 'Целлюлоза, люфа',
             'description': 'Биоразлагаемые губки из натуральной целлюлозы. Набор из 5 шт.',
             'short_description': '5 биоразлагаемых губок',
             'image_url': 'https://plus.unsplash.com/premium_photo-1679064286466-6e1ee9d3a44d?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Деревянный органайзер для хранения', 'category': 3, 'price': 1450, 'material': 'Бамбук',
             'description': 'Многофункциональный органайзер с отделениями. Для офиса или кухни.',
             'short_description': 'Органайзер из бамбука',
             'image_url': 'https://plus.unsplash.com/premium_photo-1736505437580-7d2dfc89994e?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Льняные мешочки для хранения', 'category': 3, 'price': 540, 'material': 'Лен',
             'description': 'Набор из 5 мешочков разного размера для хранения круп и специй.',
             'short_description': '5 льняных мешочков',
             'image_url': 'https://plus.unsplash.com/premium_photo-1713586579932-5880a19ad51d?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            # Аксессуары (категория 4)
            {'name': 'Деревянная расческа', 'category': 4, 'price': 340, 'material': 'Дерево',
             'description': 'Расческа из натурального дерева. Антистатический эффект.',
             'short_description': 'Расческа из натурального дерева',
             'image_url': 'https://plus.unsplash.com/premium_photo-1706800175426-78c571212b15?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Эко-ручка из переработанной бумаги', 'category': 4, 'price': 120, 'material': 'Переработанная бумага',
             'description': 'Шариковая ручка из экоматериалов. Сменный стержень.',
             'short_description': 'Шариковая ручка из экоматериалов',
             'image_url': 'https://plus.unsplash.com/premium_photo-1763666810662-22490dd6c410?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковые солнцезащитные очки', 'category': 4, 'price': 1890, 'material': 'Бамбук',
             'description': 'Стильные очки с оправой из бамбука. УФ-защита 400.',
             'short_description': 'Солнцезащитные очки из бамбука',
             'image_url': 'https://plus.unsplash.com/premium_photo-1661335409388-fef29a2598a8?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Деревянные наручные часы', 'category': 4, 'price': 3500, 'material': 'Дерево',
             'description': 'Часы с корпусом и браслетом из натурального дерева. Кварцевый механизм.',
             'short_description': 'Наручные часы из дерева',
             'image_url': 'https://plus.unsplash.com/premium_photo-1728582544287-afeaee9afb3a?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Джутовый кошелек', 'category': 4, 'price': 680, 'material': 'Джут',
             'description': 'Компактный кошелек из натурального джута с застежкой.',
             'short_description': 'Кошелек из джута',
             'image_url': 'https://plus.unsplash.com/premium_photo-1672759267829-17e48ef96660?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковый чехол для телефона', 'category': 4, 'price': 750, 'material': 'Бамбук',
             'description': 'Защитный чехол из натурального бамбука. Универсальный размер.',
             'short_description': 'Чехол для телефона из бамбука',
             'image_url': 'https://plus.unsplash.com/premium_photo-1673242573251-636883bf9ef7?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Эко-блокнот из переработанной бумаги', 'category': 4, 'price': 290, 'material': 'Переработанная бумага',
             'description': 'Блокнот А5 с крафтовой обложкой. 100 листов.',
             'short_description': 'Блокнот А5 из переработанной бумаги',
             'image_url': 'https://plus.unsplash.com/premium_photo-1725294296598-1ee0cdc4aca4?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Бамбуковая бутылка для воды', 'category': 4, 'price': 890, 'material': 'Бамбук, нержавеющая сталь',
             'description': 'Термобутылка с бамбуковым корпусом. Сохраняет температуру 12 часов. 500 мл.',
             'short_description': 'Термобутылка 500 мл',
             'image_url': 'https://plus.unsplash.com/premium_photo-1664527305901-db3d4e724d15?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Набор карандашей из переработанной бумаги', 'category': 4, 'price': 240, 'material': 'Переработанная бумага',
             'description': 'Комплект из 12 цветных карандашей. Можно посадить после использования.',
             'short_description': '12 экологичных карандашей',
             'image_url': 'https://plus.unsplash.com/premium_photo-1722859318059-d3060194c690?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},

            {'name': 'Пробковый коврик для йоги', 'category': 4, 'price': 2500, 'material': 'Пробка, натуральный каучук',
             'description': 'Экологичный коврик для йоги. Антискользящий, гипоаллергенный.',
             'short_description': 'Коврик для йоги из пробки',
             'image_url': 'https://plus.unsplash.com/premium_photo-1725983651119-1c7f55c83411?ixlib=rb-4.0.3&w=600&h=600&fit=crop&q=80'},
        ]

        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': categories[prod_data['category']],
                    'price': Decimal(prod_data['price']),
                    'material': prod_data['material'],
                    'description': prod_data['description'],
                    'short_description': prod_data.get('short_description', ''),
                    'stock': random.randint(10, 100),
                    'is_available': True,
                    'manufacturer': 'ЭкоПроизводитель',
                    'country': 'Россия',
                    'eco_certificate': 'EcoCert',
                    'image_url': prod_data.get('image_url', ''),
                }
            )
            products.append(product)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан товар: {product.name}'))
                if prod_data.get('image_url'):
                    self.stdout.write(f'  Изображение URL: {prod_data["image_url"]}')

        # Создать тестового администратора
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ecoshop.ru',
                password='admin123',
                first_name='Админ',
                last_name='Админов'
            )
            self.stdout.write(self.style.SUCCESS('Создан администратор: admin / admin123'))

        # Создать тестового пользователя
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='test@ecoshop.ru',
                password='test123',
                first_name='Тест',
                last_name='Тестов'
            )
            self.stdout.write(self.style.SUCCESS('Создан тестовый пользователь: testuser / test123'))

        # Создать статистику рекомендаций (товары, которые часто покупают вместе)
        if len(products) >= 40:
            recommendation_pairs = [
                # Эко-посуда - логичные наборы
                (0, 1, 45),   # Бамбуковая тарелка + Набор приборов
                (0, 3, 38),   # Бамбуковая тарелка + Набор мисок
                (1, 4, 32),   # Набор приборов + Разделочная доска
                (2, 5, 56),   # Эко-кружка + Набор соломинок
                (2, 6, 28),   # Эко-кружка + Ланч-бокс
                (3, 4, 41),   # Набор мисок + Разделочная доска
                (3, 7, 23),   # Набор мисок + Подставка под горячее
                (6, 1, 35),   # Ланч-бокс + Набор приборов

                # Эко-косметика - уходовые наборы
                (8, 9, 67),   # Натуральное мыло + Бамбуковая зубная щетка
                (10, 11, 52), # Органический шампунь + Твердый кондиционер
                (10, 16, 29), # Органический шампунь + Твердый шампунь с крапивой
                (12, 14, 48), # Многоразовые ватные диски + Кокосовое масло
                (13, 8, 31),  # Дезодорант + Натуральное мыло
                (14, 15, 36), # Кокосовое масло + Бамбуковая щетка для тела
                (15, 31, 44), # Бамбуковая щетка для тела + Деревянная расческа

                # Эко-текстиль - комплекты
                (17, 19, 62), # Хлопковая эко-сумка + Набор сетчатых сумок
                (18, 22, 27), # Эко-футболка + Бамбуковые носки
                (20, 21, 33), # Льняное полотенце + Органическое постельное белье

                # Товары для дома - наборы для кухни и уборки
                (23, 24, 51), # Восковые салфетки + Бамбуковые бумажные полотенца
                (23, 30, 38), # Восковые салфетки + Льняные мешочки
                (27, 28, 59), # Набор щеток для уборки + Эко-губки
                (25, 26, 24), # Соевые свечи + Джутовый коврик
                (29, 30, 42), # Деревянный органайзер + Льняные мешочки

                # Аксессуары - офисные наборы и личные вещи
                (32, 37, 71), # Эко-ручка + Эко-блокнот
                (32, 38, 46), # Эко-ручка + Набор карандашей
                (33, 35, 19), # Бамбуковые солнцезащитные очки + Джутовый кошелек
                (34, 35, 22), # Деревянные наручные часы + Джутовый кошелек

                # Кросс-категорийные - спорт и активный образ жизни
                (39, 22, 37), # Пробковый коврик для йоги + Бамбуковые носки
                (39, 18, 26), # Пробковый коврик для йоги + Эко-футболка
                (2, 17, 49),  # Эко-кружка + Хлопковая эко-сумка
                (6, 17, 53),  # Ланч-бокс + Хлопковая эко-сумка

                # Подарочные наборы
                (8, 12, 41),  # Натуральное мыло + Многоразовые ватные диски
                (9, 16, 34),  # Бамбуковая зубная щетка + Твердый шампунь
                (25, 14, 28), # Соевые свечи + Кокосовое масло
                (31, 15, 39), # Деревянная расческа + Бамбуковая щетка для тела

                # Экономные наборы
                (19, 30, 47), # Набор сетчатых сумок + Льняные мешочки
                (1, 7, 33),   # Набор приборов + Подставка под горячее
                (24, 28, 43), # Бамбуковые бумажные полотенца + Эко-губки
            ]

            for idx1, idx2, frequency in recommendation_pairs:
                if idx1 < len(products) and idx2 < len(products):
                    product1 = products[idx1]
                    product2 = products[idx2]

                    # Создать запись в обе стороны (товар1->товар2 и товар2->товар1)
                    RecommendationStats.objects.get_or_create(
                        product1=product1,
                        product2=product2,
                        defaults={'frequency': frequency}
                    )
                    RecommendationStats.objects.get_or_create(
                        product1=product2,
                        product2=product1,
                        defaults={'frequency': frequency}
                    )

            self.stdout.write(self.style.SUCCESS(f'Создано {len(recommendation_pairs) * 2} связей рекомендаций'))

        self.stdout.write(self.style.SUCCESS('Генерация тестовых данных завершена!'))

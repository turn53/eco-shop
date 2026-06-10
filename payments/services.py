"""
Сервис для работы с ЮКассой (YooKassa)
"""
from django.conf import settings
from decimal import Decimal
import uuid

# Для работы с ЮКассой нужно настроить YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY в settings.py


class YooKassaService:
    """Сервис для работы с ЮКассой"""

    def __init__(self):
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.secret_key = settings.YOOKASSA_SECRET_KEY

    def create_payment(self, order, return_url=None):
        """
        Создать платеж в ЮКассе

        Args:
            order: Объект заказа
            return_url: URL для возврата после оплаты

        Returns:
            dict: Данные платежа с confirmation_url
        """
        from payments.models import Payment

        # Проверка настроек
        if not self.shop_id or not self.secret_key:
            raise ValueError(
                "ЮКасса не настроена. Укажите YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY в settings.py"
            )

        # Создать объект платежа в БД
        payment = Payment.objects.create(
            order=order,
            user=order.user,
            amount=order.total,
            currency='RUB',
            status='pending'
        )

        try:
            # Импортировать SDK ЮКассы
            from yookassa import Configuration, Payment as YooKassaPayment

            # Настроить конфигурацию
            Configuration.account_id = self.shop_id
            Configuration.secret_key = self.secret_key

            # Подготовить данные для платежа
            if return_url is None:
                return_url = settings.YOOKASSA_RETURN_URL

            payment_data = {
                "amount": {
                    "value": str(order.total),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": f"Оплата заказа №{order.order_number}",
                "metadata": {
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "payment_id": str(payment.payment_id)
                }
            }

            # Создать платеж в ЮКассе
            yookassa_payment = YooKassaPayment.create(payment_data, uuid.uuid4())

            # Обновить данные платежа
            payment.yookassa_payment_id = yookassa_payment.id
            payment.confirmation_url = yookassa_payment.confirmation.confirmation_url
            payment.status = yookassa_payment.status
            payment.metadata = {
                'yookassa_data': dict(yookassa_payment)
            }
            payment.save()

            return {
                'payment_id': payment.payment_id,
                'confirmation_url': payment.confirmation_url,
                'status': payment.status
            }

        except Exception as e:
            # В случае ошибки обновить статус платежа
            payment.status = 'failed'
            payment.metadata = {'error': str(e)}
            payment.save()
            raise

    def check_payment_status(self, payment):
        """
        Проверить статус платежа в ЮКассе

        Args:
            payment: Объект платежа из БД

        Returns:
            str: Статус платежа
        """
        if not payment.yookassa_payment_id:
            return payment.status

        try:
            from yookassa import Configuration, Payment as YooKassaPayment

            Configuration.account_id = self.shop_id
            Configuration.secret_key = self.secret_key

            # Получить информацию о платеже
            yookassa_payment = YooKassaPayment.find_one(payment.yookassa_payment_id)

            # Обновить статус
            old_status = payment.status
            payment.status = yookassa_payment.status

            # Если платеж успешен
            if yookassa_payment.status == 'succeeded' and old_status != 'succeeded':
                from django.utils import timezone
                payment.paid_at = timezone.now()

                # Обновить заказ
                order = payment.order
                order.is_paid = True
                order.paid_at = timezone.now()
                order.status = 'paid'
                order.save()

            payment.save()
            return payment.status

        except Exception as e:
            payment.metadata['check_error'] = str(e)
            payment.save()
            return payment.status

    def handle_webhook(self, notification_data):
        """
        Обработать webhook от ЮКассы

        Args:
            notification_data: Данные уведомления от ЮКассы

        Returns:
            bool: True если обработка успешна
        """
        try:
            from payments.models import Payment
            from django.utils import timezone

            # Получить ID платежа из метаданных
            yookassa_payment_id = notification_data.get('object', {}).get('id')

            if not yookassa_payment_id:
                return False

            # Найти платеж в БД
            payment = Payment.objects.filter(
                yookassa_payment_id=yookassa_payment_id
            ).first()

            if not payment:
                return False

            # Обновить статус
            new_status = notification_data.get('object', {}).get('status')
            payment.status = new_status

            # Если платеж успешен
            if new_status == 'succeeded':
                payment.paid_at = timezone.now()

                # Обновить заказ
                order = payment.order
                order.is_paid = True
                order.paid_at = timezone.now()
                order.status = 'paid'
                order.save()

            payment.save()
            return True

        except Exception:
            return False

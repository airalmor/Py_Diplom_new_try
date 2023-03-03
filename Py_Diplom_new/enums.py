from django.db import models


class Status(models.TextChoices):
    basket = "basket", "Статус корзины"
    new = "new", "Новый"
    confirmed = "confirmed", "Подтвержден"
    assembled = "assembled", "Собран"
    sent = "sent", "Отправлен"
    delivered = "delivered", "Доставлен"
    canceled = "canceled", "Отменен"


class Role(models.TextChoices):
    shop = "shop", "Магазин"
    buyer = "buyer", "Покупатель"

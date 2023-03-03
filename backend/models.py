from django.contrib.auth.models import User

from Py_Diplom_new.enums import Role, Status

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = "email"
    email = models.EmailField(_("email address"), unique=True)
    company = models.CharField(verbose_name="Компания", max_length=40, blank=True)
    position = models.CharField(verbose_name="Должность", max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    role = models.CharField(
        verbose_name="Тип пользователя",
        choices=Role.choices,
        max_length=10,
        default="buyer",
    )

    def __str__(self):
        return f"{self.email} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ("email",)


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name="Магазин")
    url = models.URLField(verbose_name="Сайт магазина", null=True, blank=True)
    filename = models.FileField(null=True, blank=True)
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    state = models.BooleanField(verbose_name="Статус получения заказов", default=True)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return f"{self.name} - {self.user}"


class Category(models.Model):
    name = models.CharField(max_length=10, verbose_name="название категории")
    shops = models.ManyToManyField(
        Shop, verbose_name="Магазины", related_name="categories", blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название продукта")
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.CASCADE,
        related_name="products",
        blank=True,
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.category}-{self.name}"


class ProductInfo(models.Model):
    model = models.CharField(
        max_length=100, verbose_name="Модель", null=True, blank=True
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name="Цена")
    price_rrc = models.PositiveIntegerField(
        verbose_name="Рекомендованная розничная цена"
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Продукт",
        related_name="products",
        on_delete=models.CASCADE,
        blank=True,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="product_infos",
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информация о продуктах"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "shop"], name="unique_product_info"
            )
        ]

    def __str__(self):
        return f"{self.shop.name}-{self.product.name}"


class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name="название параметра")

    class Meta:
        verbose_name = "Название параметра"
        verbose_name_plural = "Список названий параметров"

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="Информация о продукте",
        on_delete=models.CASCADE,
        related_name="products_info",
        blank=True,
        null=True,
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name="parameter",
        related_name="product_parameters",
        on_delete=models.CASCADE,
    )
    value = models.CharField(max_length=100, verbose_name="Значение")

    class Meta:
        verbose_name = "Параметр продукта"
        verbose_name_plural = "Параметры продукта"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "parameter"], name="unique_product_parameter"
            ),
        ]

    def __str__(self):
        return f"здесь модель - {self.parameter.name}"


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="orders",
        blank=True,
        on_delete=models.CASCADE,
    )
    contact = models.ForeignKey(
        "Contact",
        verbose_name="Контакт",
        related_name="Контакт",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15, verbose_name="Статус", choices=Status.choices
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Список заказов"

    def __str__(self):
        return f"{self.user}-{self.created_at}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        related_name="ordered_items",
        blank=True,
    )

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        on_delete=models.CASCADE,
        related_name="ordered_items",
        blank=True,
        null=True,
    )
    quantity = models.PositiveIntegerField(verbose_name=" Количество", default=1)
    price = models.PositiveIntegerField(default=0, verbose_name="Цена")
    total_amount = models.PositiveIntegerField(
        default=0, verbose_name="Общая стоимость"
    )

    class Meta:
        verbose_name = "Заказанная позиция"
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "product_info"], name="unique_order_item"
            ),
        ]

    def __str__(self):
        return f"N{self.order}-{self.product_info.model}.Кол-во: {self.quantity}.Сумма {self.total_amount}"

    def save(self, *args, **kwargs):
        self.total_amount = self.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)


# убрать null-True
class Contact(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="contacts",
        blank=True,
        on_delete=models.CASCADE,
    )

    city = models.CharField(
        max_length=50, verbose_name="Город", default="Москва", null=True
    )
    street = models.CharField(max_length=100, verbose_name="Улица", null=True)
    house = models.CharField(max_length=15, verbose_name="Дом", blank=True, null=True)
    structure = models.CharField(
        max_length=15, verbose_name="Корпус", blank=True, null=True
    )
    building = models.CharField(
        max_length=15, verbose_name="Строение", blank=True, null=True
    )
    apartment = models.CharField(
        max_length=15, verbose_name="Квартира", blank=True, null=True
    )
    phone = models.CharField(max_length=12, verbose_name="Телефон", null=True)

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f"{self.city} {self.street} {self.house}"

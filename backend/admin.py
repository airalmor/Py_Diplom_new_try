
from django.contrib import admin

from .models import Shop, Category, Product,  Parameter,ProductInfo,ProductParameter
    #  Order, OrderItem


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    list_filter = ['name','state']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = ['name', ]
    filter_vertical = ['shops', ]
# Добавить choises


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'name',]
    list_filter = ['category','name',]


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):

    list_display = ['quantity','price','product','shop']
    list_filter = ['quantity','price','product','shop']




@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):

    list_display = ['parameter','value']
    list_filter = ['parameter','value']


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     pass
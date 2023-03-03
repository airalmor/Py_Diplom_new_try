from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Product, Shop
from backend.serializers import ProductSerializer


class ProductView(APIView):
    pass


#     def get(self, request, *args,**kwargs):
#         shop = Shop.objects.create(name='Sviaznoy', state=True)
#         Product.objects.create(name='Iphone',
#                                category='phones',
#                                quantity=20,
#                                price=80000,
#                                shop_id = shop.id)
#         queryset = Product.objects.all().select_related('shop')
#         serializer = ProductSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def post(self,request, *args,**kwargs):
#         request.data
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product = serializer.save()
#             return Response(ProductSerializer(product).data)
#         else:
#             return Response(serializer.errors)

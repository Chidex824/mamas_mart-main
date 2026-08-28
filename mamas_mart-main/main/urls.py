from django.urls import path
from . import views
from graphene_django.views import GraphQLView
from .graphql_schema import schema

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/dashboard/', views.get_dashboard_updates, name='dashboard_updates'),
    path('api/stock_report/', views.stock_report_api, name='stock_report_api'),
    path('api/top_selling_products/', views.top_selling_products_api, name='top_selling_products_api'),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema), name='graphql'),
]

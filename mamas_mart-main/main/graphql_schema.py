import graphene
from graphene_django import DjangoObjectType
from datetime import datetime, timedelta
from django.utils import timezone
from products.models import Sale
from sales.models import Sale as SaleModel

class SaleType(graphene.ObjectType):
    date = graphene.String()
    total_amount = graphene.Float()
    quantity = graphene.Int()

class SalesPerformanceType(graphene.ObjectType):
    sales = graphene.List(graphene.Float)
    expenses = graphene.List(graphene.Float)
    dates = graphene.List(graphene.String)

class Query(graphene.ObjectType):
    weekly_earnings = graphene.List(SaleType)
    sales_performance = graphene.Field(SalesPerformanceType)

    def resolve_weekly_earnings(root, info):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        sales = SaleModel.objects.filter(date__gte=week_ago).order_by('date')
        result = []
        for sale in sales:
            result.append(SaleType(
                date=sale.date.strftime('%Y-%m-%d'),
                total_amount=sale.total_amount,
                quantity=sale.quantity
            ))
        return result

    def resolve_sales_performance(root, info):
        now = timezone.now()
        sales_expenses = {
            'sales': [],
            'expenses': [],
            'dates': []
        }
        for i in range(8):  # Last 8 months
            date = now - timedelta(days=30 * i)
            month_sales = SaleModel.objects.filter(
                date__year=date.year,
                date__month=date.month
            ).aggregate(total_amount_sum=graphene.Float())['total_amount_sum'] or 0

            # For simplicity, expenses are set to 0 here; implement as needed
            month_expenses = 0

            sales_expenses['sales'].insert(0, float(month_sales))
            sales_expenses['expenses'].insert(0, float(month_expenses))
            sales_expenses['dates'].insert(0, date.strftime('%b'))

        return SalesPerformanceType(
            sales=sales_expenses['sales'],
            expenses=sales_expenses['expenses'],
            dates=sales_expenses['dates']
        )

schema = graphene.Schema(query=Query)

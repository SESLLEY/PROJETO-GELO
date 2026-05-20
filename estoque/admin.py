from django.contrib import admin
from .models import Cliente, Produto, Venda


class VendaInline(admin.TabularInline):
    model = Venda
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'valor_total', 'pago', 'data')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'parceiro', 'ativo')
    inlines = [VendaInline]


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'cliente', 'quantidade', 'valor_total', 'pago', 'data')
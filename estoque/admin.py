from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from .models import Cliente, Produto, Venda, ResumoVendas


class VendaInline(admin.TabularInline):
    model = Venda
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'valor_total', 'data')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'parceiro', 'ativo')
    inlines = [VendaInline]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'ativo')


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'cliente', 'quantidade', 'valor_total', 'pago', 'data')


@admin.register(ResumoVendas)
class ResumoVendasAdmin(admin.ModelAdmin):

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):

        total_vendas = Venda.objects.count()
        vendas_pagas = Venda.objects.filter(pago=True).count()
        vendas_pendentes =
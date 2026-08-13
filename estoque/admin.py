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
        vendas_pendentes = Venda.objects.filter(pago=False).count()

        vendas_por_produto = (
            Venda.objects.values('produto__nome')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        extra_context = extra_context or {}
        extra_context.update({
            'title': 'Resumo de Vendas',
            'total_vendas': total_vendas,
            'vendas_pagas': vendas_pagas,
            'vendas_pendentes': vendas_pendentes,
            'vendas_por_produto': vendas_por_produto,
        })

        return TemplateResponse(
            request,
            "admin/estoque/resumo_vendas.html",
            extra_context,
        )
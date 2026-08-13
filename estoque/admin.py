from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from .models import Cliente, Produto, Venda, ResumoVendas
from django.db.models import Count, Sum


class VendaInline(admin.TabularInline):
    model = Venda
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'valor_total', 'data')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'parceiro', 'ativo')
    inlines = [VendaInline]
    # change_form_template = "admin/estoque/cliente/change_form.html"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        vendas = Venda.objects.filter(cliente_id=object_id)

        total_pago = vendas.filter(pago=True).aggregate(
            total=Sum('valor_total')
        )['total'] or 0

        total_prazo = vendas.filter(pago=False).aggregate(
            total=Sum('valor_total')
        )['total'] or 0

        extra_context.update({
            'total_pago': total_pago,
            'total_prazo': total_prazo,
            'saldo': total_prazo - total_pago,
        })

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

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
        vendas = Venda.objects.all()

        cliente_id = request.GET.get('cliente')
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if cliente_id:
            vendas = vendas.filter(cliente_id=cliente_id)

        if data_inicio:
            vendas = vendas.filter(data__date__gte=data_inicio)

        if data_fim:
            vendas = vendas.filter(data__date__lte=data_fim)

        total_vendas = vendas.count()
        vendas_pagas = vendas.filter(pago=True).count()
        vendas_pendentes = vendas.filter(pago=False).count()

        vendas_por_produto = (
            vendas.values('produto__nome')
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
            'clientes': Cliente.objects.all().order_by('nome'),
            'cliente_selecionado': cliente_id,
            'data_inicio': data_inicio or '',
            'data_fim': data_fim or '',
        })

        return TemplateResponse(
            request,
            "admin/estoque/resumo_vendas.html",
            extra_context,
        )
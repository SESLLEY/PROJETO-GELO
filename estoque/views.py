from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum


from .models import Cliente, Produto, Venda


# ==============================
# VENDA RÁPIDA (ENTREGADOR)
# ==============================

def venda_rapida(request):

    clientes = Cliente.objects.filter(ativo=True)

    if request.method == "POST":

        try:
            cliente_id = request.POST.get("cliente")
            cliente_avulso = request.POST.get("cliente_avulso")
            quantidade = int(request.POST.get("quantidade"))
            pago = request.POST.get("pago") == "True"

            # cliente avulso
            if cliente_avulso and cliente_avulso.strip() != "":
                cliente = Cliente.objects.create(
                    nome=cliente_avulso,
                    preco_unitario=4.00,
                    ativo=True
                )
            else:
                cliente = Cliente.objects.get(id=cliente_id)

            produto = Produto.objects.first()

            if not produto:
                messages.error(request, "Nenhum produto cadastrado.")
                return render(request, "estoque/venda_rapida.html", {
                    "clientes": clientes
                })

            preco = produto.preco
            valor_total = quantidade * preco

            Venda.objects.create(
                cliente=cliente,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco,
                valor_total=valor_total,
                pago=pago,
                data=timezone.now()
            )

            messages.success(request, "✅ Venda registrada com sucesso!")

        except Cliente.DoesNotExist:
            messages.error(request, "Cliente não encontrado.")

        except ValueError:
            messages.error(request, "Quantidade inválida.")

        except Exception as e:
            messages.error(request, f"Erro ao salvar venda: {e}")

    return render(request, "estoque/venda_rapida.html", {
        "clientes": clientes
    })


# ==============================
# PAINEL DE RESUMO DO DIA
# ==============================

def painel(request):

    hoje = timezone.now().date()

    vendas_hoje = Venda.objects.filter(data__date=hoje)

    total_sacos = vendas_hoje.aggregate(
        Sum("quantidade")
    )["quantidade__sum"] or 0

    faturamento = vendas_hoje.aggregate(
        Sum("valor_total")
    )["valor_total__sum"] or 0

    fiado = vendas_hoje.filter(
        pago=False
    ).aggregate(
        Sum("valor_total")
    )["valor_total__sum"] or 0

    total_vendas = vendas_hoje.count()

    return render(request, "estoque/painel.html", {
        "total_sacos": total_sacos,
        "faturamento": faturamento,
        "fiado": fiado,
        "total_vendas": total_vendas
    })

# ==============================
# RESUMO DE VENDAS POR CLIENTES
# ==============================

def relatorio_clientes(request):

    relatorio = (
        Venda.objects
        .values('cliente__nome')
        .annotate(
            total_sacos=Sum('quantidade'),
            total_gasto=Sum('valor_total')
        )
        .order_by('-total_sacos')
    )

    return render(request, 'estoque/relatorio_clientes.html', {
        'relatorio': relatorio
    })
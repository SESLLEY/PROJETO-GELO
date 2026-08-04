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
            # ==============================
            # RECEBER DADOS DO FORMULÁRIO
            # ==============================

            cliente_id = request.POST.get("cliente")
            cliente_avulso = request.POST.get(
                "cliente_avulso",
                ""
            ).strip()

            quantidade = int(
                request.POST.get("quantidade", 0)
            )

            pago = request.POST.get("pago") == "True"


            # ==============================
            # VALIDAR QUANTIDADE
            # ==============================

            if quantidade <= 0:

                messages.error(
                    request,
                    "Quantidade inválida."
                )

                return render(
                    request,
                    "estoque/venda_rapida.html",
                    {
                        "clientes": clientes
                    }
                )


            # ==============================
            # BUSCAR PRODUTO
            # ==============================

            produto = Produto.objects.first()

            if not produto:

                messages.error(
                    request,
                    "Nenhum produto cadastrado."
                )

                return render(
                    request,
                    "estoque/venda_rapida.html",
                    {
                        "clientes": clientes
                    }
                )


            # ==============================
            # DEFINIR CLIENTE
            # ==============================

            cliente = None


            # ==========================================
            # CASO 1 - CLIENTE AVULSO
            # ==========================================

            if cliente_avulso:

                # Cliente fica NULL
                # O nome será salvo em cliente_avulso

                cliente = None

                # Cliente avulso paga preço normal
                preco = produto.preco


            # ==========================================
            # CASO 2 - CLIENTE CADASTRADO
            # ==========================================

            elif cliente_id:

                cliente = Cliente.objects.get(
                    id=cliente_id
                )

                # Cliente parceiro
                if cliente.parceiro:

                    preco = 3.50

                # Cliente normal
                else:

                    preco = produto.preco


            # ==========================================
            # CASO 3 - NENHUM CLIENTE INFORMADO
            # ==========================================

            else:

                messages.error(
                    request,
                    "Selecione um cliente ou informe um cliente avulso."
                )

                return render(
                    request,
                    "estoque/venda_rapida.html",
                    {
                        "clientes": clientes
                    }
                )


            # ==============================
            # CALCULAR VALOR TOTAL
            # ==============================

            valor_total = quantidade * preco


            # ==============================
            # SALVAR VENDA
            # ==============================

            Venda.objects.create(

                # Cliente cadastrado
                cliente=cliente,

                # Nome do cliente avulso
                cliente_avulso=(
                    cliente_avulso
                    if cliente_avulso
                    else None
                ),

                # Produto
                produto=produto,

                # Quantidade
                quantidade=quantidade,

                # Preço aplicado
                preco_unitario=preco,

                # Total
                valor_total=valor_total,

                # Pago ou prazo
                pago=pago,

                # Data
                data=timezone.now()
            )


            # ==============================
            # MENSAGEM DE SUCESSO
            # ==============================

            messages.success(
                request,
                "✅ Venda registrada com sucesso!"
            )


        # ==============================
        # ERRO - CLIENTE NÃO ENCONTRADO
        # ==============================

        except Cliente.DoesNotExist:

            messages.error(
                request,
                "Cliente não encontrado."
            )


        # ==============================
        # ERRO - QUANTIDADE INVÁLIDA
        # ==============================

        except ValueError:

            messages.error(
                request,
                "Quantidade inválida."
            )


        # ==============================
        # OUTROS ERROS
        # ==============================

        except Exception as e:

            messages.error(
                request,
                f"Erro ao salvar venda: {e}"
            )


    # ==============================
    # ABRIR TELA DE VENDA
    # ==============================

    return render(
        request,
        "estoque/venda_rapida.html",
        {
            "clientes": clientes
        }
    )


# ==============================
# PAINEL DE RESUMO DO DIA
# ==============================

def painel(request):

    hoje = timezone.now().date()

    vendas_hoje = Venda.objects.filter(
        data__date=hoje
    )

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

    return render(
        request,
        "estoque/painel.html",
        {
            "total_sacos": total_sacos,
            "faturamento": faturamento,
            "fiado": fiado,
            "total_vendas": total_vendas
        }
    )


# ==============================
# RESUMO DE VENDAS POR CLIENTES
# ==============================

def relatorio_clientes(request):

    relatorio = (
        Venda.objects
        .values(
            "cliente__nome",
            "cliente_avulso"
        )
        .annotate(
            total_sacos=Sum("quantidade"),
            total_gasto=Sum("valor_total")
        )
        .order_by("-total_sacos")
    )

    return render(
        request,
        "estoque/relatorio_clientes.html",
        {
            "relatorio": relatorio
        }
    )
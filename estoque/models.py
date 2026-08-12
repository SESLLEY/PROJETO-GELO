from django.db import models
from django.utils import timezone


# ==========================================
# CADASTRO DE CLIENTES
# ==========================================

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    preco_unitario = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    preco_atacado = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )

    quantidade_atacado = models.IntegerField(
        default=100
    )

    ativo = models.BooleanField(
        default=True
    )

    parceiro = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.nome


# ==========================================
# CADASTRO DE PRODUTOS
# ==========================================

class Produto(models.Model):
    nome = models.CharField(
        max_length=100
    )

    preco = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    ativo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nome


# ==========================================
# CADASTRO DE VENDAS
# ==========================================

class Venda(models.Model):

    # Cliente cadastrado
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Cliente que não possui cadastro
    cliente_avulso = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # Produto vendido
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE
    )

    # Quantidade de sacos
    quantidade = models.PositiveIntegerField()

    # Preço aplicado na venda
    preco_unitario = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Valor total da venda
    valor_total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Pagamento
    pago = models.BooleanField(
        default=False
    )

    # Data da venda
    data = models.DateTimeField(
        default=timezone.now
    )

    # ==========================================
    # SALVAR VENDA
    # ==========================================

    def save(self, *args, **kwargs):

        # ======================================
        # CLIENTE PARCEIRO
        # ======================================

        if self.cliente and self.cliente.parceiro:

            self.preco_unitario = 3.5

        # ======================================
        # CLIENTE NORMAL OU AVULSO
        # ======================================

        else:

            self.preco_unitario = self.produto.preco

        # ======================================
        # CALCULAR VALOR TOTAL
        # ======================================

        self.valor_total = (
            self.preco_unitario * self.quantidade
        )

        super().save(*args, **kwargs)

    # ==========================================
    # NOME DA VENDA
    # ==========================================

    def __str__(self):

        if self.cliente:

            nome = self.cliente.nome

        elif self.cliente_avulso:

            nome = self.cliente_avulso

        else:

            nome = "Cliente não informado"

        return f"{nome} - {self.quantidade} sacos"


# ==========================================
# RESUMO DE VENDAS (proxy para o Admin)
# ==========================================

class ResumoVendas(Venda):
    class Meta:
        proxy = True
        verbose_name = "Resumo de Vendas"
        verbose_name_plural = "Resumo de Vendas"
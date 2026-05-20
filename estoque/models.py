from django.db import models
from django.utils import timezone

#cadastro de clientes

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco_unitario = models.DecimalField(max_digits=6, decimal_places=2)
    preco_atacado = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quantidade_atacado = models.IntegerField(default=100)
    ativo = models.BooleanField(default=True)
    parceiro = models.BooleanField(default=False)

    def __str__(self):
        return self.nome
   # cadastro de produtos 
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
    #cadastro de classe de vendas , com as informações de cadastro por clientes

    from django.utils import timezone

class Venda(models.Model):
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cliente_avulso = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    preco_unitario = models.DecimalField(max_digits=6, decimal_places=2)
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    pago = models.BooleanField(default=False)
    data = models.DateTimeField(default=timezone.now)

    # 👇 pode ficar aqui embaixo dos campos
    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco

        self.valor_total = self.quantidade * self.preco_unitario

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.quantidade}"

    def save(self, *args, **kwargs):
        # aplica preço especial se for cliente parceiro
        if self.cliente.parceiro:
            self.preco_unitario = 3.5
        else:
            self.preco_unitario = self.produto.preco

        self.valor_total = self.preco_unitario * self.quantidade

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.quantidade} sacos"

        #cadastro de calsse dos clientes avulsos

        class Venda(models.Model):
            pass
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    cliente_avulso = models.CharField(max_length=100, blank=True, null=True)

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

    pago = models.BooleanField(default=True)  # pago na hora ou fiado

    data = models.DateTimeField(auto_now_add=True)
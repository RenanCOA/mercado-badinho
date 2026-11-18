# Mercado Badinho

Simulador de supermercado em Python executado pelo terminal.

## Funcionalidades

- Cadastro, consulta, atualização e remoção de produtos.
- Salvamento automático do catálogo em `produtos.json`.
- Carrinho com controle de estoque e desconto de 15% para compras com mais de 2 unidades no total.
- Pagamento simulado em dinheiro, cartão ou Pix, com cálculo de troco para dinheiro.
- Emissão de comprovante no terminal.

## Como executar

Tenha o Python 3 instalado e execute:

```powershell
python "Mercado Badinho 1.1.py"
```

Na primeira execução, o catálogo começa vazio. O arquivo `produtos.json` será criado ao cadastrar o primeiro produto e carregado nas próximas execuções. Esse arquivo contém dados locais do estoque e não é enviado ao repositório.

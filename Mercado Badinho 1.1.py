
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ARQUIVO_DADOS = Path(__file__).with_name("produtos.json")
ARQUIVO_TEMPORARIO = ARQUIVO_DADOS.with_suffix(".tmp")
ESTOQUE_MAXIMO = 200
CENTAVO = Decimal("0.01")


def carregar_produtos():
    try:
        with ARQUIVO_DADOS.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as erro:
        raise ValueError(
            f"O arquivo '{ARQUIVO_DADOS.name}' contém JSON inválido."
        ) from erro

    if not isinstance(dados, list):
        raise ValueError(
            f"O arquivo '{ARQUIVO_DADOS.name}' deve conter uma lista de produtos."
        )

    for produto in dados:
        if (
            not isinstance(produto, dict)
            or not isinstance(produto.get("nome"), str)
            or not isinstance(produto.get("preco"), (int, float))
            or not isinstance(produto.get("quantidade"), int)
        ):
            raise ValueError(
                f"O arquivo '{ARQUIVO_DADOS.name}' contém um produto inválido."
            )

    return dados


def salvar_produtos():
    with ARQUIVO_TEMPORARIO.open("w", encoding="utf-8") as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=4)

    ARQUIVO_TEMPORARIO.replace(ARQUIVO_DADOS)


produtos = carregar_produtos()


# LOCALIZAR UM PRODUTO PELO NOME
def buscar_produto(nome):
    for produto in produtos:
        if produto["nome"].lower() == nome.lower():
            return produto

    return None


# FORMATAR VALORES EM REAIS
def formatar_moeda(valor):
    valor = Decimal(str(valor)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return f"R$ {valor:.2f}".replace(".", ",")


# PEDIR UM PREÇO ATÉ RECEBER UM VALOR VÁLIDO
def ler_preco(mensagem):
    while True:
        entrada = input(mensagem).strip().replace(",", ".")

        try:
            preco = float(entrada)

            if preco <= 0:
                print("O preço precisa ser maior que zero.")
                continue

            return preco

        except ValueError:
            print("Preço inválido. Exemplo: 8,50")


# PEDIR UMA QUANTIDADE DENTRO DE UM LIMITE
def ler_quantidade(mensagem, minimo, maximo):
    while True:
        try:
            quantidade = int(input(mensagem))

            if quantidade < minimo or quantidade > maximo:
                print(f"Digite uma quantidade entre {minimo} e {maximo}.")
                continue

            return quantidade

        except ValueError:
            print("Quantidade inválida. Digite um número inteiro.")


# SELECIONAR UM PRODUTO JÁ CADASTRADO
def selecionar_produto():
    if not produtos:
        print("Nenhum produto cadastrado.")
        return None

    while True:
        nome = input(
            "Digite o nome do produto (ou 0 para voltar): "
        ).strip()

        if nome == "0":
            return None

        produto = buscar_produto(nome)

        if produto is None:
            print("Produto não encontrado. Tente novamente.")
        else:
            return produto


# 1 - CADASTRAR PRODUTO

def cadastrar_produto():
    print("\n--- CADASTRO DE PRODUTO ---")

    while True:
        nome = input(
            "Nome do produto (ou digite 'cancelar'): "
        ).strip()

        if nome.lower() == "cancelar":
            print("Cadastro cancelado.")
            return

        if not nome:
            print("O nome não pode ficar vazio.")
            continue

        if buscar_produto(nome) is not None:
            print("Esse produto já está cadastrado.")
            continue

        break

    preco = ler_preco("Preço unitário: R$ ")

    if preco is None:
        print("Cadastro cancelado.")
        return

    quantidade = ler_quantidade(
        "Quantidade inicial em estoque: ",
        0,
        ESTOQUE_MAXIMO
    )

    if quantidade is None:
        print("Cadastro cancelado.")
        return

    produto = {
        "nome": nome,
        "preco": preco,
        "quantidade": quantidade
    }

    produtos.append(produto)
    salvar_produtos()

    print(f"\nProduto '{nome}' cadastrado com sucesso!")

    
def ler_preco(mensagem):
    while True:
        entrada = input(
            mensagem + " (ou digite 'cancelar'): "
        ).strip()

        if entrada.lower() == "cancelar":
            return None

        entrada = entrada.replace(",", ".")

        try:
            preco = float(entrada)

            if preco <= 0:
                print("O preço precisa ser maior que zero.")
                continue

            return preco

        except ValueError:
            print("Preço inválido. Exemplo: 8,50")


# 2 - ADICIONAR ESTOQUE
def adicionar_estoque():
    print("\n--- ADICIONAR ESTOQUE ---")

    produto = selecionar_produto()

    if produto is None:
        return

    limite = ESTOQUE_MAXIMO - produto["quantidade"]

    if limite == 0:
        print("Esse produto já atingiu o estoque máximo.")
        return

    quantidade = ler_quantidade(
        f"Quantas unidades deseja adicionar? (máximo {limite}): ",
        1,
        limite
    )

    produto["quantidade"] += quantidade
    salvar_produtos()

    print("Estoque atualizado com sucesso!")


# 3 - CONSULTAR PRODUTOS
def consultar_produtos():
    print("\n--- TABELA DE PRODUTOS ---")

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    print(
        f"{'PRODUTO':<25} {'PREÇO':>12} "
        f"{'QTD.':>8} {'TOTAL':>16}"
    )

    print("-" * 65)

    valor_total_estoque = 0

    for produto in produtos:
        valor_estoque = produto["preco"] * produto["quantidade"]

        valor_total_estoque += valor_estoque

        nome = produto["nome"][:25]

        print(
            f"{nome:<25} "
            f"{formatar_moeda(produto['preco']):>12} "
            f"{produto['quantidade']:>8} "
            f"{formatar_moeda(valor_estoque):>16}"
        )

    print("-" * 65)

    print(f"Produtos cadastrados: {len(produtos)}")
    print(f"Valor total do estoque: {formatar_moeda(valor_total_estoque)}")


# 4 - ALTERAR PREÇO
def alterar_preco():
    print("\n--- ALTERAR PREÇO ---")

    produto = selecionar_produto()

    if produto is None:
        return

    print(f"Produto: {produto['nome']}")
    print(f"Preço atual: {formatar_moeda(produto['preco'])}")

    novo_preco = ler_preco("Digite o novo preço: R$ ")

    if novo_preco is None:
        print("Alteração cancelada.")
        return

    produto["preco"] = novo_preco
    salvar_produtos()

    print("Preço atualizado com sucesso!")


def alterar_nome():
    print("\n--- ALTERAR NOME DO PRODUTO ---")

    produto = selecionar_produto()

    if produto is None:
        return

    while True:
        novo_nome = input(
            "Digite o novo nome (ou digite 'cancelar'): "
        ).strip()

        if novo_nome.lower() == "cancelar":
            print("Alteração cancelada.")
            return

        if not novo_nome:
            print("O nome não pode ficar vazio.")
            continue

        produto_existente = buscar_produto(novo_nome)

        if produto_existente is not None and produto_existente is not produto:
            print("Já existe um produto cadastrado com esse nome.")
            continue

        break

    produto["nome"] = novo_nome
    salvar_produtos()

    print("Nome do produto atualizado com sucesso!")


# 6 - REMOVER PRODUTO
def remover_produto():
    print("\n--- REMOVER PRODUTO ---")

    produto = selecionar_produto()

    if produto is None:
        return

    while True:
        confirmar = input(
            f"Confirma a remoção de '{produto['nome']}'? (s/n): "
        ).strip().lower()

        if confirmar == "s":
            produtos.remove(produto)
            salvar_produtos()
            print("Produto removido com sucesso!")
            break

        elif confirmar == "n":
            print("Remoção cancelada.")
            break

        else:
            print("Resposta inválida. Digite s ou n.")


def calcular_resumo_carrinho(carrinho):
    unidades = sum(item["quantidade"] for item in carrinho)
    subtotal = sum(
        (
            Decimal(str(item["produto"]["preco"])) * item["quantidade"]
            for item in carrinho
        ),
        Decimal("0")
    ).quantize(
        CENTAVO,
        rounding=ROUND_HALF_UP
    )
    desconto = (
        (subtotal * Decimal("0.15")).quantize(
            CENTAVO,
            rounding=ROUND_HALF_UP
        )
        if unidades > 2
        else Decimal("0.00")
    )
    total = subtotal - desconto

    return unidades, subtotal, desconto, total


def exibir_carrinho(carrinho):
    print("\n--- CARRINHO DE COMPRAS ---")

    if not carrinho:
        print("O carrinho está vazio.")
        return

    for item in carrinho:
        produto = item["produto"]
        quantidade = item["quantidade"]
        total_item = produto["preco"] * quantidade

        print(
            f"{produto['nome']} x {quantidade} - "
            f"{formatar_moeda(total_item)}"
        )

    unidades, subtotal, desconto, total = calcular_resumo_carrinho(carrinho)
    print(f"Unidades no carrinho: {unidades}")
    print(f"Subtotal: {formatar_moeda(subtotal)}")

    if desconto:
        print(f"Desconto de 15%: -{formatar_moeda(desconto)}")

    print(f"Total: {formatar_moeda(total)}")


def adicionar_ao_carrinho(carrinho):
    produto = selecionar_produto()

    if produto is None:
        return

    item_existente = next(
        (
            item for item in carrinho
            if item["produto"] is produto
        ),
        None
    )
    quantidade_no_carrinho = (
        item_existente["quantidade"] if item_existente else 0
    )
    disponivel = produto["quantidade"] - quantidade_no_carrinho

    if disponivel <= 0:
        print("Não há unidades disponíveis desse produto para adicionar.")
        return

    quantidade = ler_quantidade(
        f"Quantidade desejada (máximo {disponivel}): ",
        1,
        disponivel
    )

    if item_existente:
        item_existente["quantidade"] += quantidade
    else:
        carrinho.append({
            "produto": produto,
            "quantidade": quantidade
        })

    print("Produto adicionado ao carrinho.")


def selecionar_pagamento(total):
    while True:
        print("\n--- FORMA DE PAGAMENTO ---")
        print("1 - Dinheiro")
        print("2 - Cartão")
        print("3 - Pix")
        print("0 - Cancelar pagamento")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            while True:
                recebido = ler_preco(
                    "Valor recebido em dinheiro: R$ "
                )

                if recebido is None:
                    return None

                recebido = Decimal(str(recebido)).quantize(
                    CENTAVO,
                    rounding=ROUND_HALF_UP
                )

                if recebido < total:
                    print(
                        f"Valor insuficiente. Total da compra: "
                        f"{formatar_moeda(total)}"
                    )
                    continue

                return "Dinheiro", recebido, recebido - total

        if opcao == "2":
            return "Cartão", total, Decimal("0.00")

        if opcao == "3":
            return "Pix", total, Decimal("0.00")

        if opcao == "0":
            return None

        print("Opção inválida. Escolha uma forma de pagamento.")


def imprimir_comprovante(carrinho, resumo, pagamento):
    unidades, subtotal, desconto, total = resumo
    forma_pagamento, recebido, troco = pagamento

    print("\n========================================")
    print("      COMPROVANTE - MERCADO BADINHO")
    print("========================================")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("----------------------------------------")

    for item in carrinho:
        produto = item["produto"]
        quantidade = item["quantidade"]
        total_item = produto["preco"] * quantidade

        print(
            f"{produto['nome']} x {quantidade} - "
            f"{formatar_moeda(total_item)}"
        )

    print("----------------------------------------")
    print(f"Unidades: {unidades}")
    print(f"Subtotal: {formatar_moeda(subtotal)}")

    if desconto:
        print(f"Desconto de 15%: -{formatar_moeda(desconto)}")

    print(f"Total pago: {formatar_moeda(total)}")
    print(f"Pagamento: {forma_pagamento}")

    if forma_pagamento == "Dinheiro":
        print(f"Valor recebido: {formatar_moeda(recebido)}")
        print(f"Troco: {formatar_moeda(troco)}")

    print("========================================")
    print("Obrigado pela preferência!")


def finalizar_compra(carrinho):
    resumo = calcular_resumo_carrinho(carrinho)
    pagamento = selecionar_pagamento(resumo[3])

    if pagamento is None:
        print("Pagamento cancelado. O estoque não foi alterado.")
        return False

    for item in carrinho:
        item["produto"]["quantidade"] -= item["quantidade"]

    salvar_produtos()
    imprimir_comprovante(carrinho, resumo, pagamento)
    return True


def realizar_compra():
    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    carrinho = []

    while True:
        print("\n--- CARRINHO DE COMPRAS ---")
        print("1 - Adicionar produto")
        print("2 - Visualizar carrinho")
        print("3 - Finalizar compra")
        print("4 - Cancelar compra")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            adicionar_ao_carrinho(carrinho)

        elif opcao == "2":
            exibir_carrinho(carrinho)

        elif opcao == "3":
            if not carrinho:
                print("Adicione pelo menos um produto ao carrinho.")
                continue

            exibir_carrinho(carrinho)
            confirmar = input(
                "Deseja prosseguir para o pagamento? (s/n): "
            ).strip().lower()

            if confirmar == "s":
                if finalizar_compra(carrinho):
                    return
            elif confirmar != "n":
                print("Resposta inválida. Digite s ou n.")

        elif opcao == "4":
            print("Compra cancelada.")
            return

        else:
            print("Opção inválida. Escolha uma opção de 1 a 4.")


# MENU PRINCIPAL
while True:
    print("\n================================")
    print("       MERCADO BADINHO")
    print("================================")
    print("1 - Cadastrar produto")
    print("2 - Adicionar estoque")
    print("3 - Consultar produtos")
    print("4 - Alterar preço")
    print("5 - Alterar nome do produto")
    print("6 - Remover produto")
    print("7 - Realizar compra")
    print("8 - Encerrar sistema")
    print("================================")

    opcao = input("Escolha uma opção: ").strip()

    if opcao == "1":
        cadastrar_produto()

    elif opcao == "2":
        adicionar_estoque()

    elif opcao == "3":
        consultar_produtos()

    elif opcao == "4":
        alterar_preco()

    elif opcao == "5":
        alterar_nome()

    elif opcao == "6":
        remover_produto()

    elif opcao == "7":
        realizar_compra()

    elif opcao == "8":
        print("Encerrando o Mercado Badinho. Até logo!")
        break

    else:
        print("Opção inválida. Escolha uma opção de 1 a 8.")

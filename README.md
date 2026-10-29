# Meu Financeiro — Sistema de Gestão Financeira Pessoal

Aplicação web de exemplo que combina **HTML, CSS, JavaScript, Python (Flask) e SQL (SQLite)**.

## Funcionalidades
- Cadastro de receitas e despesas com categorias, data e observações.
- Resumo do período: receitas, despesas e saldo.
- Filtros por intervalo de datas, tipo e categoria.
- Gráfico de despesas por categoria.
- Criação de metas, atualização do valor economizado e barra de progresso.
- Exportação das transações filtradas para CSV compatível com planilhas.
- Exclusão de transações e metas.


## Onde cada tecnologia é usada
- **HTML:** formulários, filtros, tabelas, metas e estrutura do painel (`templates/index.html`).
- **CSS:** identidade visual, layout responsivo, cartões e estados visuais (`static/style.css`).
- **JavaScript:** troca dinâmica das categorias e renderização do gráfico com Chart.js.
- **Python:** rotas, validação de dados, cálculo de saldos, filtros e exportação CSV (`app.py`).
- **SQL:** tabelas `transactions` e `goals`, consultas e persistência usando SQLite.

## Estrutura
```text
gestao_financeira_pessoal/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    └── style.css




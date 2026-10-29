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

## Requisitos
- Python 3.10 ou superior
- Navegador moderno
- Internet para carregar Chart.js e fontes externas via CDN (a aplicação funciona sem o gráfico caso a CDN esteja indisponível).

## Como executar

1. Extraia o ZIP e abra o terminal dentro da pasta do projeto.
2. Crie um ambiente virtual (recomendado):

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie a aplicação:
   ```bash
   python app.py
   ```

5. Abra `http://127.0.0.1:5000` no navegador.

O arquivo `financeiro.db` é criado automaticamente na primeira inicialização e guarda os dados localmente.

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
```

## Observações importantes
- Este é um projeto de portfólio/estudo, não um serviço financeiro pronto para produção.
- Não inclui login, sincronização em nuvem, criptografia de dados ou integração bancária.
- Antes de publicar na internet, altere a chave secreta, desative `debug=True`, implemente autenticação e proteção CSRF, validação mais rigorosa e backups.
- Os cálculos de resumo respeitam o intervalo filtrado. Sem filtro de datas, o painel começa no primeiro dia do mês atual e vai até hoje.

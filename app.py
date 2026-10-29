from flask import Flask, render_template, request, redirect, url_for, Response, flash
import sqlite3
import csv
import io
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"
DB_PATH = "financeiro.db"

CATEGORIES = {
    "Receita": ["Salário", "Freelance", "Investimentos", "Presentes", "Outros"],
    "Despesa": ["Moradia", "Alimentação", "Transporte", "Saúde", "Educação",
                "Lazer", "Contas", "Compras", "Dívidas", "Outros"]
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL CHECK(kind IN ('Receita', 'Despesa')),
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            transaction_date TEXT NOT NULL,
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL CHECK(target_amount > 0),
            saved_amount REAL NOT NULL DEFAULT 0 CHECK(saved_amount >= 0),
            deadline TEXT
        );
        """)

def parse_filters():
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    kind = request.args.get("kind", "").strip()
    category = request.args.get("category", "").strip()
    return start, end, kind, category

@app.route("/")
def index():
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    month_end = today.isoformat()
    start, end, kind, category = parse_filters()
    # The dashboard defaults to the current month; custom dates override it.
    query_start = start or month_start
    query_end = end or month_end
    clauses, params = ["transaction_date >= ?", "transaction_date <= ?"], [query_start, query_end]
    if kind in ("Receita", "Despesa"):
        clauses.append("kind = ?")
        params.append(kind)
    if category:
        clauses.append("category = ?")
        params.append(category)
    where = " AND ".join(clauses)

    with get_db() as conn:
        transactions = conn.execute(
            f"SELECT * FROM transactions WHERE {where} ORDER BY transaction_date DESC, id DESC",
            params
        ).fetchall()
        # Monthly summary uses the selected range.
        summary = conn.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN kind='Receita' THEN amount ELSE 0 END), 0) AS income,
              COALESCE(SUM(CASE WHEN kind='Despesa' THEN amount ELSE 0 END), 0) AS expenses
            FROM transactions WHERE transaction_date >= ? AND transaction_date <= ?
        """, (query_start, query_end)).fetchone()
        category_rows = conn.execute("""
            SELECT category, SUM(amount) AS total FROM transactions
            WHERE kind='Despesa' AND transaction_date >= ? AND transaction_date <= ?
            GROUP BY category ORDER BY total DESC
        """, (query_start, query_end)).fetchall()
        goals = conn.execute("SELECT * FROM goals ORDER BY id DESC").fetchall()

    income = summary["income"]
    expenses = summary["expenses"]
    return render_template(
        "index.html", transactions=transactions, goals=goals,
        income=income, expenses=expenses, balance=income-expenses,
        categories=CATEGORIES, selected_kind=kind, selected_category=category,
        start=start, end=end, query_start=query_start, query_end=query_end,
        chart_labels=[r["category"] for r in category_rows],
        chart_values=[round(r["total"], 2) for r in category_rows],
        today=today.isoformat()
    )

@app.route("/transaction", methods=["POST"])
def add_transaction():
    kind = request.form.get("kind", "")
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    raw_amount = request.form.get("amount", "").replace(",", ".").strip()
    transaction_date = request.form.get("transaction_date", "")
    notes = request.form.get("notes", "").strip()
    try:
        amount = float(raw_amount)
        if amount <= 0:
            raise ValueError
        datetime.strptime(transaction_date, "%Y-%m-%d")
        if kind not in CATEGORIES or category not in CATEGORIES[kind] or not description:
            raise ValueError
    except (ValueError, TypeError):
        flash("Confira os campos: valor positivo, data válida, descrição e categoria.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute("""INSERT INTO transactions
            (kind, description, category, amount, transaction_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (kind, description, category, amount, transaction_date, notes))
    flash("Transação cadastrada com sucesso!", "success")
    return redirect(url_for("index"))

@app.route("/transaction/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction(transaction_id):
    with get_db() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    flash("Transação excluída.", "success")
    return redirect(url_for("index"))

@app.route("/goal", methods=["POST"])
def add_goal():
    name = request.form.get("name", "").strip()
    deadline = request.form.get("deadline", "").strip() or None
    try:
        target = float(request.form.get("target_amount", "").replace(",", "."))
        saved = float(request.form.get("saved_amount", "0").replace(",", ".") or 0)
        if not name or target <= 0 or saved < 0:
            raise ValueError
        if deadline:
            datetime.strptime(deadline, "%Y-%m-%d")
    except (ValueError, TypeError):
        flash("Informe um nome e valores válidos para a meta.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute("INSERT INTO goals (name, target_amount, saved_amount, deadline) VALUES (?, ?, ?, ?)",
                     (name, target, saved, deadline))
    flash("Meta criada com sucesso!", "success")
    return redirect(url_for("index"))

@app.route("/goal/<int:goal_id>/progress", methods=["POST"])
def update_goal(goal_id):
    try:
        saved = float(request.form.get("saved_amount", "").replace(",", "."))
        if saved < 0:
            raise ValueError
    except (ValueError, TypeError):
        flash("Informe um valor acumulado válido.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute("UPDATE goals SET saved_amount = ? WHERE id = ?", (saved, goal_id))
    flash("Progresso da meta atualizado.", "success")
    return redirect(url_for("index"))

@app.route("/goal/<int:goal_id>/delete", methods=["POST"])
def delete_goal(goal_id):
    with get_db() as conn:
        conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    flash("Meta excluída.", "success")
    return redirect(url_for("index"))

@app.route("/export.csv")
def export_csv():
    start, end, kind, category = parse_filters()
    today = date.today()
    query_start = start or today.replace(day=1).isoformat()
    query_end = end or today.isoformat()
    clauses, params = ["transaction_date >= ?", "transaction_date <= ?"], [query_start, query_end]
    if kind in ("Receita", "Despesa"):
        clauses.append("kind = ?"); params.append(kind)
    if category:
        clauses.append("category = ?"); params.append(category)
    with get_db() as conn:
        rows = conn.execute(
            f"SELECT transaction_date, kind, description, category, amount, notes FROM transactions WHERE {' AND '.join(clauses)} ORDER BY transaction_date",
            params
        ).fetchall()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Data", "Tipo", "Descrição", "Categoria", "Valor (R$)", "Observações"])
    for row in rows:
        writer.writerow([row["transaction_date"], row["kind"], row["description"], row["category"],
                         f'{row["amount"]:.2f}'.replace(".", ","), row["notes"]])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=relatorio_financeiro.csv"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

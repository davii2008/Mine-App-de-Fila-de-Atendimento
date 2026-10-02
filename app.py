from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave-fila-atendimento"

DATABASE = "fila.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            prioridade TEXT NOT NULL DEFAULT 'Normal',
            status TEXT NOT NULL DEFAULT 'Aguardando',
            criado_em TEXT NOT NULL,
            iniciado_em TEXT,
            concluido_em TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    fila = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
    """).fetchall()

    em_atendimento = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status = 'Em Atendimento'
        ORDER BY iniciado_em ASC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        fila=fila,
        em_atendimento=em_atendimento
    )


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form.get("nome", "").strip()
    prioridade = request.form.get("prioridade", "Normal")

    if not nome:
        flash("Digite o nome do cliente.", "erro")
        return redirect(url_for("index"))

    if prioridade not in ("Normal", "Preferencial"):
        prioridade = "Normal"

    conn = get_db()
    conn.execute("""
        INSERT INTO atendimentos (nome, prioridade, status, criado_em)
        VALUES (?, ?, 'Aguardando', ?)
    """, (nome, prioridade, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    conn.commit()
    conn.close()

    flash(f"{nome} foi adicionado à fila.", "sucesso")
    return redirect(url_for("index"))


@app.route("/chamar")
def chamar_proximo():
    conn = get_db()

    # Impede chamar outro cliente enquanto existe atendimento em andamento.
    atual = conn.execute("""
        SELECT id FROM atendimentos
        WHERE status = 'Em Atendimento'
        LIMIT 1
    """).fetchone()

    if atual:
        flash("Finalize o atendimento atual antes de chamar o próximo.", "erro")
        conn.close()
        return redirect(url_for("index"))

    cliente = conn.execute("""
        SELECT id, nome FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
        LIMIT 1
    """).fetchone()

    if not cliente:
        flash("Não há clientes aguardando.", "erro")
        conn.close()
        return redirect(url_for("index"))

    conn.execute("""
        UPDATE atendimentos
        SET status = 'Em Atendimento', iniciado_em = ?
        WHERE id = ?
    """, (
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        cliente["id"]
    ))
    conn.commit()
    conn.close()

    flash(f"Próximo cliente: {cliente['nome']}", "sucesso")
    return redirect(url_for("index"))


@app.route("/status/<int:id>", methods=["POST"])
def alterar_status(id):
    novo_status = request.form.get("status")

    if novo_status not in ("Aguardando", "Em Atendimento", "Concluído"):
        flash("Status inválido.", "erro")
        return redirect(url_for("index"))

    conn = get_db()

    if novo_status == "Em Atendimento":
        outro = conn.execute("""
            SELECT id FROM atendimentos
            WHERE status = 'Em Atendimento' AND id != ?
            LIMIT 1
        """, (id,)).fetchone()

        if outro:
            flash("Já existe um atendimento em andamento.", "erro")
            conn.close()
            return redirect(url_for("index"))

        conn.execute("""
            UPDATE atendimentos
            SET status = ?, iniciado_em = ?
            WHERE id = ?
        """, (
            novo_status,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            id
        ))

    elif novo_status == "Concluído":
        conn.execute("""
            UPDATE atendimentos
            SET status = ?, concluido_em = ?
            WHERE id = ?
        """, (
            novo_status,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            id
        ))

    else:
        conn.execute("""
            UPDATE atendimentos
            SET status = ?, iniciado_em = NULL, concluido_em = NULL
            WHERE id = ?
        """, (novo_status, id))

    conn.commit()
    conn.close()
    flash("Status atualizado.", "sucesso")
    return redirect(url_for("index"))


@app.route("/cancelar/<int:id>", methods=["POST"])
def cancelar(id):
    conn = get_db()
    conn.execute("""
        UPDATE atendimentos
        SET status = 'Cancelado', concluido_em = ?
        WHERE id = ?
    """, (
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        id
    ))
    conn.commit()
    conn.close()

    flash("Atendimento cancelado.", "sucesso")
    return redirect(url_for("index"))


@app.route("/historico")
def historico():
    conn = get_db()
    registros = conn.execute("""
        SELECT * FROM atendimentos
        WHERE status IN ('Concluído', 'Cancelado')
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template("historico.html", registros=registros)


@app.route("/limpar")
def limpar_historico():
    conn = get_db()
    conn.execute("""
        DELETE FROM atendimentos
        WHERE status IN ('Concluído', 'Cancelado')
    """)
    conn.commit()
    conn.close()

    flash("Histórico limpo.", "sucesso")
    return redirect(url_for("historico"))


@app.route("/api/fila")
def api_fila():
    conn = get_db()
    fila = conn.execute("""
        SELECT id, nome, prioridade, status
        FROM atendimentos
        WHERE status = 'Aguardando'
        ORDER BY
            CASE WHEN prioridade = 'Preferencial' THEN 0 ELSE 1 END,
            id ASC
    """).fetchall()
    conn.close()

    return {
        "fila": [dict(item) for item in fila]
    }


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

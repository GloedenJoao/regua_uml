"""Initialize the Flask application and database.

This module creates the Flask application instance, configures
SQLAlchemy to use a SQLite database and registers the database models.
The use of SQLite is convenient because it is built into Python and
does not require a separate server. However, writes occur sequentially,
so heavy write loads can slow down【779944838122452†L12-L20】.  For this
project, which will be used to define CRM communication schedules,
SQLite is sufficient.

The application enables foreign‑key support for SQLite and
configures cascade behaviour on foreign keys so that deleting a
parent record automatically deletes dependent records; SQLite
implements this behaviour via the `ON DELETE CASCADE` clause【685663684588476†L559-L563】.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    # Secret key for sessions/flash messages. Replace with a strong value in production.
    app.config['SECRET_KEY'] = 'dev'
    # SQLite database file. The database will be created automatically.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///regua_comunicacao.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialise database
    db.init_app(app)

    # Enable SQLite foreign key enforcement each time a connection is created.
    # Without this pragma SQLite ignores foreign keys by default.【685663684588476†L559-L563】
    @app.before_request
    def before_request():
        from sqlalchemy import text
        db.session.execute(text('PRAGMA foreign_keys = ON'))

    # Import models so that they are registered with SQLAlchemy
    from . import models  # noqa: F401

    # Register routes
    from .routes import bp as routes_bp  # noqa: F401
    app.register_blueprint(routes_bp)

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
        _ensure_schema()

    return app


def _ensure_schema() -> None:
    """Garante colunas adicionadas em versões posteriores sem precisar de migração."""

    from sqlalchemy import text
    from sqlalchemy.orm import selectinload
    from .models import DiaComunicacao, TemaRegra, Tema

    engine = db.get_engine()

    def coluna_existe(tabela: str, coluna: str) -> bool:
        with engine.connect() as conn:
            info = conn.execute(text(f"PRAGMA table_info('{tabela}')")).fetchall()
        return any(linha[1] == coluna for linha in info)

    alter_statements = []
    if not coluna_existe('temas', 'jornada_id'):
        alter_statements.append(
            "ALTER TABLE temas ADD COLUMN jornada_id INTEGER REFERENCES jornadas(id) ON DELETE SET NULL"
        )
    if not coluna_existe('dias_comunicacoes', 'jornada_id'):
        alter_statements.append("ALTER TABLE dias_comunicacoes ADD COLUMN jornada_id INTEGER")
    if not coluna_existe('dias_comunicacoes', 'jornada_nome'):
        alter_statements.append("ALTER TABLE dias_comunicacoes ADD COLUMN jornada_nome VARCHAR(120)")

    if alter_statements:
        with engine.begin() as conn:
            for comando in alter_statements:
                conn.execute(text(comando))

    dias = (
        DiaComunicacao.query.options(
            selectinload(DiaComunicacao.tema_regra)
            .selectinload(TemaRegra.tema)
            .selectinload(Tema.jornada),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.alternativa),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.regra),
        ).all()
    )
    alterado = False
    for dia in dias:
        tema_regra = dia.tema_regra
        tema = tema_regra.tema if tema_regra else None
        if tema:
            if dia.tema_id != tema.id:
                dia.tema_id = tema.id
                alterado = True
            if dia.tema_nome != (tema.nome or dia.tema_nome):
                dia.tema_nome = tema.nome or dia.tema_nome
                alterado = True
            jornada = tema.jornada
            jornada_id = jornada.id if jornada else None
            jornada_nome = jornada.nome if jornada else None
            if dia.jornada_id != jornada_id or dia.jornada_nome != jornada_nome:
                dia.jornada_id = jornada_id
                dia.jornada_nome = jornada_nome
                alterado = True
        if tema_regra:
            alternativa = tema_regra.alternativa
            alt_tema_id = alternativa.tema_id if alternativa else None
            if dia.tema_id_alternativo != alt_tema_id:
                dia.tema_id_alternativo = alt_tema_id
                alterado = True
            if dia.regra_id != tema_regra.regra_id:
                dia.regra_id = tema_regra.regra_id
                alterado = True

    if alterado:
        db.session.commit()

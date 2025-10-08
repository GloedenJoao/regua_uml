"""Database models for the CRM communication ruler application.

The tables correspond to the entities described by the user: Temas,
Regras, Temas_Regras and Dias_Comunicacoes.  Each table uses
SQLAlchemy to declare fields and relationships.  Foreign keys are
declared with ON DELETE CASCADE so that when a parent record is
deleted, all dependent records are automatically removed【685663684588476†L559-L563】.

The `Tema` table includes a self‑referential foreign key for
`id_alternativo` which is nullable and models alternative themes.

SQLAlchemy relationships are used to make it easy to navigate between
entities in Python.  Back‑references are provided where helpful for
listing dependents.
"""

from . import db


class Tema(db.Model):
    __tablename__ = 'temas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    objetivo = db.Column(db.Text, nullable=True)
    id_alternativo = db.Column(
        db.Integer,
        db.ForeignKey('temas.id', ondelete='SET NULL'),
        nullable=True,
    )

    # Relationship to the alternative theme. Use remote_side so SQLAlchemy can
    # distinguish between the parent and child in a self‑referential relationship.
    alternativo = db.relationship('Tema', remote_side=[id], backref='variacoes')

    def __repr__(self):
        return f"<Tema {self.id}: {self.nome}>"


class Regra(db.Model):
    __tablename__ = 'regras'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Regra {self.id}>"


class TemaRegra(db.Model):
    __tablename__ = 'temas_regras'
    id = db.Column(db.Integer, primary_key=True)
    tema_id = db.Column(
        db.Integer,
        db.ForeignKey('temas.id', ondelete='CASCADE'),
        nullable=False,
    )
    regra_id = db.Column(
        db.Integer,
        db.ForeignKey('regras.id', ondelete='CASCADE'),
        nullable=False,
    )
    tema_id_alternativo = db.Column(
        db.Integer,
        db.ForeignKey('temas.id', ondelete='SET NULL'),
        nullable=True,
    )

    tema = db.relationship('Tema', foreign_keys=[tema_id], backref='tema_regras')
    regra = db.relationship('Regra', foreign_keys=[regra_id], backref='tema_regras')
    tema_alternativo = db.relationship(
        'Tema', foreign_keys=[tema_id_alternativo], backref='tema_regra_alternativas'
    )

    def __repr__(self):
        return f"<TemaRegra {self.id}: Tema {self.tema_id} – Regra {self.regra_id}>"


class DiaComunicacao(db.Model):
    __tablename__ = 'dias_comunicacoes'
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.Integer, nullable=False)  # Valor maior ou igual a zero
    tema_regra_id = db.Column(
        db.Integer,
        db.ForeignKey('temas_regras.id', ondelete='CASCADE'),
        nullable=False,
    )

    tema_regra = db.relationship('TemaRegra', backref='dias')

    def __repr__(self):
        return f"<Dia {self.id}: Dia {self.dia} para TemaRegra {self.tema_regra_id}>"
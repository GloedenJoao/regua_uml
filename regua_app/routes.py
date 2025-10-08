"""Application routes for the CRM communication ruler app.

This module defines the Flask routes responsible for displaying
templates, processing form submissions and deleting or editing records.
Each route corresponds to one of the tables defined by the user: Temas,
Regras, Temas_Regras and Dias_Comunicacoes.  The routes follow a
simple CRUD pattern (Create, Read, Update, Delete).

UML generation uses the Graphviz Python package to assemble a
directed graph that represents each Tema‑Regra and its communication
days.  Graphviz must be installed at the system level (e.g. using
`brew install graphviz`) and the Python package must also be
installed (`pip install graphviz`)【326654681106756†L221-L234】.  Nodes and
edges are defined using the `Digraph` class and rendered to a PNG
file【326654681106756†L246-L266】.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from . import db
from .models import Tema, Regra, TemaRegra, DiaComunicacao

bp = Blueprint('routes', __name__)


@bp.route('/')
def home():
    """Home page showing lists of all existing records and options to add new."""
    temas = Tema.query.all()
    regras = Regra.query.all()
    temas_regras = TemaRegra.query.all()
    dias = DiaComunicacao.query.all()
    return render_template(
        'home.html',
        temas=temas,
        regras=regras,
        temas_regras=temas_regras,
        dias=dias,
    )


@bp.route('/tema/novo', methods=['GET', 'POST'])
def novo_tema():
    """Create a new Tema.  Presents a form and handles submission."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        objetivo = request.form.get('objetivo')
        id_alternativo = request.form.get('id_alternativo') or None
        tema = Tema(
            nome=nome,
            descricao=descricao,
            objetivo=objetivo,
            id_alternativo=int(id_alternativo) if id_alternativo else None,
        )
        db.session.add(tema)
        db.session.commit()
        flash('Tema criado com sucesso!')
        return redirect(url_for('routes.home'))

    temas_existentes = Tema.query.all()
    return render_template('tema_form.html', temas=temas_existentes, tema=None)


@bp.route('/tema/<int:tema_id>/editar', methods=['GET', 'POST'])
def editar_tema(tema_id):
    """Edit an existing Tema."""
    tema = Tema.query.get_or_404(tema_id)
    if request.method == 'POST':
        tema.nome = request.form.get('nome')
        tema.descricao = request.form.get('descricao')
        tema.objetivo = request.form.get('objetivo')
        id_alternativo = request.form.get('id_alternativo') or None
        tema.id_alternativo = int(id_alternativo) if id_alternativo else None
        db.session.commit()
        flash('Tema atualizado com sucesso!')
        return redirect(url_for('routes.home'))
    temas_existentes = Tema.query.filter(Tema.id != tema_id).all()
    return render_template('tema_form.html', temas=temas_existentes, tema=tema)


@bp.route('/tema/<int:tema_id>/deletar', methods=['POST'])
def deletar_tema(tema_id):
    """Delete a Tema and cascade delete related records."""
    tema = Tema.query.get_or_404(tema_id)
    db.session.delete(tema)
    db.session.commit()
    flash('Tema deletado com sucesso!')
    return redirect(url_for('routes.home'))


@bp.route('/regra/novo', methods=['GET', 'POST'])
def novo_regra():
    """Create a new Regra."""
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        regra = Regra(descricao=descricao)
        db.session.add(regra)
        db.session.commit()
        flash('Regra criada com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template('regra_form.html', regra=None)


@bp.route('/regra/<int:regra_id>/editar', methods=['GET', 'POST'])
def editar_regra(regra_id):
    """Edit a Regra."""
    regra = Regra.query.get_or_404(regra_id)
    if request.method == 'POST':
        regra.descricao = request.form.get('descricao')
        db.session.commit()
        flash('Regra atualizada com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template('regra_form.html', regra=regra)


@bp.route('/regra/<int:regra_id>/deletar', methods=['POST'])
def deletar_regra(regra_id):
    """Delete a Regra and cascade delete related TemaRegra and Dias."""
    regra = Regra.query.get_or_404(regra_id)
    db.session.delete(regra)
    db.session.commit()
    flash('Regra deletada com sucesso!')
    return redirect(url_for('routes.home'))


@bp.route('/tema_regra/novo', methods=['GET', 'POST'])
def novo_tema_regra():
    """Create a new TemaRegra linking a Tema and a Regra."""
    temas = Tema.query.all()
    regras = Regra.query.all()
    if request.method == 'POST':
        tema_id = int(request.form.get('tema_id'))
        regra_id = int(request.form.get('regra_id'))
        tema_id_alternativo = request.form.get('tema_id_alternativo') or None
        tr = TemaRegra(
            tema_id=tema_id,
            regra_id=regra_id,
            tema_id_alternativo=int(tema_id_alternativo)
            if tema_id_alternativo
            else None,
        )
        db.session.add(tr)
        db.session.commit()
        flash('Vínculo Tema–Regra criado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template(
        'tema_regra_form.html', temas=temas, regras=regras, tema_regra=None
    )


@bp.route('/tema_regra/<int:tr_id>/editar', methods=['GET', 'POST'])
def editar_tema_regra(tr_id):
    """Edit a TemaRegra relationship."""
    tema_regra = TemaRegra.query.get_or_404(tr_id)
    temas = Tema.query.all()
    regras = Regra.query.all()
    if request.method == 'POST':
        tema_regra.tema_id = int(request.form.get('tema_id'))
        tema_regra.regra_id = int(request.form.get('regra_id'))
        tema_id_alternativo = request.form.get('tema_id_alternativo') or None
        tema_regra.tema_id_alternativo = (
            int(tema_id_alternativo) if tema_id_alternativo else None
        )
        db.session.commit()
        flash('Vínculo Tema–Regra atualizado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template(
        'tema_regra_form.html', temas=temas, regras=regras, tema_regra=tema_regra
    )


@bp.route('/tema_regra/<int:tr_id>/deletar', methods=['POST'])
def deletar_tema_regra(tr_id):
    """Delete a TemaRegra and cascade delete its Dias."""
    tema_regra = TemaRegra.query.get_or_404(tr_id)
    db.session.delete(tema_regra)
    db.session.commit()
    flash('Vínculo Tema–Regra deletado com sucesso!')
    return redirect(url_for('routes.home'))


@bp.route('/dia/novo', methods=['GET', 'POST'])
def novo_dia():
    """Create a new DiaComunicacao for a given TemaRegra."""
    tema_regras = TemaRegra.query.all()
    if request.method == 'POST':
        dia = int(request.form.get('dia'))
        tr_id = int(request.form.get('tr_id'))
        dc = DiaComunicacao(dia=dia, tema_regra_id=tr_id)
        db.session.add(dc)
        db.session.commit()
        flash('Dia de comunicação adicionado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template('dia_form.html', tema_regras=tema_regras, dia=None)


@bp.route('/dia/<int:dia_id>/editar', methods=['GET', 'POST'])
def editar_dia(dia_id):
    """Edit an existing DiaComunicacao."""
    dia = DiaComunicacao.query.get_or_404(dia_id)
    tema_regras = TemaRegra.query.all()
    if request.method == 'POST':
        dia.dia = int(request.form.get('dia'))
        dia.tema_regra_id = int(request.form.get('tr_id'))
        db.session.commit()
        flash('Dia atualizado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template('dia_form.html', tema_regras=tema_regras, dia=dia)


@bp.route('/dia/<int:dia_id>/deletar', methods=['POST'])
def deletar_dia(dia_id):
    """Delete a DiaComunicacao."""
    dia = DiaComunicacao.query.get_or_404(dia_id)
    db.session.delete(dia)
    db.session.commit()
    flash('Dia de comunicação deletado com sucesso!')
    return redirect(url_for('routes.home'))


@bp.route('/uml')
def uml():
    """Renderiza o diagrama da régua usando Mermaid em vez de Graphviz.

    Esta versão não requer a instalação do executável Graphviz.  Para cada
    `TemaRegra` o código monta uma linha Mermaid no formato:

        TR1["Tema / Regra"] -->|Dia X| END

    que o Mermaid renderizará como uma aresta rotulada.  O nó "END" é
    adicionado ao final do diagrama para representar o destino das
    comunicações.
    """
    lines = ["graph LR"]
    # Mapeia cada dia para a lista de comunicações (Tema / Regra) associadas
    dias_dict = {}
    # Faz uma consulta que já traz as relações necessárias
    dias = (
        DiaComunicacao.query
        .join(DiaComunicacao.tema_regra)
        .join(TemaRegra.tema)
        .join(TemaRegra.regra)
        .all()
    )
    for dia in dias:
        numero = dia.dia
        # Constrói a etiqueta com o tema e a descrição da regra
        etiqueta = f"{dia.tema_regra.tema.nome} / {dia.tema_regra.regra.descricao}"
        dias_dict.setdefault(numero, []).append(etiqueta)
    # Ordena os dias para criar a série histórica
    sorted_days = sorted(dias_dict.keys())
    if sorted_days:
        # Define um nó para cada dia com as comunicações listadas
        for numero in sorted_days:
            etiquetas = dias_dict[numero]
            # Remove duplicidades mantendo a ordem
            unique_labels = list(dict.fromkeys(etiquetas))
            # Constrói a string da etiqueta com quebras de linha
            label_str = "<br/>".join(unique_labels)
            lines.append(f"    D{numero}[\"Dia {numero}<br/>{label_str}\"]")
        # Conecta cada dia ao seguinte em ordem
        for i in range(len(sorted_days) - 1):
            atual = sorted_days[i]
            proximo = sorted_days[i + 1]
            lines.append(f"    D{atual} --> D{proximo}")
        # Conecta o último dia ao fim
        ultimo = sorted_days[-1]
        lines.append(f"    D{ultimo} --> END")
    else:
        # Caso não existam dias registrados
        lines.append("    D0[\"Sem dias cadastrados\"] --> END")
    # Define o nó final
    lines.append("    END(Fim)")
    mermaid_code = "\n".join(lines)
    return render_template('uml.html', mermaid_code=mermaid_code)
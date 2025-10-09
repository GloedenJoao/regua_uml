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
    Response
)
from . import db
from .models import Tema, Regra, TemaRegra, DiaComunicacao
from sqlalchemy.orm import selectinload


bp = Blueprint('routes', __name__)


def ensure_regra_padrao() -> None:
    """Garante que a regra padrão "Sem Regra" exista na base de dados."""
    if not Regra.query.filter_by(descricao='Sem Regra').first():
        regra_padrao = Regra(descricao='Sem Regra')
        db.session.add(regra_padrao)
        db.session.commit()


@bp.route('/')
def home():
    """Home page showing lists of all existing records and options to add new."""
    ensure_regra_padrao()
    temas = Tema.query.order_by(Tema.nome).all()
    regras = Regra.query.order_by(Regra.descricao).all()
    temas_regras = (
        TemaRegra.query.options(
            selectinload(TemaRegra.tema),
            selectinload(TemaRegra.regra),
            selectinload(TemaRegra.alternativa).selectinload(TemaRegra.tema),
            selectinload(TemaRegra.alternativa).selectinload(TemaRegra.regra),
        )
        .order_by(TemaRegra.id)
        .all()
    )
    dias = (
        DiaComunicacao.query.options(
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.tema),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.regra),
        )
        .order_by(DiaComunicacao.dia, DiaComunicacao.id)
        .all()
    )
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
        tema = Tema(
            nome=nome,
            descricao=descricao,
            objetivo=objetivo,
        )
        db.session.add(tema)
        db.session.commit()
        flash('Tema criado com sucesso!')
        return redirect(url_for('routes.home'))

    temas = Tema.query.order_by(Tema.nome).all()
    return render_template('tema_form.html', tema=None, temas=temas)


@bp.route('/tema/<int:tema_id>/editar', methods=['GET', 'POST'])
def editar_tema(tema_id):
    """Edit an existing Tema."""
    tema = Tema.query.get_or_404(tema_id)
    if request.method == 'POST':
        tema.nome = request.form.get('nome')
        tema.descricao = request.form.get('descricao')
        tema.objetivo = request.form.get('objetivo')
        db.session.commit()
        flash('Tema atualizado com sucesso!')
        return redirect(url_for('routes.home'))
    temas = Tema.query.order_by(Tema.nome).all()
    return render_template('tema_form.html', tema=tema, temas=temas)


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
    ensure_regra_padrao()
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        regra = Regra(descricao=descricao)
        db.session.add(regra)
        db.session.commit()
        flash('Regra criada com sucesso!')
        return redirect(url_for('routes.home'))
    regras = Regra.query.order_by(Regra.descricao).all()
    return render_template('regra_form.html', regra=None, regras=regras)


@bp.route('/regra/<int:regra_id>/editar', methods=['GET', 'POST'])
def editar_regra(regra_id):
    """Edit a Regra."""
    regra = Regra.query.get_or_404(regra_id)
    ensure_regra_padrao()
    if request.method == 'POST':
        regra.descricao = request.form.get('descricao')
        db.session.commit()
        flash('Regra atualizada com sucesso!')
        return redirect(url_for('routes.home'))
    regras = Regra.query.order_by(Regra.descricao).all()
    return render_template('regra_form.html', regra=regra, regras=regras)


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
    temas = Tema.query.order_by(Tema.nome).all()
    regras = Regra.query.order_by(Regra.descricao).all()
    tema_regra_lista = (
        TemaRegra.query.options(
            selectinload(TemaRegra.tema),
            selectinload(TemaRegra.regra),
            selectinload(TemaRegra.alternativa).selectinload(TemaRegra.tema),
            selectinload(TemaRegra.alternativa).selectinload(TemaRegra.regra),
        )
        .order_by(TemaRegra.id)
        .all()
    )
    preselected_tema_id = request.args.get('tema_id', type=int)
    if request.method == 'POST':
        tema_id = int(request.form.get('tema_id'))
        regra_id = int(request.form.get('regra_id'))
        alternativa_id = request.form.get('alternativa_id') or None
        tr = TemaRegra(
            tema_id=tema_id,
            regra_id=regra_id,
            alternativa_id=int(alternativa_id) if alternativa_id else None,
        )
        db.session.add(tr)
        db.session.commit()
        flash('Vínculo Tema–Regra criado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template(
        'tema_regra_form.html',
        temas=temas,
        regras=regras,
        tema_regra=None,
        tema_regra_opcoes=tema_regra_lista,
        tema_regra_lista=tema_regra_lista,
        preselected_tema_id=preselected_tema_id,
    )


@bp.route('/tema_regra/<int:tr_id>/editar', methods=['GET', 'POST'])
def editar_tema_regra(tr_id):
    """Edit a TemaRegra relationship."""
    tema_regra = TemaRegra.query.get_or_404(tr_id)
    temas = Tema.query.order_by(Tema.nome).all()
    regras = Regra.query.order_by(Regra.descricao).all()
    tema_regra_lista = (
        TemaRegra.query.options(
            selectinload(TemaRegra.tema),
            selectinload(TemaRegra.regra),
            selectinload(TemaRegra.alternativa).selectinload(TemaRegra.tema),
            selectinload(TemaRegra.alternativa).selectinload(TemaRegra.regra),
        )
        .order_by(TemaRegra.id)
        .all()
    )
    tema_regra_opcoes = (
        TemaRegra.query.options(
            selectinload(TemaRegra.tema),
            selectinload(TemaRegra.regra),
        )
        .filter(TemaRegra.id != tr_id)
        .order_by(TemaRegra.id)
        .all()
    )
    if request.method == 'POST':
        tema_regra.tema_id = int(request.form.get('tema_id'))
        tema_regra.regra_id = int(request.form.get('regra_id'))
        alternativa_id = request.form.get('alternativa_id') or None
        if alternativa_id:
            alternativa_id = int(alternativa_id)
            # Evita ciclos ao selecionar como alternativa um vínculo
            # que já depende deste registro.
            corrente = TemaRegra.query.get(alternativa_id)
            visitados = {tema_regra.id}
            while corrente and corrente.alternativa_id:
                if corrente.alternativa_id in visitados:
                    flash(
                        'A comunicação alternativa selecionada gera um ciclo. '
                        'Escolha outro vínculo.',
                        'warning',
                    )
                    return render_template(
                        'tema_regra_form.html',
                        temas=temas,
                        regras=regras,
                        tema_regra=tema_regra,
                        tema_regra_opcoes=tema_regra_opcoes,
                    )
                visitados.add(corrente.alternativa_id)
                corrente = TemaRegra.query.get(corrente.alternativa_id)
        tema_regra.alternativa_id = alternativa_id
        db.session.commit()
        flash('Vínculo Tema–Regra atualizado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template(
        'tema_regra_form.html',
        temas=temas,
        regras=regras,
        tema_regra=tema_regra,
        tema_regra_opcoes=tema_regra_opcoes,
        tema_regra_lista=tema_regra_lista,
        preselected_tema_id=tema_regra.tema_id,
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
    tema_regras = (
        TemaRegra.query.options(
            selectinload(TemaRegra.tema),
            selectinload(TemaRegra.regra),
        )
        .order_by(TemaRegra.id)
        .all()
    )
    dias_existentes = (
        DiaComunicacao.query.options(
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.tema),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.regra),
        )
        .order_by(DiaComunicacao.dia, DiaComunicacao.id)
        .all()
    )
    if request.method == 'POST':
        dia = int(request.form['dia'])
        tr_id = int(request.form['tr_id'])
        tr = TemaRegra.query.get_or_404(tr_id)
        # cria o registro copiando os dados do vínculo
        dc = DiaComunicacao(
            dia=dia,
            tema_regra_id=tr_id,
            tema_id=tr.tema_id,
            tema_nome=tr.tema.nome,
            regra_id=tr.regra_id,
            tema_id_alternativo=(
                tr.alternativa.tema_id if getattr(tr, 'alternativa', None) else None
            ),
        )
        db.session.add(dc)
        db.session.commit()
        flash('Dia de comunicação adicionado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template(
        'dia_form.html',
        tema_regras=tema_regras,
        dia=None,
        dias=dias_existentes,
    )


@bp.route('/dia/<int:dia_id>/editar', methods=['GET', 'POST'])
def editar_dia(dia_id):
    """Edit an existing DiaComunicacao."""
    dia = DiaComunicacao.query.get_or_404(dia_id)
    tema_regras = (
        TemaRegra.query.options(
            selectinload(TemaRegra.tema),
            selectinload(TemaRegra.regra),
        )
        .order_by(TemaRegra.id)
        .all()
    )
    dias_existentes = (
        DiaComunicacao.query.options(
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.tema),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.regra),
        )
        .order_by(DiaComunicacao.dia, DiaComunicacao.id)
        .all()
    )
    if request.method == 'POST':
        dia.dia = int(request.form.get('dia'))
        dia.tema_regra_id = int(request.form.get('tr_id'))
        db.session.commit()
        flash('Dia atualizado com sucesso!')
        return redirect(url_for('routes.home'))
    return render_template(
        'dia_form.html',
        tema_regras=tema_regras,
        dia=dia,
        dias=dias_existentes,
    )


@bp.route('/dia/<int:dia_id>/deletar', methods=['POST'])
def deletar_dia(dia_id):
    """Delete a DiaComunicacao."""
    dia = DiaComunicacao.query.get_or_404(dia_id)
    db.session.delete(dia)
    db.session.commit()
    flash('Dia de comunicação deletado com sucesso!')
    return redirect(url_for('routes.home'))


from .models import DiaComunicacao, TemaRegra


def gerar_diagrama_mermaid() -> str:
    """Monta o código Mermaid (flowchart LR) com cadeia de alternativas."""
    from sqlalchemy.orm import selectinload

    # Todos os vínculos Tema–Regra para facilitar a navegação pelas alternativas
    tema_regra_map = {
        tr.id: tr
        for tr in (
            TemaRegra.query.options(
                selectinload(TemaRegra.tema),
                selectinload(TemaRegra.regra),
            ).all()
        )
    }

    dias = (
        DiaComunicacao.query.options(selectinload(DiaComunicacao.tema_regra))
        .order_by(DiaComunicacao.dia, DiaComunicacao.id)
        .all()
    )

    por_dia = {}
    for d in dias:
        por_dia.setdefault(d.dia, []).append(d)

    ordered_days = sorted(por_dia.keys())

    fim_dia_valor = 99999
    fim_node_id = f"D{fim_dia_valor}"
    day_nodes = []
    decision_nodes = []

    if not ordered_days:
        lines = [
            "flowchart LR",
            "    SD[\"Sem dias cadastrados\"]",
            f"    {fim_node_id}[\"Fim\"]:::dia",
            f"    SD --> {fim_node_id}",
            "    classDef dia fill:#FFF3CD,stroke:#C77D00,stroke-width:2px,rx:8,ry:8;",
            f"    class {fim_node_id} dia",
        ]
        return "\n".join(lines)

    def sanitize(texto: str, default: str) -> str:
        texto = (texto or '').strip()
        if not texto:
            texto = default
        texto = texto.replace('"', "'").replace('\n', '<br/>')
        return texto

    def regra_para_decisao(texto: str) -> str:
        texto = sanitize(texto, 'Regra')
        if not texto.endswith('?'):
            texto = f"{texto}?"
        return texto

    def cadeia_alternativas(tr_inicial):
        cadeia = []
        visitados = set()
        corrente = tr_inicial
        while corrente and corrente.id not in visitados:
            visitados.add(corrente.id)
            cadeia.append(corrente)
            prox_id = getattr(corrente, 'alternativa_id', None)
            if prox_id:
                corrente = tema_regra_map.get(prox_id)
            else:
                corrente = None
        return cadeia

    lines = ["flowchart LR"]

    for n in ordered_days:
        node_id = f'D{n}'
        lines.append(f'    {node_id}["Dia {n}"]:::dia')
        day_nodes.append(node_id)

    lines.append(f'    {fim_node_id}["Fim"]:::dia')
    day_nodes.append(fim_node_id)

    for i in range(len(ordered_days) - 1):
        a, b = ordered_days[i], ordered_days[i + 1]
        lines.append(f'    D{a} --> D{b}')

    if ordered_days:
        lines.append(f'    D{ordered_days[-1]} --> {fim_node_id}')

    for dia_valor in ordered_days:
        blocos = por_dia[dia_valor]
        for idx, registro in enumerate(blocos, start=1):
            tema_regra = tema_regra_map.get(registro.tema_regra_id)
            if not tema_regra:
                continue

            cadeia = cadeia_alternativas(tema_regra)
            if not cadeia:
                continue

            etapas = []
            for nivel, etapa in enumerate(cadeia):
                tema_label = sanitize(
                    etapa.tema.nome if etapa.tema else registro.tema_nome,
                    'Tema',
                )
                regra_label = sanitize(
                    etapa.regra.descricao if etapa.regra else '',
                    '',
                )
                has_rule = bool(regra_label) and regra_label.lower() not in {
                    'sem regra',
                }
                entry_id = f'ST{dia_valor}_{idx}_{nivel}_ENTRY'
                msg_id = f'ST{dia_valor}_{idx}_{nivel}_MSG'
                if not has_rule:
                    entry_id = msg_id
                etapas.append(
                    {
                        'nivel': nivel,
                        'entry_id': entry_id,
                        'msg_id': msg_id,
                        'tema': tema_label,
                        'regra': regra_label,
                        'has_rule': has_rule,
                    }
                )

            for etapa in etapas:
                if etapa['has_rule']:
                    entry_id = etapa["entry_id"]
                    lines.append(
                        f'    {entry_id}{{"{regra_para_decisao(etapa["regra"])}"}}'
                    )
                    decision_nodes.append(entry_id)
                lines.append(f'    {etapa["msg_id"]}["{etapa["tema"]}"]')

            for pos, etapa in enumerate(etapas):
                entry_id = etapa['entry_id']
                msg_id = etapa['msg_id']
                if etapa['has_rule']:
                    if pos == 0:
                        lines.append(f'    D{dia_valor} --> {entry_id}')
                    lines.append(f'    {entry_id} -->|Sim| {msg_id}')
                    if pos < len(etapas) - 1:
                        prox_entry = etapas[pos + 1]['entry_id']
                        lines.append(f'    {entry_id} -->|Não| {prox_entry}')
                    else:
                        lines.append(f'    {entry_id} -->|Não| {msg_id}')
                else:
                    if pos == 0:
                        lines.append(f'    D{dia_valor} --> {msg_id}')

    if day_nodes:
        lines.append('    classDef dia fill:#FFF3CD,stroke:#C77D00,stroke-width:2px,rx:8,ry:8;')
        lines.append(f"    class {','.join(day_nodes)} dia")

    if decision_nodes:
        lines.append('    classDef decisao fill:#E2F0FF,stroke:#0F5DA3,stroke-width:2px;')
        lines.append(f"    class {','.join(decision_nodes)} decisao")

    return "\n".join(lines)




@bp.route('/uml')
def uml():
    mermaid_code = gerar_diagrama_mermaid()
    return render_template('uml.html', mermaid_code=mermaid_code)


@bp.route('/uml/download')
def download_uml():
    """
    Rota mantida apenas para compatibilidade.
    Hoje o PDF é gerado no navegador (sem depender do servidor).
    Esta rota retorna o código Mermaid atual como texto, caso alguém queira exportar.
    """
    codigo = gerar_diagrama_mermaid()
    resp = Response(codigo, mimetype='text/plain; charset=utf-8')
    resp.headers['Content-Disposition'] = 'attachment; filename=diagrama_uml.mmd'
    return resp

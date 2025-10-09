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
    tema_regras = TemaRegra.query.all()
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
            tema_id_alternativo=tr.tema_id_alternativo
        )
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


from .models import DiaComunicacao, TemaRegra

def gerar_diagrama_mermaid() -> str:
    """
    Gera o Mermaid (flowchart LR) mantendo os DIAS alinhados no topo:
      1) Declara todos os nós de dia (D0..Dn).
      2) Conecta D0 --> D1 --> ... --> Dn (isso ancora a 'linha' dos dias).
      3) Para cada dia, adiciona decisão (se houver alternativo) e/ou tema(s),
         ligando SEMPRE para baixo a partir de Dn (sem voltar para a cadeia de dias).
    """
    from sqlalchemy.orm import selectinload
    from .models import DiaComunicacao, TemaRegra

    dias = (
        DiaComunicacao.query
        .options(
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.tema),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.regra),
            selectinload(DiaComunicacao.tema_regra).selectinload(TemaRegra.tema_alternativo),
        )
        .all()
    )

    # if not dias:
    #     return 'flowchart LR\n    D0["Sem dias cadastrados"] --> END\n    END(Fim)'

    # Agrupa por dia
    por_dia = {}
    for d in dias:
        por_dia.setdefault(d.dia, []).append(d)

    ordered_days = sorted(por_dia.keys())
    lines = []
    lines.append("flowchart LR")

    # 1) Declarar todos os nós de dia primeiro (ancora no topo visual)
    for n in ordered_days:
        lines.append(f'    D{n}["Dia {n}"]')

    # 2) Conectar a série histórica dos dias
    for i in range(len(ordered_days) - 1):
        a, b = ordered_days[i], ordered_days[i + 1]
        lines.append(f'    D{a} --> D{b}')

    # 3) Para cada dia, acrescentar decisões/temas somente para "baixo"
    for n in ordered_days:
        blocos = por_dia[n]
        for idx, d in enumerate(blocos, start=1):
            tema_principal = (
                (d.tema_nome or "").strip()
                or (d.tema_regra.tema.nome.strip()
                    if d.tema_regra and d.tema_regra.tema and d.tema_regra.tema.nome
                    else "Tema")
            )

            # Existe alternativo?
            tem_alt = bool(d.tema_regra and d.tema_regra.tema_alternativo)

            if tem_alt:
                regra_desc = (
                    (d.tema_regra.regra.descricao or "").strip()
                    if d.tema_regra and d.tema_regra.regra else "Regra"
                )
                tema_alt = (
                    d.tema_regra.tema_alternativo.nome.strip()
                    if d.tema_regra.tema_alternativo and d.tema_regra.tema_alternativo.nome
                    else "Alternativo"
                )

                dec_id  = f"DEC{n}_{idx}"
                tpri_id = f"T{n}_{idx}_P"
                talt_id = f"T{n}_{idx}_A"

                # Declarar nós adicionais após a cadeia de dias
                lines.append(f'    {dec_id}{{"{regra_desc}?"}}')
                lines.append(f'    {tpri_id}["{tema_principal}"]')
                lines.append(f'    {talt_id}["{tema_alt}"]')

                # Conectar a partir de D{n} para baixo
                lines.append(f'    D{n} --> {dec_id}')
                lines.append(f'    {dec_id} -->|Sim| {tpri_id}')
                lines.append(f'    {dec_id} -->|Não| {talt_id}')

            else:
                tpri_id = f"T{n}_{idx}_P"
                lines.append(f'    {tpri_id}["{tema_principal}"]')
                lines.append(f'    D{n} --> {tpri_id}')

    # Nó final
    # lines.append(f'    D{ordered_days[-1]} --> END')
    # lines.append('    END(Fim)')

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

# app.py
import duckdb
from shiny import App, ui, reactive, render
from shiny.ui import tags
from pathlib import Path
import os


from style import custom_css
from data import get_unidades_disponiveis,get_eixos_sql,get_donut_sql,get_ranking_sql,get_distribuicao_sql,get_eixos_sql_disciplina,get_donut_sql_disciplina,get_ranking_sql_disciplina,get_distribuicao_sql_disciplina
from components import *
from ui_content import get_home_content
from logic_filter import setup_cascading_filters
from modules import dashboard_ui, dashboard_server
from upload_page import criar_pagina_upload  
from ingestao import processar_excel  

www_dir = Path(__file__).parent / "www"

status_ingestao_msg = None

app_ui = ui.page_fluid(
    tags.head(
        tags.style(custom_css),
        tags.title("Fechamento CPA - Universidade Federal do Paraná"), 
        tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css", crossorigin="anonymous"),
        tags.link(rel="icon", type="image/png", href="/static/icon.png?v=2"),
        tags.link(rel="shortcut icon", href="/static/icon.png?v=2")
    ),
    
    ui.output_ui("css_controlador"), 
    tags.div(class_="overlay-escura"),
    
    render_sidebar_nav(), 
    render_header_ufpr("btn_sidebar_toggle"), 
    
    tags.div(
        ui.navset_hidden(
            ui.nav_panel("home", get_home_content()),
            
            # Aba Institucional usando Módulo
            ui.nav_panel("institucional", 
                dashboard_ui("inst", "Institucional", criar_filtro_simples("inst"))
            ),
            
            # Aba Cursos usando Módulo
            ui.nav_panel("cursos", 
                dashboard_ui("cursos", "Cursos", criar_filtro_simples("curso"))
            ),
            
            # Aba Disciplinas usando Módulo
            ui.nav_panel("disciplinas", 
                dashboard_ui("disc", "Disciplinas", criar_filtro_disciplinas())
            ),
            
            # NOVA ABA: Upload de Dados
            ui.nav_panel("upload", criar_pagina_upload()),
            
            id="router_principal"
        ), class_="conteudo-spa"
    ), padding=0
)

def server(input, output, session):
    global status_ingestao_msg
    
    
    estado_menu = reactive.Value(False)
    
    @reactive.effect
    @reactive.event(input.btn_sidebar_toggle)
    def _(): estado_menu.set(not estado_menu.get())
        
    @reactive.effect
    @reactive.event(input.btn_fechar)
    def _(): estado_menu.set(False)
    
    def navegar_para(page_id): 
        ui.update_navset("router_principal", selected=page_id)
        estado_menu.set(False)
    
    @reactive.effect
    @reactive.event(input.nav_home)
    def _(): navegar_para("home")
    
    @reactive.effect
    @reactive.event(input.nav_inst)
    def _(): navegar_para("institucional")
    
    @reactive.effect
    @reactive.event(input.nav_cursos)
    def _(): navegar_para("cursos")
    
    @reactive.effect
    @reactive.event(input.nav_disc)
    def _(): navegar_para("disciplinas")
    
    
    @reactive.effect
    @reactive.event(input.nav_upload)
    def _(): navegar_para("upload")
    
    @render.ui
    def css_controlador(): 
        return tags.style(".menu-lateral { display: flex !important;} .overlay-escura { display: block !important; }") if estado_menu.get() else None

    
    unidades = get_unidades_disponiveis()
    ui.update_select("inst_campus", choices=unidades)
    ui.update_select("curso_campus", choices=unidades)
    
    
    setup_cascading_filters(input, ui)

    
    # Institucional
    dados_inst = reactive.Value(get_eixos_sql("Institucional", "Todos"))
    donut_inst = reactive.Value(get_donut_sql("Institucional", "Todos"))
    barras_inst = reactive.Value(get_ranking_sql("Institucional", "Todos"))
    dist_inst = reactive.Value(get_distribuicao_sql("Institucional", "Todos"))

    # Cursos
    dados_curso = reactive.Value(get_eixos_sql("Cursos", "Todos"))
    donut_curso = reactive.Value(get_donut_sql("Cursos", "Todos"))
    barras_curso = reactive.Value(get_ranking_sql("Cursos", "Todos"))
    dist_curso = reactive.Value(get_distribuicao_sql("Cursos", "Todos"))

    # Disciplinas
    dados_disc = reactive.Value((0, []))
    donut_disc = reactive.Value({"total": 0, "concordo": 0, "neutro": 0, "discordo": 0})
    barras_disc = reactive.Value({"titulo": "Top Disciplinas", "dados": []})
    dist_disc = reactive.Value({"notas": [], "media": 0})

    
    status_ingestao_msg = reactive.Value("")
    
    @output
    @render.text
    def status_ingestao():
        return status_ingestao_msg.get()
    
    
    @reactive.Effect
    @reactive.event(input.processar_excel)
    def _():
        file = input.upload_excel()

        if file is None:
            status_ingestao_msg.set(" Nenhum arquivo enviado.")
            return

        caminho_temp = file[0]["datapath"]
        
        try:
            #
            status_ingestao_msg.set("Carregando arquivo Excel...")
            
            
            BANCO_PRINCIPAL_PATH = r"C:\Users\gabri\Documents\theoutliers-ufpr-hackathon\data\db\hackathon.duckdb"
            
            
            total_registros = processar_excel(
                caminho_temp, 
                BANCO_PRINCIPAL_PATH,
                evitar_duplicatas=True
            )
            
            status_ingestao_msg.set(f"Sucesso! {total_registros} registros inseridos no banco.")
            
        except Exception as e:
            
            import traceback
            erro_detalhado = traceback.format_exc()
            print(f"ERRO DETALHADO:\n{erro_detalhado}")
            
            
            status_ingestao_msg.set(f" Erro ao processar arquivo:\n{str(e)[:150]}")
    
    
    @reactive.Effect
    @reactive.event(input.baixar_pdf)
    def _():
        pdf_path = os.path.join(www_dir, "manual_ingestao.pdf")

        if not os.path.exists(pdf_path):
            status_ingestao_msg.set("PDF não encontrado.")
            return

        os.system(f'start "" "{pdf_path}"')
        status_ingestao_msg.set("Manual aberto.")

    
    @reactive.effect
    @reactive.event(input.inst_btn_filtrar)
    def _():
        u = input.inst_campus()
        dados_inst.set(get_eixos_sql("Institucional", u))
        donut_inst.set(get_donut_sql("Institucional", u))
        barras_inst.set(get_ranking_sql("Institucional", u))
        dist_inst.set(get_distribuicao_sql("Institucional", u))

    @reactive.effect
    @reactive.event(input.curso_btn_filtrar)
    def _():
        u = input.curso_campus()
        dados_curso.set(get_eixos_sql("Cursos", u))
        donut_curso.set(get_donut_sql("Cursos", u))
        barras_curso.set(get_ranking_sql("Cursos", u))
        dist_curso.set(get_distribuicao_sql("Cursos", u))

    @reactive.effect
    @reactive.event(input.disc_btn_filtrar)
    def _():
        setor = input.disc_setor()
        depto = input.disc_depto()
        curso = input.disc_curso()
        disciplina = input.disc_disciplina()
        modalidade = input.disc_modalidade() 

        dados_disc.set(get_eixos_sql_disciplina(setor, depto, curso, disciplina, modalidade))
        donut_disc.set(get_donut_sql_disciplina(setor, depto, curso, disciplina, modalidade))
        barras_disc.set(get_ranking_sql_disciplina(setor, depto, curso, disciplina, modalidade))
        dist_disc.set(get_distribuicao_sql_disciplina(setor, depto, curso, disciplina, modalidade))

    
    dashboard_server("inst", dados_inst, donut_inst, barras_inst, dist_inst)
    dashboard_server("cursos", dados_curso, donut_curso, barras_curso, dist_curso)
    dashboard_server("disc", dados_disc, donut_disc, barras_disc, dist_disc)

app = App(app_ui, server, static_assets={"/static": www_dir})

import os

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
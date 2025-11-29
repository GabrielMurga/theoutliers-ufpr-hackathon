from shiny import App, ui, reactive, render
from shiny.ui import tags

custom_css = """
    /* --- RESET & GERAL --- */
    html, body { margin: 0 !important; padding: 0 !important; width: 100%; height: 100%; overflow: hidden; }
    .container-fluid { padding: 0 !important; max-width: 100% !important; }
    .bg { background-color: #fff; }

    /* --- HEADER UFPR --- */
    .ufpr-header {
        background-color: #004b8d; color: white; height: 80px;
        display: flex; gap: 35px; align-items: center;
        padding: 55px 80px; 
        width: 100%; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        z-index: 1; 
        position: relative;
    }
    
    h4 { font-family: 'Roboto', sans-serif; font-weight: 600; font-size: 28px; margin: 0; }
    img { width: 100; max-width: 120px; }

    /* --- BOTÃO MENU HEADER --- */
    .btn-reset {
        color: white !important; background: transparent !important;
        border: none !important; text-decoration: none !important;
        cursor: pointer !important; padding: 0 !important; margin: 0 !important;
        display: flex !important; align-items: center;
    }
    .btn-reset:hover { opacity: 0.8; }
    
    /* --- SIDEBAR --- */
    .menu-lateral {
        position: fixed; z-index: 99999;
        background-color: #fff;    
        padding: 25px 55px;
        height: 100vh; width: 350px; 
        display: none; 
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        flex-direction: column !important; 
    }
    
    /* --- ESTILIZAÇÃO DOS BOTÕES DO MENU (MODIFICADO) --- */
    .btn-nav-custom {
        width: 100%; text-align: left; margin-bottom: 10px;
        background: transparent; border: none; color: #333;
        font-size: 18px; padding: 10px; /* Adicionei padding geral para o fundo não ficar colado */
        border-bottom: 1px solid #eee; transition: 0.2s;
        border-radius: 5px; /* Arredonda levemente os cantos do hover */
    }
    
    .btn-nav-custom:hover { 
        padding-left: 20px; /* Aumenta o deslocamento para a direita */
        background-color: #f5f5dc; /* <--- O BEGE AQUI */
        color: #000; /* <--- Mantém PRETO/ESCURO em vez de azul */
        font-weight: 500; 
    }

    .overlay-escura {
        background-color: black; position:fixed; top: 0; left:0; width: 100vw; z-index:999; height: 100vh; opacity: .5; padding: 20px; display: none;
    }

    /* --- BOTÃO FECHAR (X) --- */
    #btn_fechar {
        align-self: flex-end !important;
        background-color: transparent !important; border: none !important;
        box-shadow: none !important; outline: none !important;
        width: auto !important; padding: 0 !important; line-height: 1 !important; margin-bottom: 20px !important;
        font-size: 24px !important; font-weight: bold !important; color: #333 !important;
    }
    #btn_fechar:hover, #btn_fechar:active, #btn_fechar:focus {
        background-color: transparent !important; color: #333 !important; box-shadow: none !important; border: none !important; outline: none !important;
    }

    /* --- CONTEUDO PRINCIPAL (SPA CONTAINER) --- */
    .conteudo-spa {
        padding: 40px 80px;
        height: calc(100vh - 80px); 
        overflow-y: auto; 
    }
    
    .page-title { color: #004b8d; margin-bottom: 20px; border-bottom: 2px solid #004b8d; padding-bottom: 10px; display: inline-block; }
"""

app_ui = ui.page_fluid(
    tags.head(tags.style(custom_css)),
    tags.head(
        tags.link(rel="preconnect", href="https://fonts.googleapis.com"),
        tags.link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin="anonymous"),
        tags.link(href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap", rel="stylesheet"),
        tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"), 
    ),

    ui.output_ui("css_controlador"), 

    tags.div(class_="overlay-escura"),

    # --- MENU LATERAL ---
    tags.section(
        ui.input_action_button("btn_fechar", "✕"), 

        tags.nav(
            tags.ul(
                tags.li(ui.input_action_button("nav_home", "Painel Principal", class_="btn-nav-custom")), 
                tags.li(ui.input_action_button("nav_inst", "Institucional", class_="btn-nav-custom")), 
                tags.li(ui.input_action_button("nav_cursos", "Cursos", class_="btn-nav-custom")), 
                tags.li(ui.input_action_button("nav_disc", "Disciplinas", class_="btn-nav-custom"))
            ),
            style="list-style: none; padding: 0;"
        ), 
        class_="menu-lateral"
    ),

    # --- HEADER ---
    tags.header(
        ui.input_action_link(
            "btn_sidebar_toggle",  
            label=None,
            icon=tags.i(class_="fa-solid fa-bars", style="font-size:24px;"), 
            class_="btn-reset"
        ),
        tags.img(src="https://ufpr.br/wp-content/themes/wpufpr_bootstrap5_portal/images/ufpr.png"),
        tags.h4("UNIVERSIDADE FEDERAL DO PARANÁ"),
        class_="ufpr-header"
    ),

    # --- SPA CONTAINER ---
    tags.div(
        ui.navset_hidden(
            ui.nav_panel("home",
                tags.h2("Visão Geral", class_="page-title"),
                tags.p("Bem-vindo ao Painel Principal.")
            ),
            ui.nav_panel("institucional",
                tags.h2("Institucional", class_="page-title"),
                tags.p("Informações sobre a reitoria.")
            ),
            ui.nav_panel("cursos",
                tags.h2("Cursos", class_="page-title"),
                tags.p("Lista de cursos.")
            ),
            ui.nav_panel("disciplinas",
                tags.h2("Disciplinas", class_="page-title"),
                tags.p("Grade curricular.")
            ),
            id="router_principal"
        ),
        class_="conteudo-spa"
    )
)

def server(input, output, session):
    estado_menu = reactive.Value(False)

    @reactive.effect
    @reactive.event(input.btn_sidebar_toggle)
    def _():
        estado_menu.set(not estado_menu.get())

    @reactive.effect
    @reactive.event(input.btn_fechar)
    def _():
        estado_menu.set(False)

    def navegar_para(page_id):
        ui.update_navs("router_principal", selected=page_id)
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

    @render.ui
    def css_controlador():
        if estado_menu.get():
            return tags.style(".menu-lateral { display: flex !important;} .overlay-escura { display: block !important; }")
        return None

app = App(app_ui, server)
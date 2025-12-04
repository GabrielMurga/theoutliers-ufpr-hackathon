from shiny import reactive, ui
import pandas as pd
from data import df_estrutura  

def setup_cascading_filters(input, ui_session):
    
    
    setores = sorted(df_estrutura['Setor'].dropna().unique().tolist())
    ui_session.update_select("disc_setor", choices=["Todos"] + setores)

    
    @reactive.effect
    def _():
        setor = input.disc_setor()
        if setor == "Todos" or not setor:
            opcoes = sorted(df_estrutura['Departamento'].dropna().unique().tolist())
        else:
            opcoes = sorted(df_estrutura[df_estrutura['Setor'] == setor]['Departamento'].dropna().unique().tolist())
        ui_session.update_select("disc_depto", choices=["Todos"] + opcoes)

    
    @reactive.effect
    def _():
        depto = input.disc_depto()
        mask = pd.Series([True] * len(df_estrutura))
        if input.disc_setor() != "Todos": mask &= (df_estrutura['Setor'] == input.disc_setor())
        
        if depto != "Todos":
            mask &= (df_estrutura['Departamento'] == depto)
            
        opcoes = sorted(df_estrutura[mask]['Curso'].dropna().unique().tolist())
        ui_session.update_select("disc_curso", choices=["Todos"] + opcoes)

    
    @reactive.effect
    def _():
        curso = input.disc_curso()
        mask = pd.Series([True] * len(df_estrutura))
        
        if input.disc_setor() != "Todos": mask &= (df_estrutura['Setor'] == input.disc_setor())
        if input.disc_depto() != "Todos": mask &= (df_estrutura['Departamento'] == input.disc_depto())
        
        if curso != "Todos":
            mask &= (df_estrutura['Curso'] == curso)
            
        opcoes = sorted(df_estrutura[mask]['Nome_Disciplina'].dropna().unique().tolist())
        ui_session.update_select("disc_disciplina", choices=["Todas"] + opcoes)

    
    @reactive.effect
    def _():
        
        mask = pd.Series([True] * len(df_estrutura))
        
        if input.disc_setor() != "Todos": mask &= (df_estrutura['Setor'] == input.disc_setor())
        if input.disc_depto() != "Todos": mask &= (df_estrutura['Departamento'] == input.disc_depto())
        if input.disc_curso() != "Todos": mask &= (df_estrutura['Curso'] == input.disc_curso())
        if input.disc_disciplina() != "Todas": mask &= (df_estrutura['Nome_Disciplina'] == input.disc_disciplina())
        
        opcoes = sorted(df_estrutura[mask]['Modalidade'].dropna().unique().tolist())
        ui_session.update_select("disc_modalidade", choices=["Todas"] + opcoes)
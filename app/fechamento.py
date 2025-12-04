import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# 1. CONEXÃO
CAMINHO_DB = "data/db/hackathon.duckdb"
con = duckdb.connect(CAMINHO_DB)
print("\n--- 3. GERANDO GRÁFICO DE TESTE ---")

# Vamos testar o JOIN mais importante: Fato + Curso
# Pergunta: "Quais os 10 cursos com mais respostas na avaliação?"

query = """
    SELECT 
        c.Curso,
        COUNT(*) as Total_Respostas
    FROM fAvaliacao f
    JOIN dCurso c ON f.Cod_Curso = c.Cod_Curso
    GROUP BY c.Curso
    ORDER BY Total_Respostas DESC
    LIMIT 10
"""

df_resultado = con.sql(query).df()

print("Dados recuperados:")
print(df_resultado)

# Plotando
plt.figure(figsize=(10, 6))
# Inverte o eixo Y para o maior ficar em cima no gráfico de barras horizontal
plt.barh(df_resultado['Curso'][::-1], df_resultado['Total_Respostas'][::-1], color='#003366')
plt.xlabel('Quantidade de Respostas')
plt.title('Top 10 Cursos com Mais Avaliações')
plt.tight_layout()

print("\nAbrindo gráfico...")
plt.show()

con.close()
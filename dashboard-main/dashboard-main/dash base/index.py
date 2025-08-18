import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd 
from supabase import create_client

# import from folders/theme changer
from app import *
from dash_bootstrap_templates import ThemeSwitchAIO


# ========== Styles ============ #
tab_card = {'height': '100%'}


main_config = {
    "hovermode": "x unified",
    "legend": {"yanchor":"top", 
                "y":0.9, 
                "xanchor":"left",
                "x":0.1,
                "title": {"text": None},
                "font" :{"color":"white"},
                "bgcolor": "rgba(0,0,0,0.5)"},
    "margin": {"l":10, "r":10, "t":10, "b":10}
}

config_graph={"displayModeBar": False, "showTips": False}

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY


# ========== Data ============= #
# Load data


import pandas as pd
from supabase import create_client

# Conexão com Supabase
url = "https://nilukfhilcvwqzzwrbmb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pbHVrZmhpbGN2d3F6endyYm1iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODk5NzgyNSwiZXhwIjoyMDY0NTczODI1fQ.TjwW4ztaD6CwFIDOK8aKm10VcgRvUZasMbst7Yiq3h0"
supabase = create_client(url, key)

# Carregamento das tabelas
americanas = supabase.table("AMERICANAS").select("*").execute()
del_tel = supabase.table("DELFIA-TELMEX").select("*").execute()
fus_cla_ms = supabase.table("FUST-CLARO-MS").select("*").execute()
fus_cla_rj = supabase.table("FUST-CLARO-RJ").select("*").execute()
mul_pro = supabase.table("MULT-PROJETOS").select("*").execute()

# Conversão em DataFrames
df_americanas = pd.DataFrame(americanas.data)
df_del_tel = pd.DataFrame(del_tel.data)
df_fus_cla_ms = pd.DataFrame(fus_cla_ms.data)
df_fus_cla_rj = pd.DataFrame(fus_cla_rj.data)
df_mul_pro = pd.DataFrame(mul_pro.data)

# Adiciona nome do cliente em cada DataFrame
df_americanas["Cliente"] = "AMERICANAS"
df_del_tel["Cliente"] = "DELFIA-TELMEX"
df_fus_cla_ms["Cliente"] = "FUST-CLARO-MS"
df_fus_cla_rj["Cliente"] = "FUST-CLARO-RJ"
df_mul_pro["Cliente"] = "MULT-PROJETOS"

# Junta todos os DataFrames
dfs = [df_americanas, df_del_tel, df_fus_cla_ms, df_fus_cla_rj, df_mul_pro]
df = pd.concat(dfs, ignore_index=True)

# Remove possíveis linhas duplicadas de cabeçalho que vieram como dados
df = df[df["Agendado"] != "Agendado"]

# Converte colunas numéricas para tipo adequado
colunas_numericas = [
    "Agendado", "agendado para hoje", "Em Campo", "finalizado",
    "Prospectar Técnico", "Valores", "pendente agendamento", "id"
]
for col in colunas_numericas:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Converte a coluna de data
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")











# =========  Layout  =========== #
app.layout = dbc.Container([
    dbc.Row([
        # COLUNA ESQUERDA (MENU)
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([html.Legend("Sales Analytics")], sm=8),
                        dbc.Col([
                            html.I(className='fa fa-balance-scale', style={'font-size': '300%'})
                        ], sm=4, align="center")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
                            html.Legend("Asimov Academy")
                        ])
                    ], style={'margin-top': '10px'}),
                    dbc.Row([
                        dbc.Button("Visite o Site", href="https://asimov.academy/", target="_blank")
                    ], style={'margin-top': '10px'}),

                    # ✅ FILTRO DE DATA COM DROPDOWN
                    dbc.Row([
                        html.Label("Filtrar por Data:", style={"margin-top": "10px", "font-weight": "bold", "color": "white"}),
                        dcc.Dropdown(
                            id='dropdown-date',
                            options=[
                                {"label": d.strftime("%d/%m/%Y"), "value": d.strftime("%Y-%m-%d")}
                                for d in sorted(df["Date"].dropna().unique())
                            ],
                            placeholder="Selecione uma data",
                            style={"margin-top": "5px"}
                        )
                    ])
                ])
            ], style={
                "backgroundColor": "#2C2F33",
                "color": "white",
                "border": "none"
            })
        ], sm=4, lg=2),

        # COLUNA DIREITA (KPI + GRÁFICOS)
        dbc.Col([
            # LINHA DE INDICADORES (KPI)
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("1", className="card-title text-center", style={"color": "white"}),
                    html.P("Pendente Agendamento", className="text-center", style={"color": "white"})
                ]), style={"backgroundColor": "#2C2F33"}), lg=2),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("2", className="card-title text-center", style={"color": "white"}),
                    html.P("Agendado", className="text-center", style={"color": "white"})
                ]), style={"backgroundColor": "#2C2F33"}), lg=2),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("3", className="card-title text-center", style={"color": "white"}),
                    html.P("Agendado Hoje", className="text-center", style={"color": "white"})
                ]), style={"backgroundColor": "#2C2F33"}), lg=2),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("4", className="card-title text-center", style={"color": "white"}),
                    html.P("Prospecção", className="text-center", style={"color": "white"})
                ]), style={"backgroundColor": "#2C2F33"}), lg=2),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("5", className="card-title text-center", style={"color": "white"}),
                    html.P("Em Campo", className="text-center", style={"color": "white"})
                ]), style={"backgroundColor": "#2C2F33"}), lg=2),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("6", className="card-title text-center", style={"color": "white"}),
                    html.P("Finalizado", className="text-center", style={"color": "white"})
                ]), style={"backgroundColor": "#2C2F33"}), lg=2),
            ], className="mb-4", style={"margin-top": "10px"}),

            # LINHA DE GRÁFICOS COM ALTURA TOTAL DA LINHA
            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='graph1', config=config_graph),
                            style={"height": "100%", "padding": 0, "margin": 0}
                        ),
                        style={"height": "100%", "transition": "all 0.5s ease-in-out"}
                    ), lg=2
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='graph2', config=config_graph),
                            style={"height": "100%", "padding": 0, "margin": 0}
                        ),
                        style={"height": "100%", "transition": "all 0.5s ease-in-out"}
                    ), lg=2
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='graph3', config=config_graph),
                            style={"height": "100%", "padding": 0, "margin": 0}
                        ),
                        style={"height": "100%", "transition": "all 0.5s ease-in-out"}
                    ), lg=2
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='graph4', config=config_graph),
                            style={"height": "100%", "padding": 0, "margin": 0}
                        ),
                        style={"height": "100%", "transition": "all 0.5s ease-in-out"}
                    ), lg=2
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='graph5', config=config_graph),
                            style={"height": "100%", "padding": 0, "margin": 0}
                        ),
                        style={"height": "100%", "transition": "all 0.5s ease-in-out"}
                    ), lg=2
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(id='graph6', config=config_graph),
                            style={"height": "100%", "padding": 0, "margin": 0}
                        ),
                        style={"height": "100%", "transition": "all 0.5s ease-in-out"}
                    ), lg=2
                ),
            ], style={"height": "85vh", "marginTop": "10px", "transition": "all 0.5s ease-in-out"})
        ], sm=8, lg=10)
    ])
], fluid=True, style={"height": "100vh", "overflow": "hidden"})




























# ========== Callbacks ========== #

@app.callback(
    Output('graph2', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("dropdown-date", "value")
)
def graph2(toggle, selected_date):
    template = template_theme1 if toggle else template_theme2

    # Cor de fundo de acordo com o modo claro/escuro
    paper_bg = "#FFFFFF" if toggle else "#121212"
    plot_bg = "#F5F5F5" if toggle else "#1E1E1E"

    df_filtrado = df.copy()
    if selected_date:
        df_filtrado = df_filtrado[df_filtrado["Date"] == selected_date]

    df_agendados = df_filtrado.groupby("Cliente")["Agendado"].sum().reset_index().sort_values(by="Agendado", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_agendados["Agendado"],
        y=df_agendados["Cliente"],
        orientation='h',
        marker=dict(color="#FFFF00"),
        text=df_agendados["Agendado"],
        textposition='inside',
        insidetextanchor="start",
        texttemplate="     %{text}",
        width=0.6
    ))

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono",
            size=28,
            color="#000000"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": "Agendados por Cliente",
            "x": 0.5,
            "y": 0.96,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=18, color="#FFFFFF", family="Arial Black")
        },
        template=template,
        height=1300,
        margin=dict(l=4, r=0, t=200, b=200),
        paper_bgcolor='#2C2F33',  # ✅ Fundo externo
        plot_bgcolor='#2C2F33',    # ✅ Fundo interno (barras)
        xaxis=dict(
            title=None,
            tickvals=[],
            showticklabels=False,
            tickfont=dict(
                size=16,
                color="#B38B6D",
                family="Arial Black"
            )
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=16,
                color="#C6C6C6",
                family="Arial Black"
            ),
            ticklabelposition='outside',
            ticklabelstandoff=15
),
        bargap=0.2,
        bargroupgap=0.05,
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    return fig


#pendente agendamento


@app.callback(
    Output('graph1', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("dropdown-date", "value")
)
def graph1(toggle, selected_date):
    template = template_theme1 if toggle else template_theme2

    # Cor de fundo de acordo com o modo claro/escuro
    paper_bg = "#FFFFFF" if toggle else "#121212"
    plot_bg = "#F5F5F5" if toggle else "#1E1E1E"

    df_filtrado = df.copy()
    if selected_date:
        df_filtrado = df_filtrado[df_filtrado["Date"] == selected_date]

    df_agendados = df_filtrado.groupby("Cliente")["pendente agendamento"].sum().reset_index().sort_values(by="pendente agendamento", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_agendados["pendente agendamento"],
        y=df_agendados["Cliente"],
        orientation='h',
        marker=dict(color="#FF073A"),
        text=df_agendados["pendente agendamento"],
        textposition='inside',
        insidetextanchor="start",
        texttemplate="     %{text}",
        width=0.6
    ))

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono",
            size=28,
            color="#000000"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": "Pendente Agendamento por Cliente",
            "x": 0.5,
            "y": 0.96,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=18, color="#FFFFFF", family="Arial Black")
        },
        template=template,
        height=1300,
        margin=dict(l=4, r=0, t=200, b=200),
        paper_bgcolor='#2C2F33',  # ✅ Fundo externo
        plot_bgcolor='#2C2F33',    # ✅ Fundo interno (barras)
        xaxis=dict(
            title=None,
            tickvals=[],
            showticklabels=False,
            tickfont=dict(
                size=16,
                color="#B38B6D",
                family="Arial Black"
            )
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=16,
                color="#C6C6C6",
                family="Arial Black"
            ),
            ticklabelposition='outside',
            ticklabelstandoff=15
),
        bargap=0.2,
        bargroupgap=0.05,
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    return fig


#Agendado Hoje

@app.callback(
    Output('graph3', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("dropdown-date", "value")
)
def graph3(toggle, selected_date):
    template = template_theme1 if toggle else template_theme2

    # Cor de fundo de acordo com o modo claro/escuro
    paper_bg = "#FFFFFF" if toggle else "#121212"
    plot_bg = "#F5F5F5" if toggle else "#1E1E1E"

    df_filtrado = df.copy()
    if selected_date:
        df_filtrado = df_filtrado[df_filtrado["Date"] == selected_date]

    df_agendados = df_filtrado.groupby("Cliente")["agendado para hoje"].sum().reset_index().sort_values(by="agendado para hoje", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_agendados["agendado para hoje"],
        y=df_agendados["Cliente"],
        orientation='h',
        marker=dict(color="#FF8C00"),
        text=df_agendados["agendado para hoje"],
        textposition='inside',
        insidetextanchor="start",
        texttemplate="     %{text}",
        width=0.6
    ))

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono",
            size=28,
            color="#000000"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": "agendado para hoje por Cliente",
            "x": 0.5,
            "y": 0.96,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=18, color="#FFFFFF", family="Arial Black")
        },
        template=template,
        height=1300,
        margin=dict(l=4, r=0, t=200, b=200),
        paper_bgcolor='#2C2F33',  # ✅ Fundo externo
        plot_bgcolor='#2C2F33',    # ✅ Fundo interno (barras)
        xaxis=dict(
            title=None,
            tickvals=[],
            showticklabels=False,
            tickfont=dict(
                size=16,
                color="#B38B6D",
                family="Arial Black"
            )
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=16,
                color="#C6C6C6",
                family="Arial Black"
            ),
            ticklabelposition='outside',
            ticklabelstandoff=15
),
        bargap=0.2,
        bargroupgap=0.05,
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    return fig

# prospectar técnico


@app.callback(
    Output('graph4', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("dropdown-date", "value")
)
def graph4(toggle, selected_date):
    template = template_theme1 if toggle else template_theme2

    # Cor de fundo de acordo com o modo claro/escuro
    paper_bg = "#FFFFFF" if toggle else "#121212"
    plot_bg = "#F5F5F5" if toggle else "#1E1E1E"

    df_filtrado = df.copy()
    if selected_date:
        df_filtrado = df_filtrado[df_filtrado["Date"] == selected_date]

    df_agendados = df_filtrado.groupby("Cliente")["Prospectar Técnico"].sum().reset_index().sort_values(by="Prospectar Técnico", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_agendados["Prospectar Técnico"],
        y=df_agendados["Cliente"],
        orientation='h',
        marker=dict(color="#FF00AA"),
        text=df_agendados["Prospectar Técnico"],
        textposition='inside',
        insidetextanchor="start",
        texttemplate="     %{text}",
        width=0.6
    ))

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono",
            size=28,
            color="#000000"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": "Prospectar Técnico por Cliente",
            "x": 0.5,
            "y": 0.96,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=18, color="#FFFFFF", family="Arial Black")
        },
        template=template,
        height=1300,
        margin=dict(l=4, r=0, t=200, b=200),
        paper_bgcolor='#2C2F33',  # ✅ Fundo externo
        plot_bgcolor='#2C2F33',    # ✅ Fundo interno (barras)
        xaxis=dict(
            title=None,
            tickvals=[],
            showticklabels=False,
            tickfont=dict(
                size=16,
                color="#B38B6D",
                family="Arial Black"
            )
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=16,
                color="#C6C6C6",
                family="Arial Black"
            ),
            ticklabelposition='outside',
            ticklabelstandoff=15
),
        bargap=0.2,
        bargroupgap=0.05,
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    return fig

#Em Campo

@app.callback(
    Output('graph5', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("dropdown-date", "value")
)
def graph5(toggle, selected_date):
    template = template_theme1 if toggle else template_theme2

    # Cor de fundo de acordo com o modo claro/escuro
    paper_bg = "#FFFFFF" if toggle else "#121212"
    plot_bg = "#F5F5F5" if toggle else "#1E1E1E"

    df_filtrado = df.copy()
    if selected_date:
        df_filtrado = df_filtrado[df_filtrado["Date"] == selected_date]

    df_agendados = df_filtrado.groupby("Cliente")["Em Campo"].sum().reset_index().sort_values(by="Em Campo", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_agendados["Em Campo"],
        y=df_agendados["Cliente"],
        orientation='h',
        marker=dict(color="#1E90FF"),
        text=df_agendados["Em Campo"],
        textposition='inside',
        insidetextanchor="start",
        texttemplate="     %{text}",
        width=0.6
    ))

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono",
            size=28,
            color="#000000"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": "Prospectar Técnico por Cliente",
            "x": 0.5,
            "y": 0.96,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=18, color="#FFFFFF", family="Arial Black")
        },
        template=template,
        height=1300,
        margin=dict(l=4, r=0, t=200, b=200),
        paper_bgcolor='#2C2F33',  # ✅ Fundo externo
        plot_bgcolor='#2C2F33',    # ✅ Fundo interno (barras)
        xaxis=dict(
            title=None,
            tickvals=[],
            showticklabels=False,
            tickfont=dict(
                size=16,
                color="#B38B6D",
                family="Arial Black"
            )
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=16,
                color="#C6C6C6",
                family="Arial Black"
            ),
            ticklabelposition='outside',
            ticklabelstandoff=15
),
        bargap=0.2,
        bargroupgap=0.05,
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    return fig

# Finalizado

@app.callback(
    Output('graph6', 'figure'),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    Input("dropdown-date", "value")
)
def graph6(toggle, selected_date):
    template = template_theme1 if toggle else template_theme2

    # Cor de fundo de acordo com o modo claro/escuro
    paper_bg = "#FFFFFF" if toggle else "#121212"
    plot_bg = "#F5F5F5" if toggle else "#1E1E1E"

    df_filtrado = df.copy()
    if selected_date:
        df_filtrado = df_filtrado[df_filtrado["Date"] == selected_date]

    df_agendados = df_filtrado.groupby("Cliente")["finalizado"].sum().reset_index().sort_values(by="finalizado", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_agendados["finalizado"],
        y=df_agendados["Cliente"],
        orientation='h',
        marker=dict(color="#00FF7F"),
        text=df_agendados["finalizado"],
        textposition='inside',
        insidetextanchor="start",
        texttemplate="     %{text}",
        width=0.6
    ))

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono",
            size=28,
            color="#000000"
        ),
        marker_line_width=0
    )

    fig.update_layout(
        title={
            "text": "Prospectar Técnico por Cliente",
            "x": 0.5,
            "y": 0.96,
            "xanchor": "center",
            "yanchor": "top",
            "font": dict(size=18, color="#FFFFFF", family="Arial Black")
        },
        template=template,
        height=1300,
        margin=dict(l=4, r=0, t=200, b=200),
        paper_bgcolor='#2C2F33',  # ✅ Fundo externo
        plot_bgcolor='#2C2F33',    # ✅ Fundo interno (barras)
        xaxis=dict(
            title=None,
            tickvals=[],
            showticklabels=False,
            tickfont=dict(
                size=16,
                color="#B38B6D",
                family="Arial Black"
            )
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                size=16,
                color="#C6C6C6",
                family="Arial Black"
            ),
            ticklabelposition='outside',
            ticklabelstandoff=15
),
        bargap=0.2,
        bargroupgap=0.05,
        transition=dict(
            duration=500,
            easing='cubic-in-out'
        )
    )

    return fig

















# Run server
if __name__ == '__main__':
    app.run(debug=False, port=3000)


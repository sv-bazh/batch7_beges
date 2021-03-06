import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input, State

from app import app
from utils.organization_chart import oc
from utils.odrive_handler import ov
from components.html_components import build_figure_container, build_card_indicateur


def get_vehicle_category(emission_per_km):
    if emission_per_km < 10:
        return "Emission très faible"
    if emission_per_km < 60:
        return "Emission faible"
    return "Emission haute"


def get_donut_by_entity_type(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    prestation_df = odrive_df.groupby(["Entité 3"])["Emissions (g/an)"].sum().reset_index()
    prestation_df.entities = list(set(odrive_df["Entité 3"]))
    fig = go.Figure(data=[go.Pie(labels=prestation_df["Entité 3"], values=prestation_df["Emissions (g/an)"], hole=0.3)])
    fig.update_layout(plot_bgcolor="white", template="plotly_white", margin={"t": 30, "r": 30, "l": 30})
    return fig


def get_plot_by_vehicle_type(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    print(filter_vehicle_type)
    print("odrive_df", odrive_df)
    odrive_df["categorie_emmission"] = odrive_df["CO2 (g/km)"].apply(get_vehicle_category)
    vehicles_df = odrive_df.groupby(["categorie_emmission"])["Immatriculation"].nunique().reset_index()
    fig = go.Figure(
        data=[go.Pie(labels=vehicles_df["categorie_emmission"], values=vehicles_df["Immatriculation"], hole=0.3)]
    )
    fig.update_layout(plot_bgcolor="white", template="plotly_white", margin={"t": 30, "r": 30, "l": 30})
    return fig


def get_histogram_by_entity_type(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    prestation_df = odrive_df.groupby(["Entité 3"])["km parcours par an"].sum().reset_index()
    prestation_df.entities = list(set(odrive_df["Entité 3"]))
    fig = go.Figure(data=[go.Bar(y=prestation_df["km parcours par an"], x=prestation_df["Entité 3"])])
    fig.update_layout(
        plot_bgcolor="white",
        template="plotly_white",
        margin={"t": 30, "r": 30, "l": 30},
        yaxis=dict(title_text="km parcours par an"),
    )
    return fig


def get_histogram_plot_by_vehicle(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    odrive_df["Immatriculation"] = (
        odrive_df["Immatriculation"].astype(str) + " (" + odrive_df["Marque"] + " - " + odrive_df["Modèle"] + ")"
    )
    vehicle_emissions = odrive_df.groupby(["Immatriculation"])
    vehicle_emissions = vehicle_emissions.agg(
        {"Moyenne KM par mois": pd.Series.mean, "Emissions (g/an)": pd.Series.mean}
    ).reset_index()
    vehicle_emissions["Moyenne KM par mois"] = vehicle_emissions["Moyenne KM par mois"]
    vehicle_emissions["Emissions (g/an)"] = vehicle_emissions["Emissions (g/an)"] / 12000
    vehicle_emissions = vehicle_emissions.nlargest(50, "Moyenne KM par mois")
    vehicle_emissions = vehicle_emissions.sort_values("Moyenne KM par mois", ascending=[0])
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(
        go.Bar(
            y=vehicle_emissions["Moyenne KM par mois"],
            x=vehicle_emissions["Immatriculation"],
            name="Distance parcourue (km/mois)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            y=vehicle_emissions["Emissions (g/an)"], x=vehicle_emissions["Immatriculation"], name="Emissions (kg/mois)"
        ),
        secondary_y=False,
    )
    fig.update_layout(plot_bgcolor="white", template="plotly_white", margin={"t": 30, "r": 30, "l": 30})
    fig.update_yaxes(title_text="Emissions (kg/mois), Distance par mois (km)", secondary_y=False)
    # fig.update_yaxes(title_text="CO2 (g/km)", secondary_y=True)
    fig.update_layout(barmode="group")
    return fig


def get_scatter_plot_by_vehicle_type(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    odrive_df["Marque"] = odrive_df["Marque"] + " " + odrive_df["Modèle"] + " (" + odrive_df["Motorisation"] + ")"
    vehicle_emissions = odrive_df.groupby(["Marque"])
    vehicle_emissions = vehicle_emissions.agg(
        {
            "Emissions (g/an)": pd.Series.mean,
            "km parcours par an": pd.Series.mean,
            "Motorisation": lambda x: x.value_counts().index[0],
            "Immatriculation": pd.Series.nunique,
        }
    ).reset_index()
    vehicle_emissions["Marque"] = (
        vehicle_emissions["Marque"] + " (" + vehicle_emissions["Immatriculation"].astype(str) + " véhicule(s))"
    )
    vehicle_emissions["Immatriculation"] = vehicle_emissions["Immatriculation"].add(5)
    fig = go.Figure(
        data=[
            go.Scatter(
                x=vehicle_emissions["km parcours par an"],
                y=vehicle_emissions["Emissions (g/an)"],
                mode="markers",
                marker_size=vehicle_emissions["Immatriculation"],
                text=vehicle_emissions["Marque"],
            )
        ]
    )  # color=vehicle_emissions["Motorisation"],
    fig.update_layout(
        plot_bgcolor="white",
        template="plotly_white",
        margin={"t": 30, "r": 30, "l": 30},
        xaxis=dict(title_text="Moyenne de distance parcourue par an (km)"),
        yaxis=dict(title_text="Moyenne des emissions par an (g)"),
    )
    return fig


def get_test_graph_odrive(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    prestation_df = odrive_df.groupby(["Entité 3"])["km parcours par an"].sum().reset_index()
    prestation_df.entities = list(set(odrive_df["Entité 3"]))
    fig = go.Figure(data=[go.Bar(y=prestation_df["km parcours par an"], x=prestation_df["Entité 3"])])
    fig.update_layout(
        plot_bgcolor="white",
        template="plotly_white",
        margin={"t": 30, "r": 30, "l": 30},
        yaxis=dict(title_text="km parcours par an"),
    )
    return fig


def get_fleet_vehicle(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    count_vehicles = odrive_df["Immatriculation"].nunique()
    return round(count_vehicles, 2)


def get_total_emisions_vehicles(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    count_emissions = odrive_df["Emissions (g/an)"].sum()
    return round(count_emissions / 1000, 2)


def get_kilometers_total_odive(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    count_kilometers = odrive_df["km parcours par an"].sum()
    return round(count_kilometers, 2)


def get_montly_kilometer_odrive(code_structure=None, filter_vehicle_type=None):
    odrive_df = ov.get_structure_data(code_structure, filter_vehicle_type)
    count_kilometers_per_month_per_vehicle = (odrive_df["km parcours par an"].sum() / 12) / odrive_df[
        "Immatriculation"
    ].nunique()
    return round(count_kilometers_per_month_per_vehicle, 2)


def get_dropdown_list_vehicle_motor():
    odrive_df = ov.get_structure_data()
    motors = list(set(odrive_df["Motorisation"]))
    options = []
    value = []
    for m in motors:
        if m is not None and m is not np.nan:
            options.append({"label": m, "value": m})
            value.append(m)
    return dcc.Checklist(id="select_odrive_vehicle_type", options=options, value=value, labelStyle={"display": "block"})


cards = dbc.CardDeck(
    [
        build_card_indicateur("Emissions en CO2 par an (kg)", "0", "total_emissions_odrive"),
        build_card_indicateur("Nombre de véhicules", "0", "fleet_vehicle_number_odrive"),
        build_card_indicateur("Distance parcourue par an (km)", "0", "kilometers_total_odrive"),
        build_card_indicateur("Distance par mois par véhicule (km)", "0", "montly_kilometer_odrive"),
    ]
)


layout = html.Div(
    [
        # Cards row
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.B("", id="selected-odrive-vehicle_type"),
                        dbc.Jumbotron(
                            [
                                html.P(
                                    "Les émissions annuelles sont obtenues en multipliant le facteur d'émission des véhicules par le nombre de kilomètres qu'ils parcourent en un an"
                                ),
                                html.P(dbc.Button("En savoir plus", color="primary", href="/methodologie")),
                            ]
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H3("Filtres"),
                                    html.Br(),
                                    dbc.FormGroup(
                                        [
                                            dbc.Label("Selectionner le type de motorisation du véhicule"),
                                            get_dropdown_list_vehicle_motor(),
                                        ]
                                    ),
                                ]
                            ),
                            className="pretty_container",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        cards,
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        build_figure_container(
                                            title="Répartition des émissions par direction", id="donut-by-entity"
                                        )
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        build_figure_container(
                                            title="Répartition des km parcours par direction", id="histogram-by-entity"
                                        )
                                    ],
                                    width=6,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        build_figure_container(
                                            title="Répartition des émissions et kilomètres par marque et modèle",
                                            id="scatter_plot_by_vehicle_type",
                                            footer="Deux types de véhicule dans le même axe vertical ont la même utilisation, mais des emissions différentes, privilégiez l'utilisation ou l'achat de véhicules dans la partie basse du graphique ..",
                                        )
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        build_figure_container(
                                            title="Répartition des émissions par type de véhicule",
                                            id="plot_by_vehicle_type",
                                        )
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        build_figure_container(
                                            title="Répartition des émissions par véhicule",
                                            id="histogram_plot_by_vehicle",
                                        )
                                    ],
                                    width=12,
                                ),
                            ]
                        ),
                    ],
                    width=9,
                ),
            ]
        )
    ],
    id="div-data-odrive",
)


@app.callback(
    Output("donut-by-entity", "figure"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_donut_by_prestation(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_donut_by_entity_type(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("histogram-by-entity", "figure"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_histogram_by_prestation(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_histogram_by_entity_type(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("scatter_plot_by_vehicle_type", "figure"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_scatter_plot_by_vehicle(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_scatter_plot_by_vehicle_type(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("histogram_plot_by_vehicle", "figure"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_histogram_plot_by_vehicle(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_histogram_plot_by_vehicle(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("plot_by_vehicle_type", "figure"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_plot_by_vehicle_type(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    print(service)
    return get_plot_by_vehicle_type(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("fleet_vehicle_number_odrive", "children"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_fleet_vehicle(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_fleet_vehicle(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("total_emissions_odrive", "children"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_total_emissions_vehicles(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_total_emisions_vehicles(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("kilometers_total_odrive", "children"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_kilometers_total_odive(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_kilometers_total_odive(service.code_odrive, filter_vehicle_type)


@app.callback(
    Output("montly_kilometer_odrive", "children"),
    [Input("dashboard-selected-entity", "children"), Input("select_odrive_vehicle_type", "value")],
)
def update_montly_kilometer_odrive(selected_entity, filter_vehicle_type):
    service = oc.get_entity_by_id(selected_entity)
    return get_montly_kilometer_odrive(service.code_odrive, filter_vehicle_type)

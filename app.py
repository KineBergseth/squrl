import pandas as pd
import base64
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import Namespace

# import data into dataframe and remove useless columns
census = pd.read_csv('squirrel_data.csv')
squirrel_census = pd.DataFrame(census)
squirrel_census.drop(['Hectare', 'Above Ground Sighter Measurement', 'Hectare Squirrel Number',
                      'Combination of Primary and Highlight Color', 'Color notes', 'Specific Location',
                      'Other Activities', 'Other Interactions', 'Lat/Long'], axis=1, inplace=True)
squirrel_census.rename(columns={"X": "lon", "Y": "lat"}, inplace=True)

# clean up data, replace missing data with the value unknown
squirrel_census["Age"].replace("?", "Unknown", inplace=True)
squirrel_census["Age"].fillna("Unknown", inplace=True)
squirrel_census["Primary Fur Color"].fillna("Unknown", inplace=True)
squirrel_census["Highlight Fur Color"].fillna("Unknown", inplace=True)
squirrel_census["Location"].fillna("Unknown", inplace=True)

# dropping missing values to avoid errors, drop rows where at least one element is missing
squirrel_census.dropna(inplace=True)

# convert dataframe to a list of dictionaries [{column -> value}, … , {column -> value}]
squirrel_data = squirrel_census.to_dict('records')


# Encode the local sound files
# https://life.hawkeoptics.com/woodland-stalking/
kuk_sound = 'assets/squirrel-kuk.wav'
quaa_sound = 'assets/squirrel-quaa.wav'
moan_sound = 'assets/squirrel-moan.mp3'

encoded_kuk_sound = base64.b64encode(open(kuk_sound, 'rb').read())
encoded_quaa_sound = base64.b64encode(open(quaa_sound, 'rb').read())
encoded_moan_sound = base64.b64encode(open(moan_sound, 'rb').read())

ns = Namespace("myNamespace", "mySubNamespace")


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Find Lat Long center to set map center
lat_center = sum(squirrel_census['lat']) / len(squirrel_census['lat'])
long_center = sum(squirrel_census['lon']) / len(squirrel_census['lon'])

# get map style
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

app.layout = html.Div(
    children=[

        # HEADER
        html.Div(
            children=[
                html.Img(src='assets/squ2.png', id='header-logo'),
                html.H1('SQURL', id='header-text'),
            ],
            className="header",
        ),

        # MAP
        html.Div(
            children=
            [
                dl.Map(center=[lat_center, long_center], zoom=15, children=[
                    dl.TileLayer(url=url, attribution=attribution), dl.Marker(position=(56, 10)),
                    dl.GeoJSON(data=dlx.geojson_to_geobuf(dlx.dicts_to_geojson(squirrel_data)),
                               id="unique-squirrel-id", format="geobuf", options=dict(pointToLayer=ns("pointToLayer"))),
                ], style={'width': '100%', 'height': '75vh', "display": "block"}, id="map"),
            ],
            className="squirrel-map",
        ),
        # SQUIRREL INFO
        html.Div(id="squirrel-facts"),
        html.Div(id="placeholder1", style={"display": "none"}),
        html.Div(id="placeholder2", style={"display": "none"}),
        html.Div(id="placeholder3", style={"display": "none"}),

    ],
    className="main"
)


@app.callback(Output("squirrel-facts", "children"), [Input("unique-squirrel-id", "click_feature")])
def squirrel_click(feature):
    if feature is not None:
        facts = feature['properties']
        primary_color = ""
        highlight_color = ""
        age_image = ""
        location_image = ""
        if facts['Age'] == 'Adult':
            age_image = "assets/squ2.png"
        elif facts['Age'] == 'Juvenile':
            age_image = "assets/squ1.jpg"
        else:
            age_image = "assets/squ22.png"

        if facts['Location'] == 'Ground Plane':
            location_image = "assets/bush.png"
        elif facts['Location'] == 'Above Ground':
            location_image = "assets/tree2.png"
        else:
            location_image = "assets/squirrel.png"

        return html.Div(children=[
            html.Div(html.P(f"Squirrel ID: {facts['Unique Squirrel ID']}"), className="div1"),
            html.Div([html.P(facts['Primary Fur Color']), html.P("color")], className="div2"),
            html.Div(html.Img(src='assets/squ2.png', className='header-2'), className="div3"),
            html.Div([html.P(facts['Highlight Fur Color']), html.P("color")], className="div4"),
            html.Div(html.Img(src='assets/squ2.png', className='header-2'), className="div5"),
            html.Div([html.P("POS"), html.P("lat"), html.P("long")], className="div6"),
            html.Div([html.P(""), html.P(''), html.P("")], className="div7"),
            html.Div(html.P("28th october"), className="div8"),
            html.Div(html.P(facts['Shift']), className="div9"),
            html.Div([html.P("Running"), html.Img(src='assets/squ2.png', className='header-2')],
                     className="div10"),
            html.Div([html.P("Chasing"), html.Img(src='assets/squ2.png', className='header-2')],
                     className="div11"),
            html.Div([html.P("Climbing"), html.Img(src='assets/squ2.png', className='header-2')],
                     className="div12"),
            html.Div([html.P("Eating"), html.Img(src='assets/squ2.png', className='header-2')],
                     className="div13"),
            html.Div([html.P("Foraging"), html.Img(src='assets/squ2.png', className='header-2')],
                     className="div14"),
            html.Div([html.P("Kuks"), html.Img(src='assets/squ2.png', className='header-2', id='sound-kuks')],
                     className="div15"),
            html.Div([html.P("Quaas"), html.Img(src='assets/squ2.png', className='header-2', id='sound-quaas')],
                     className="div16"),
            html.Div([html.P("Moans"), html.Img(src='assets/squ2.png', className='header-2', id='sound-moans')],
                     className="div17"),
            html.Div([html.P(f"Age: {facts['Age']}"), html.Img(src=age_image, className='header-22')],
                     className="div18"),
            html.Div([html.P(f"Elevation: {facts['Location']}"),
                      html.Img(src=location_image, className='header-22')], className="div19"),
        ], className='parent', )


@app.callback(Output("placeholder1", "children"),
              [Input("sound-kuks", "n_clicks")],
              )
def play(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 != 0:
        return html.Audio(src='data:audio/mpeg;base64,{}'.format(encoded_kuk_sound.decode()),
                          controls=False,
                          autoPlay=True,
                          )


@app.callback(Output("placeholder2", "children"),
              [Input("sound-quaas", "n_clicks")],
              )
def play(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 != 0:
        return html.Audio(src='data:audio/mpeg;base64,{}'.format(encoded_quaa_sound.decode()),
                          controls=False,
                          autoPlay=True,
                          )


@app.callback(Output("placeholder3", "children"),
              [Input("sound-moans", "n_clicks")],
              )
def play(n_clicks):
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 != 0:
        return html.Audio(src='data:audio/mpeg;base64,{}'.format(encoded_moan_sound.decode()),
                          controls=False,
                          autoPlay=True,
                          )


if __name__ == '__main__':
    app.run_server(debug=True)

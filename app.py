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

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'SQURL'
server = app.server

# Find Lat Long center to set map center
lat_center = sum(squirrel_census['lat']) / len(squirrel_census['lat'])
long_center = sum(squirrel_census['lon']) / len(squirrel_census['lon'])

data = dlx.geojson_to_geobuf(dlx.dicts_to_geojson(squirrel_data))

ns = Namespace("myNamespace", "mySubNamespace")
nz = Namespace("dlx", "scatter")

# get map style
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

app.layout = html.Div(
    children=[

        # HEADER
        html.Div(
            children=[
                html.H1('SQURL', id='header-text'),
            ],
            className="header",
        ),

        # MAP
        html.Div(
            children=
            [
                dl.Map(center=[lat_center, long_center], zoom=15, children=[
                    dl.TileLayer(url=url, attribution=attribution),
                    dl.GeoJSON(data=data, id="unique-squirrel-id", format="geobuf", cluster=True,
                               zoomToBoundsOnClick=True, superClusterOptions={"radius": 50},
                               options=dict(pointToLayer=ns("pointToLayer"))),
                ], style={'width': '100%', 'height': '75vh', "display": "block"}, id="map"),
            ],
            className="squirrel-map",
        ),
        # SQUIRREL INFO
        html.Div(id="squirrel-facts"),

        # SOUNDS
        html.Div(
            children=
            [
                html.Div([html.P("Kuks"), html.Img(src='assets/squ2.png', className='header-2', id='sound-kuks')],
                         className="k"),
                html.Div([html.P("q"), html.Img(src='assets/squ2.png', className='header-2', id='sound-quaas')],
                         className="div16"),
                html.Div([html.P("Moans"), html.Img(src='assets/squ2.png', className='header-2', id='sound-moans')],
                         className="m"),
            ],
            className="squirrel-sounds",
        ),
        # invisible sound containers
        html.Div(id="placeholder1", style={"display": "none"}),
        html.Div(id="placeholder2", style={"display": "none"}),
        html.Div(id="placeholder3", style={"display": "none"}),

    ],
    className="main"
)


# print squirrel fact table when a marker is clicked
@app.callback(Output("squirrel-facts", "children"), [Input("unique-squirrel-id", "click_feature")])
def squirrel_click(feature):
    # user must have clicker on a squirrel marker
    if (feature is not None) and not (feature['properties']['cluster']):
        facts = feature['properties']
        # choose image paths based on the fact that applies to a certain squirrel
        primary_color = ""
        highlight_color = ""
        location_image = ""

        if facts['Age'] == 'Adult':
            age_image = "assets/age_adult.png"
        elif facts['Age'] == 'Juvenile':
            age_image = "assets/age_juvenile.png"
        else:
            age_image = "assets/age_unknown.png"

        if facts['Location'] == 'Ground Plane':
            location_image = "assets/ground.png"
        elif facts['Location'] == 'Above Ground':
            location_image = "assets/tree.png"
        else:
            location_image = "assets/tree2.png"

        # choose image based on action. colored images means that the squirrel does that activity
        if facts['Running']:
            running_image = "assets/running_true.png"
        else:
            running_image = "assets/running_false.png"

        if facts['Chasing']:
            chasing_image = "assets/chasing_true.png"
        else:
            chasing_image = "assets/chasing_false.png"

        if facts['Climbing']:
            climbing_image = "assets/climbing_true.png"
        else:
            climbing_image = "assets/climbing_false.png"

        if facts['Eating']:
            eating_image = "assets/eating_true.png"
        else:
            eating_image = "assets/eating_false.png"

        if facts['Foraging']:
            foraging_image = "assets/foraging_true.png"
        else:
            foraging_image = "assets/foraging_false.png"

        return html.Div(children=[
            html.Div([html.P("PRIMARY COLOR"), html.P(facts['Primary Fur Color'])], className="div1"),
            html.Div(html.Img(src='https://www.transparentpng.com/thumb/circle/0JKSf2-circle-icon.png',
                              className='color_circle'), className="div2"),
            html.Div([html.P("HIGHLIGHT COLOR"), html.P(facts['Highlight Fur Color'])], className="div3"),
            html.Div(html.Img(src='https://www.transparentpng.com/thumb/circle/0JKSf2-circle-icon.png',
                              className='color_circle'), className="div4"),
            html.Div([html.P("POS"), html.P("lat"), html.P("long")], className="div5"),
            html.Div([html.P(f"Age: {facts['Age']}"), html.Img(src=age_image, className='header-22')],
                     className="div6"),
            html.Div([html.P(f"Elevation: {facts['Location']}"),
                      html.Img(src=location_image, className='header-222')], className="div7"),
            html.Div([html.Img(src=running_image, className='header-2'), html.P("Running")],
                     className="div8"),
            html.Div([html.Img(src=chasing_image, className='header-2'), html.P("Chasing")],
                     className="div9"),
            html.Div([html.Img(src=climbing_image, className='header-2'), html.P("Climbing")],
                     className="div10"),
            html.Div([html.Img(src=eating_image, className='header-2'), html.P("Eating")],
                     className="div11"),
            html.Div([html.Img(src=foraging_image, className='header-2'), html.P("Foraging")],
                     className="div12"),
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

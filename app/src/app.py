import dash
import dash_bootstrap_components as dbc
import flask
import io
from flask import url_for

import utils

external_stylesheets = [dbc.themes.BOOTSTRAP]  # ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Beges"
# The underlying flask server

app.config.suppress_callback_exceptions = True


@app.server.route("/data/exportRaw")
def download_raw_excel():
    """Define route for exporting raw data"""
    service = flask.request.args.get("service")
    # TODO: Include some security checks on passed value
    de = utils.DataExport(service)
    strIO = de.get_file_as_bytes()
    return flask.send_file(
        strIO,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        attachment_filename="export_beges.xlsx",
        as_attachment=True,
        cache_timeout=0,
    )  # TODO: Remove cache timeout

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start/<start>/end/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precip data for the last year."""
    # Query date and precip data
    precip_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    
    session.close()

    # Create a dictionary from the precip_results tuple list
    #precip_dict = {precip_results[i]: float(precip_results[i+1]) for i in range(0, len(precip_results),2)}
    # Create a dictionary from the row data and append to a list list of last years precip
    last_year_precip = []
    for date, prcp in precip_results:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        last_year_precip.append(precip_dict)

    # Convert list of tuples into normal list
    # = list(np.ravel(results))

    return jsonify(last_year_precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    stations = session.query(Station.station).all()
    
    session.close()

    #convert list of lists into single list
    stations_one_list = [item for elem in stations for item in elem]

    # Convert list of tuples into normal list
    #list(np.ravel(stations))

    return jsonify(stations_one_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temp data for the last year."""
    # Query date and precip data
    last_year_temp_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').\
                                        filter(Measurement.station == 'USC00519281').all()
    
    session.close()

    # Create a dictionary from the temp_results tuple list
    #precip_dict = {precip_results[i]: float(precip_results[i+1]) for i in range(0, len(precip_results),2)}
    # Create a dictionary from the row data and append to a list of last years temperatures
    last_year_temps = []
    for date, tobs in last_year_temp_results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        last_year_temps.append(temp_dict)

    # Convert list of tuples into normal list
    # = list(np.ravel(results))

    return jsonify(last_year_temps)

@app.route("/api/v1.0/start/<start_date>")
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    import sys
    print(start_date, file=sys.stderr)

    """Return a list of temp data for date passed ."""
    # Query temp date for dates from start date forward
    s_temp_results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).\
        group_by(Measurement.date).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list list of last years precip
    temp_data_start = []
    for a, b, c, d in s_temp_results:
        temp_start_dict = {}
        temp_start_dict["Date:"] = a
        temp_start_dict["Min Temp:"] = b
        temp_start_dict["Average Temp:"] = c
        temp_start_dict["Max Temp:"] = d

        temp_data_start.append(temp_start_dict)

    #convert list of lists into single list
    #s_temps_one_list = [item for elem in s_temp_results for item in elem]

    return jsonify(temp_data_start)
    
@app.route("/api/v1.0/start/<start>/end/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temp data for date passed ."""
    # Query temp date for dates from start date forward
    se_temp_results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
        group_by(Measurement.date).all()
    
    #session.close()

    # Create a dictionary from the row data and append to a list list of last years precip
    temp_start_end = []
    for a, b, c, d in se_temp_results:
        temp_se_dict = {}
        temp_se_dict["Date:"] = a
        temp_se_dict["Min Temp:"] = b
        temp_se_dict["Average Temp:"] = c
        temp_se_dict["Max Temp:"] = d
        temp_start_end.append(temp_se_dict)

    return jsonify(temp_start_end)

if __name__ == "__main__":
    app.run(debug=True)

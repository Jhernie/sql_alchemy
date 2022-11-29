#import dependencies
import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify 
import datetime
from dateutil.relativedelta import relativedelta

#build engine and map keys
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#build app
app = Flask(__name__)

#build routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("/api/v1.0/precipitation - route hit")
    
    session = Session(engine)

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    pcrp_results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    precip = []
    for date, pcrp in pcrp_results:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = pcrp
        precip.append(precip_dict)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    print("/api/v1.0/stations - route hit")

    session = Session(engine)

    selection = [Measurement.station, Station.name]
    station_results = session.query(*selection).all()

    session.close()

    station_list = []
    for station, name in station_results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_list.append(station_dict)
    return jsonify(station_list)
        
@app.route("/api/v1.0/temperature")
def temperature():
    print("/api/v1.0/temp - route hit")

    session = Session(engine)

    # datetime in string format, format, convert from string format to datetime format
    input = '2017-08-23'
    format = '%Y-%m-%d'
    converted_date = datetime.datetime.strptime(input, format)

    #create 'year ago' variable
    year_ago = datetime.date(2017,8,23) - relativedelta(years=1)

    selection = [Measurement.date, Measurement.tobs]
    temp_results = session.query(*selection).filter(Measurement.station == "USC00519281", Measurement.date <= converted_date.date(), Measurement.date >= year_ago).all()

    session.close()

    temp_list = []
    for date, tobs in temp_results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        temp_list.append(temp_dict)
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start(start):
    print("/api/v1.0/<start> - route hit")

    session = Session(engine)

    # datetime in string format, format, convert from string format to datetime format
    format = '%Y-%m-%d'

    start_date = datetime.datetime.strptime(start, format)
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_temp_results = session.query(*selection).filter(Measurement.date >= start_date).all()

    session.close()

    start_list = list(np.ravel(start_temp_results))

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def end(start,end):
    print("/api/v1.0/<start>/<end> - route hit")
    
    session = Session(engine)

    # datetime in string format, format, convert from string format to datetime format
    format = '%Y-%m-%d'

    start_date = datetime.datetime.strptime(start, format)
    end_date = datetime.datetime.strptime(start, format)
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_end_temp_results = session.query(*selection).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    session.close()

    start_list = list(np.ravel(start_end_temp_results))

    return jsonify(start_list)

if __name__ == '__main__':
    app.run(debug=True)


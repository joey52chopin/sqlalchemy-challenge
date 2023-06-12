# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify
from sqlalchemy import func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#====================================================================================================
# Create an instance of Flask
app = Flask(__name__)

# Define the homepage route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/mm-dd-yyyy<br/>"
        f"/api/v1.0/mm-dd-yyyy/mm-dd-yyyy"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Calculate the date one year from the last date in the data set
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    session.close()
    
    # Convert the query results to a dictionary
    prcp_data = {date: prcp for date, prcp in results}

    return jsonify(prcp_data)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query the list of stations
    station_results = session.query(Station.station, Station.name).all()

    session.close()

    # Create a list of dictionaries for each station
    station_list = []
    for station, name in station_results:
        station_dict = {"Station": station, "Name": name}
        station_list.append(station_dict)

    return jsonify(station_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Calculate the date one year from the last date in the data set
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for the most active station
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == "USC00519281").all()

    session.close()

    # Create a list of dictionaries for each temperature observation
    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict = {"Date": date, "Temperature": tobs}
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

# Define the start and start-end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    session = Session(engine)

    # Query the minimum, average, and maximum temperature based on the specified date range
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(
            Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        
    else:
        results = session.query(
            func.min(Measurement.tobs), func.avg(
                Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
     
    temps = list(np.ravel(results))

    session.close
    return jsonify(temps=temps)



if __name__ == '__main__':
    app.run(debug=True)

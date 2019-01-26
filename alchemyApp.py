import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt
from datetime import timedelta 

from flask import Flask, jsonify
'''
 sqlite:///relative/path/to/file.db
 sqlite:////absolute/path/to/file.db
''' 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station= Base.classes.station
session = Session(engine)

# FLASK
app = Flask(__name__)


#$ routes
@app.route("/")
def welcome():
    return (f"<h2>Welcome to hawaii weather data API!<h2>")

# `/api/v1.0/precipitation`
# * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
# * Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precip():
    results = session.query(Measurement).all()
    all_measurements=[]
    for mea in results:
        mea_dict={}
        mea_dict={mea.date:mea.prcp}
        all_measurements.append(mea_dict)
    return jsonify(all_measurements)

# * `/api/v1.0/stations`
# * Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    stations=list(np.ravel(results))
    return jsonify(stations)


# * `/api/v1.0/tobs`
#  * query for the dates and temperature observations from a year from the last data point.
#  * Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobbs():
    # Calculate the date 1 year ago from the last data point in the database
    lastDateQ=session.query(Measurement).order_by(desc('date')).limit(1).all()[0]
    lastDate = dt.datetime.strptime(lastDateQ.date, "%Y-%m-%d").date()
    firstDate= lastDate - timedelta(days=365)
    firstDateStr=firstDate.strftime('%Y-%m-%d') 
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.tobs).filter(Measurement.date > firstDateStr)
    all_tobs= []
    for r in results:
        rd={}
        rd["temp"]=r.tobs    
        all_tobs.append(rd)
    #selectDates=list(np.ravel(results))
    return jsonify(all_tobs)

#* `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#* When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
OPTIONAL=object() 
def daily_normals(sdate,*args): 
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)] 
    if len(args)==0:
        return session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= sdate).all() 
    else:
        print("edata")
        return session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= sdate).filter(func.strftime("%Y-%m-%d", Measurement.date) <= args[0]).all() 

@app.route("/api/v1.0/<start>")
def startd(start):
    #* When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    dn=daily_normals(start)
    dnd={'min':dn[0][0], 'avg':dn[0][1], 'max':dn[0][2]}
    return jsonify(dnd)

@app.route("/api/v1.0/<start>/<end>")
def endd(start,end):
    dn=daily_normals(start,end)
    dnd={'min':dn[0][0], 'avg':dn[0][1], 'max':dn[0][2]}
    return jsonify(dnd)

if __name__ == '__main__':
    app.run(debug=True)

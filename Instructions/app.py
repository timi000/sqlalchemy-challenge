import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt 

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station=Base.classes.station 
Measurement=Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2011-05-01<br/>"
        f"/api/v1.0/2011-05-01/2017-05-01"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    Result=session.query(Measurement.date,Measurement.prcp)
    session.close()

   
    # Query all passengers
    Res=Result.all()
    datet=[]
    prp=[]
    for row in Res:
        datet.append(row[0])
        prp.append(row[1])
    new_dict=dict(zip(datet,prp))  
    return jsonify(new_dict)
@app.route("/api/v1.0/stations")
def station ():
    session = Session(engine)
    result=session.query(Station.name,Station.station)
    session.close()

    
    all_stations= []
    for name, station in result:
        stations_dict = {}
        stations_dict["name"] = name
        stations_dict["Station Id"] = station
        all_stations.append(stations_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    station_high=session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    Last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    #s = time.strftime(f'{Last_date}', time.gmtime(time.time()))
    a_date=dt.datetime.strptime(Last_date,"%Y-%m-%d").date()
    days=dt.timedelta(365)
    end_date=a_date-days
    end_d= '{:%Y-%m-%d}'.format(end_date)
    Stat_results=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date.between(f'{end_d}', f'{Last_date}')).\
    filter(Measurement.station==station_high)
    session.close()
    
    all_tobs = []
    for date, tobs in Stat_results:
        tobs_dict ={}
        tobs_dict["date"]=date
        tobs_dict["tobs"]=tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    session=Session(engine)
    s_result=session.query(Measurement.date,func.avg(Measurement.tobs), func.max(Measurement.tobs),func.min(Measurement.tobs) ).\
        filter(Measurement.date >= start)
    session.close()
    start_list = []
    for date, avg, max, min in s_result: 
        start_dict={}
        start_dict["Date"]=date
        start_dict["TAVG"]=avg
        start_dict["TMAX"]=max
        start_dict["TMIN"]=min
        start_list.append(start_dict)

  
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session=Session(engine)
    se_result=session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs),func.min(Measurement.tobs) ).\
        filter(Measurement.date.between (start,end))
    session.close()
    end_list = []
    for  avg, max, min in se_result: 
        end_dict={}
        end_dict["TAVG"]=avg
        end_dict["TMAX"]=max
        end_dict["TMIN"]=min
        end_list.append(end_dict)

  
    return jsonify(end_list)

if __name__ == '__main__':
    app.run(debug=True)
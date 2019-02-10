import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)

from flask import Flask, jsonify
app=Flask(__name__)
@app.route("/")
def welcome():
    return "Hi"
    
#Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
    session=Session()
    prcp_query = session.query(Measurement.date, Measurement.prcp)\
    .filter(Measurement.date >= '2017-01-01').all()
    prcp_query_dict = dict(prcp_query)
    
    print("Results for Precipitation")
    session.close()
    return jsonify(prcp_query_dict) 
    

#Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    session=Session()
    station = session.query(Station.name).all()
    print("Station List:")   
    for i in station:
        print (i)
    session.close()
    return jsonify(station)
    

# Calculate the date 1 year ago from the last data point in the database

#Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session=Session()
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    lastyear_date = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    tob_query = session.query(Measurement.tobs).\
    filter(Measurement.date >= lastyear_date).\
    order_by(Measurement.date).all()
    print("Temperature Of Previous Year")
    session.close()
    return jsonify(tob_query)
    

#Return a JSON list of the minimum temperature, the average temperature 
#and the max temperature for a given start or start-end range.

@app.route('/api/v1.0/station/<start>')
def temp_start(start):
    session=Session()
    temp_start_query = session.query(Station.id,
                                     Station.station,
                                     func.min(Measurement.tobs),
                                     func.max(Measurement.tobs),
                                     func.avg(Measurement.tobs)).\
                                     filter(Measurement.station == Station.station).\
                                     filter(Measurement.date >= start).\
                                     group_by(Station.station).\
                                     order_by(Station.id).all()
    print(f"Temperature for Stations with Start ({start}) Date")
    for row in temp_start_query:
        print()
        print(row)
    session.close()
    return jsonify(temp_start_query)

@app.route('/api/v1.0/station/<start>/<end>')
def temp_start_end(start,end):
    session=Session()
    temp_start_end_query = session.query(Station.id,
                                         Station.station,
                                         func.min(Measurement.tobs),
                                         func.max(Measurement.tobs),
                                         func.avg(Measurement.tobs)).\
                                         filter(Measurement.station == Station.station).\
                                         filter(Measurement.date <= end).\
                                         filter(Measurement.date >= start).\
                                         group_by(Station.station).\
                                         order_by(Station.id).all()
                        
    print(f"Query Temps for Stations with Start ({start}) and End ({end}) Date")
    for row in temp_start_end_query:
        print(row)
    session.close()
    return jsonify(temp_start_end_query)
    

if __name__ == '__main__':
    app.run(debug=True)

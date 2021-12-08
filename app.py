############################################
## Work in progress - extraneous comments ##
## will be removed soon                   ##
############################################

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

from sqlalchemy.orm import backref

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Job Query Class/Model
class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    radius = db.Column(db.String(2))
    entryLevel = db.Column(db.Boolean())
    #jobs = db.relationship('Job', backref='query', lazy=True) # Does this need to be in init and schema? # put under class Job for now
    
    # Okay, it looks like maybe init is taken care of in this version of Flask
    #  def __init__(self, term, city, state, radius, entryLevel):
    #      self.term = term
    #      self.city = city
    #      self.state = state
    #      self.radius = radius
    #      self.entryLevel = entryLevel

    def __repr__(self):
        return '<Query %r>' % self.id

# Job Class/Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    href = db.Column(db.String(100), nullable=False)
    query = db.relationship('Query', backref=db.backref('jobs', lazy=True))
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)

    def __repr__(self):
        return '<Job %r>' % self.title

    # See line 32
    # def __init__(self, title, company, city, state, href, query_id):
    #     self.title = title
    #     self.company = company
    #     self.city = city
    #     self.state = state
    #     self.href = href
    #     self.query_id = query_id

# Query Schema
class QuerySchema(ma.Schema):
    class Meta:
        fields = ('id', 'term', 'city', 'state', 'radius', 'entryLevel') # does jobs relationship need to be here?

# Job Schema
class JobSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'company', 'city', 'state', 'href', 'query_id')

# Init schema
query_schema = QuerySchema()
queries_schema = QuerySchema(many=True)
job_schema = JobSchema()
jobs_schema = JobSchema(many=True)

# Create a Job
@app.route('/job', methods=['POST'])
def add_job():
    title = request.json['title']
    company = request.json['company']
    city = request.json['city']
    state = request.json['state']
    href = request.json['href']
    query_id = request.json['query_id']

    new_job = Job(title, company, city, state, href, query_id)

    db.session.add(new_job)
    db.session.commit()

    return job_schema.jsonify(new_job)

# Create a Query
@app.route('/query', methods=['POST'])
def add_query():
    term = request.json['term']
    city = request.json['city']
    state = request.json['state']
    radius = request.json['radius']
    entryLevel = request.json['entryLevel']

    new_query = Job(term, city, state, radius, entryLevel)

    db.session.add(new_query)
    db.session.commit()

    return job_schema.jsonify(new_query)

# testing
# /j?term=software+engineer&city=bethpage+ny
# '+' replaced with blank spaces
#@app.route('/j', methods=['GET'])
#def testing():
#    term = request.args['term']
#    city = request.args['city']
#    return jsonify({"term": term, "city": city})

# Get all jobs
@app.route('/job', methods=['GET'])
def get_jobs():
    all_jobs = Job.query.all()
    result = jobs_schema.dump(all_jobs)
    return jsonify(result)

# Get all queries
@app.route('/query', methods=['GET'])
def get_queries():
    all_queries = Query.query.all()
    result = queries_schema.dump(all_queries)
    return jsonify(result)

# Get single job
@app.route('/job/<id>', methods=['GET'])
def get_job(id):
    job = Job.query.get(id)
    return job_schema.jsonify(job)

# Get single query
@app.route('/query/<id>', methods=['GET'])
def get_query(id):
    query = Query.query.get(id)
    return query_schema.jsonify(query)

# Update a job
@app.route('/job/<id>', methods=['PUT'])
def update_job(id):
    job = Job.query.get(id)

    title = request.json['title']
    company = request.json['company']
    city = request.json['city']
    state = request.json['state']
    href = request.json['href']
    query_id = request.json['query_id']

    job.title = title
    job.company = company
    job.city = city
    job.state = state
    job.href = href
    job.query_id = query_id

    db.session.commit()

    return job_schema.jsonify(job)

# Update a query
@app.route('/query/<id>', methods=['PUT']) #'term', 'city', 'state', 'radius', 'entryLevel'
def update_query(id):
    query = Query.query.get(id)

    term = request.json['term']
    city = request.json['city']
    state = request.json['state']
    radius = request.json['radius']
    entryLevel = request.json['entryLevel']

    query.term = term
    query.city = city
    query.state = state
    query.radius = radius
    query.entryLevel = entryLevel

    db.session.commit()

    return job_schema.jsonify(query)

# Delete a job
@app.route('/job/<id>', methods=['DELETE'])
def delete_job(id):
    job = Job.query.get(id)
    db.session.delete(job)
    db.session.commit()

    return job_schema.jsonify(job)

# Delete a query
@app.route('/query/<id>', methods=['DELETE'])
def delete_query(id):
    query = Query.query.get(id)
    db.session.delete(query)
    db.session.commit()

    return job_schema.jsonify(query)

# Run server
if __name__ == '__main__':
    app.run(debug=True)
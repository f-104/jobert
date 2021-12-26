from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hobbes@mysql:3306/jobertdb'
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

    def __repr__(self):
        return '<Query %r>' % self.id

# Job Class/Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    href = db.Column(db.String(5000), nullable=False)
    query_rel = db.relationship('Query', backref=db.backref('jobs', lazy=True))
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)

    def __repr__(self):
        return '<Job %r>' % self.title

# Query Schema
class QuerySchema(ma.Schema):
    class Meta:
        fields = ('id', 'term', 'city', 'state', 'radius')

# Job Schema
class JobSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'company', 'location', 'href', 'query_id')

# Init schema
query_schema = QuerySchema()
queries_schema = QuerySchema(many=True)
job_schema = JobSchema()
jobs_schema = JobSchema(many=True)

# Parameters allowed by radius filter on Indeed
radius_options = ['0', '5,', '10', '15', '25', '50', '100']

# Create a Job
@app.route('/job', methods=['POST'])
def add_job():
    title = request.json['title']
    company = request.json['company']
    location = request.json['location']
    href = request.json['href']
    query_id = request.json['query_id']

    new_job = Job(title=title, company=company, location=location, href=href, query_id=query_id)

    db.session.add(new_job)
    db.session.commit()

    return job_schema.jsonify(new_job), 201

# Create a Query
@app.route('/query', methods=['POST'])
def add_query():
    term = request.json['term']
    city = request.json['city']
    state = request.json['state']
    radius = request.json['radius']

    if radius not in radius_options:
        return f"400 Bad Request\nInvalid radius: {radius}\nRadius must be one of {radius_options}", 400

    new_query = Query(term=term, city=city, state=state, radius=radius)

    db.session.add(new_query)
    db.session.commit()

    return query_schema.jsonify(new_query), 201

# Get all jobs
@app.route('/job', methods=['GET'])
def get_jobs():
    if qid := request.args.get('query_id'):
        all_jobs = Job.query.filter_by(query_id=qid)
    else:
        all_jobs = Job.query.all()
    result = jobs_schema.dump(all_jobs)
    return jsonify(result), 200

# Get all queries
@app.route('/query', methods=['GET'])
def get_queries():
    all_queries = Query.query.all()
    result = queries_schema.dump(all_queries)
    return jsonify(result), 200

# Get single job
@app.route('/job/<id>', methods=['GET'])
def get_job(id):
    job = Job.query.get(id)
    return job_schema.jsonify(job), 200

# Get single query
@app.route('/query/<id>', methods=['GET'])
def get_query(id):
    query = Query.query.get(id)
    return query_schema.jsonify(query), 200

# Update a job
@app.route('/job/<id>', methods=['PUT'])
def update_job(id):
    job = Job.query.get(id)

    title = request.json['title']
    company = request.json['company']
    location = request.json['location']
    href = request.json['href']
    query_id = request.json['query_id']

    job.title = title
    job.company = company
    job.location = location
    job.href = href
    job.query_id = query_id

    db.session.commit()

    return job_schema.jsonify(job), 200

# Update a query
@app.route('/query/<id>', methods=['PUT'])
def update_query(id):
    query = Query.query.get(id)

    term = request.json['term']
    city = request.json['city']
    state = request.json['state']
    radius = request.json['radius']

    if radius not in radius_options:
        return f"400 Bad Request\nInvalid radius: {radius}\nRadius must be one of {radius_options}", 400

    query.term = term
    query.city = city
    query.state = state
    query.radius = radius

    db.session.commit()

    return query_schema.jsonify(query), 200

# Delete a job
@app.route('/job/<id>', methods=['DELETE'])
def delete_job(id):
    job = Job.query.get(id)
    db.session.delete(job)
    db.session.commit()

    return job_schema.jsonify(job), 200

# Delete a query
@app.route('/query/<id>', methods=['DELETE'])
def delete_query(id):
    query = Query.query.get(id)
    db.session.delete(query)
    db.session.commit()

    return query_schema.jsonify(query), 200

# Run server
if __name__ == '__main__':
    #app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
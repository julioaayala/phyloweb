from flask import Flask

## Initialize the app
app = Flask(__name__, instance_relative_config=True, template_folder='templates')
app.config['JOBS_FOLDER'] = 'jobs'

## Import routes
import phyloweb.routes

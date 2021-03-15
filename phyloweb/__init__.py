from flask import Flask

app = Flask(__name__, instance_relative_config=True, template_folder='templates')
app.config['JOBS_FOLDER'] = 'jobs'

import phyloweb.routes

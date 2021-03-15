from phyloweb import app
from flask import render_template, request, jsonify, send_file, send_from_directory
from phyloweb import phylotools
import re
import os
from pathlib import Path


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/software')
def software():
    return render_template('software.html')

@app.route('/fetchsequences', methods=['POST'])
def getFasta():
    ## Retrieve fields from form
    accessionNumbers = request.form['accessionNumbers']
    accessionNumbersList = list(filter(None, re.split(';|\n',accessionNumbers)))
    seqtype =  request.form['seqtype']
    includetaxonomy = True if request.form.get('includetaxonomy') else False

    if len(accessionNumbersList)<4:
        saveResult = 'Error: You need to provide at least 4 taxa'
        fetchResult = {}
    else:    ## Get sequences
        fetchResult = phylotools.getSequences(accessionNumbersList, db=seqtype, includetaxonomy=includetaxonomy)
        saveResult = phylotools.saveFasta(fetchResult)


    #Response
    seqids = list(fetchResult.keys())
    valid = False if saveResult.startswith('Error') else True ## In order to handle valid requests
    return jsonify({'result':saveResult, 'seqids':seqids, 'valid':valid}), 200


@app.route('/gettree', methods=['POST'])
def getTree():
    config = {}
    jobid = request.form['jobid']
    config['alignmethod'] = request.form['alignmethod']
    config['outgroup'] = request.form['outgroup']
    if ('nuclsubmodel' in request.form):
        config['submodel'] = request.form['nuclsubmodel']
    else:
        config['submodel'] = request.form['protsubmodel'] + request.form['aasubmodel']
    config['seed'] = request.form['seed']

    saveConfig = phylotools.generateConfigFile(jobid, config)
    if saveConfig:
        valid = phylotools.runPhylogeny(jobid)
        result = jobid
    else:
        result = 'An error occured while generating the phylogeny.'

    return jsonify({'valid':saveConfig, 'result':result}), 200

@app.route('/results/<jobid>')
def getResults(jobid):
    tree = phylotools.getRawTree(jobid)
    return render_template('results.html', jobid=jobid, tree=tree)

@app.route('/download/<path:jobid>')
def getFile(jobid):
    folder = os.path.join(Path(app.root_path).parent, app.config['JOBS_FOLDER'], jobid)
    print(folder)
    return send_file(folder, as_attachment=True)

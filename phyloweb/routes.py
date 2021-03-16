from phyloweb import app
from flask import render_template, request, jsonify, send_file, send_from_directory
from phyloweb import phylotools
import re
import os
from pathlib import Path

## Julio Ayala
## Flask routes file

@app.route('/')
def index():
    # Home route
    return render_template('index.html')

@app.route('/software')
def software():
    # Route to render the software template, which contains links to the used software
    return render_template('software.html')

@app.route('/fetchsequences', methods=['POST'])
def getFasta():
    # Route to get FASTA sequences based on accession IDs
    ## Retrieve fields from form
    accessionNumbers = request.form['accessionNumbers']
    accessionNumbersList = list(filter(None, re.split(';|\n',accessionNumbers)))
    seqtype =  request.form['seqtype']
    includetaxonomy = True if request.form.get('includetaxonomy') else False
    ## RAxML requires at least 4 taxa to infer a tree, thus it's valdated before fetching.
    if len(accessionNumbersList)<4:
        saveResult = 'Error: You need to provide at least 4 taxa'
        fetchResult = {}
    else:    ## Get sequences
        ## Sequences are retrieved and saved to a file. Saveresult contains the jobid, which corresponds to the folder where the sequences are stored.
        fetchResult = phylotools.getSequences(accessionNumbersList, db=seqtype, includetaxonomy=includetaxonomy)
        saveResult = phylotools.saveFasta(fetchResult)

    #Response
    seqids = list(fetchResult.keys())
    valid = False if saveResult.startswith('Error') else True ## In order to handle valid requests
    return jsonify({'result':saveResult, 'seqids':seqids, 'valid':valid}), 200


@app.route('/gettree', methods=['POST'])
def getTree():
    # Route to generate a config file and execute the phylogenetic tree snakemake function.
    # Returns a JSON containing the jobid if it's successful, otherwise, an error message
    config = {}
    jobid = request.form['jobid']
    config['alignmethod'] = request.form['alignmethod']
    config['outgroup'] = request.form['outgroup']
    # Validate the substitution model to be used
    if ('nuclsubmodel' in request.form):
        config['submodel'] = request.form['nuclsubmodel']
    else:
        config['submodel'] = request.form['protsubmodel'] + request.form['aasubmodel']
    config['seed'] = request.form['seed']

    # generate config file
    saveConfig = phylotools.generateConfigFile(jobid, config)
    if saveConfig:
        valid = phylotools.runPhylogeny(jobid)
        result = jobid
    else:
        result = 'An error occured while generating the phylogeny.'

    return jsonify({'valid':saveConfig, 'result':result}), 200

@app.route('/results/<jobid>')
def getResults(jobid):
    # Route to render the raw newick tree and show download links
    tree = phylotools.getRawTree(jobid)
    return render_template('results.html', jobid=jobid, tree=tree)

@app.route('/download/<path:jobid>')
def getFile(jobid):
    # Generic download function, given a job id and the file to be downloaded.
    folder = os.path.join(Path(app.root_path).parent, app.config['JOBS_FOLDER'], jobid)
    return send_file(folder, as_attachment=True)

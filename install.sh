#!/bin/bash

## Core packages:
# conda install -y -c conda-forge snakemake
conda install -y flask=1.1.2

## Install urllib and biopython for sequence retrieval
conda install -y -c conda-forge -c bioconda -c defaults urllib3 biopython=1.77

## Alignment software
conda install -y -c bioconda clustalo=1.2.3 mafft=7.475

## Tree inference
conda install -y -c bioconda raxml=8.2.12

## Set up the flask app
python -m pip install .
export FLASK_APP=phyloweb
export FLASK_ENV=development

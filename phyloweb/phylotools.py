from Bio import Entrez
import urllib3
import time
import uuid
import os

## Julio Ayala
## 2021.03.09
## Toolbox of functions for phylogenetic tree inference.

def getEntrezRecord(id, db):
    ## Get an entrez record given an accession number(id) and a database (nucleotide or protein)
    handle = Entrez.efetch(db=db, id=id, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    return record

def getSequences(accessionNumbers, db, includetaxonomy = False):
    ## Function to get sequences based on a list of accession numbers
    Entrez.email ="ayala.j@live.com" ## Set an Entrez email for the query
    records = {}
    for line in accessionNumbers: ## Iterate through accesion numbers and get their sequences, if they exist
        try:
            record = Entrez.esearch(db=db, retmax=2, term=line, idtype="acc")
            if int(Entrez.read(record)["Count"]) > 0:
                record.close()
                record = getEntrezRecord(line, db)
                if 'GBSeq_sequence' not in record[0].keys(): # Handling different format of sequences
                    record[0]['GBSeq_sequence'] = 'NA'

                if includetaxonomy and 'GBSeq_organism' in record[0].keys(): # Handle taxonomy
                    organism = '_'+record[0]['GBSeq_organism'].replace(' ','_')
                    records[record[0]['GBSeq_accession-version']+organism] = record[0]['GBSeq_sequence']
                else:
                    records[record[0]['GBSeq_accession-version']] = record[0]['GBSeq_sequence']
            else:
                records[line] = 'NA'
        except Exception as e: ## Manage exceptions, either for records not found or timeouts
            if str(type(e))=="<class 'urllib.error.HTTPError'>": ## For records not found
                records[line] = 'NA'
                continue
            time.sleep(5) ## Wait 5 seconds and query again
            record = Entrez.esearch(db=db, retmax=2, term=line, idtype="acc")
            if int(Entrez.read(record)["Count"]) > 0:
                record.close()
                record = getEntrezRecord(line, db)
                if 'GBSeq_sequence' not in record[0].keys(): # Handling different format of sequences
                    record[0]['GBSeq_sequence'] = 'NA'

                if includetaxonomy and 'GBSeq_organism' in record[0].keys(): # Handle taxonomy
                    organism = '_'+record[0]['GBSeq_organism'].replace(' ','_')
                    records[record[0]['GBSeq_accession-version']+organism] = record[0]['GBSeq_sequence']
                else:
                    records[record[0]['GBSeq_accession-version']] = record[0]['GBSeq_sequence']
            else:
                records[line] = 'NA'
        time.sleep(1) # Avoid sending many requests at once
    return records

def saveFasta(records): ## Saves a fasta file given a dictionary of sequences.
    jobid = uuid.uuid4().hex ## Generate a random hash for the folder
    for i,j in records.items(): ## Validate if sequences are valid, otherwise, return an error.
        if j=='NA':
            return 'Error: '+i+' is an invalid accession number. Please validate'


    try:
        os.mkdir('jobs/'+jobid) ## Create folder, file and write sequences.
        f = open('jobs/'+jobid+'/sequences.fasta', 'w')
        for i in records:
            f.write('>'+i+'\n')
            f.write(records[i]+'\n')
        f.close()
        return jobid
    except Exception as e:
        return 'Error: An error occured while creating the fasta file'

def generateConfigFile(jobid, parameters): ## Generate a params.tsv file given a dictionary of parameters.
    ## Try to write to file
    try:
        f = open('jobs/'+jobid+'/params.tsv', 'w')
        f.write('\t'.join(parameters.keys()) + '\n')
        f.write('\t'.join(parameters.values()) + '\n')
        f.close()
        success = True
    except Exception as e:
        success = False
    return success

def runPhylogeny(jobid): ## Runs snakemake on a given folder (jobid).
    os.chdir('jobs') # First, change directory to jobs, and execute the command
    command = 'snakemake --config dir='+jobid+' --cores 4'
    os.system(command)
    os.chdir('..') # Return to the previous folder
    return True


def getRawTree(jobid): ## Returns the result tree from a given job.
    tree = ''
    with open('jobs/'+jobid+'/RAxML_result.tree.tre', 'r') as t:
        tree += t.read()
    return tree.replace('\n', '')

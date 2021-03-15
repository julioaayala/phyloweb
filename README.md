# Phyloweb - A web application to infer phylogenetic trees from accession numbers

### Setup instructions
In order to setup the app, you need to have conda installed.

Create an environment with:
```bash
conda create -n phyloweb -c conda-forge -c bioconda snakemake python=3.8.3 -y
conda activate phyloweb
```

Once created and active, run the install.sh script
```bash
chmod +x install.sh
./install.sh
```

Finally, run the app with:

```bash
flask run
```

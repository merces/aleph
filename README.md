# Aleph - OpenSource Malware Analysis Pipeline System

## What?
Aleph is designed to pipeline the analysis of malware samples. It has a series of collectors that will gather samples from many sources and shove them into the pipeline. The sample manager has a series of plugins that are ran against the sample and returns found data into JSON form.

These JSON data can be further processed and queried in a objective manner instead of *grepping and regexing*.

## How?
The main Aleph daemon is a loose-coupled python application and library. These are composed by the Aleph Service that spawns:

1. The Collectors. These are responsible for going to multiple sources (Filesystem folder, IMAP folder, FTP directory etc) and collect all the files there, store locally and add them to the processing queue. Each collector runs in its own process (fork).
2. Multiple (quantity is configurable) parallel SampleManager services (that will pull samples from the work queue and process them) and run the plugins that receives the sample path and return the JSON object of found artifacts.
3. The sample object is converted to JSON along with its data and is stored into an Elasticsearch backend.

## Installing Aleph
### Requirements
#### ElasticSearch
First if you don't have an [Elasticsearch](www.elasticsearch.org) instance ready, you must install one. 

For Debian/Ubuntu/Redhat/Fedora/CentOS (yum + apt basically) users, follow [this guide](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html).

#### Python modules
We strongly suggest that you use python's virtual environment so you don't pollute the rest of your OS installation with python modules. To make a contained virtual environment, install _virtualenv_ with _pip_:

    pip install virtualenv

Go to the desired Aleph installation folder and type the following to create and activate your virtual environment:

    virtualenv venv # 'venv' can be any name
    source venv/bin/activate

There will be the environment name (venv) appended to your PS1 variable:

    (venv)(2014-08-19 17:36:%)(~/opt/aleph/)

All python modules required are listed on the _requirements.txt_ file on the root repository folder. You can install all of them at once using _pip_:

    pip install < requirements.txt

Then clone the repository and copy the settings file:

    git clone https://github.com/merces/aleph.git --branch aleph-python --single-branch .
    cp aleph/settings.py.orig aleph/settings.py

Edit settings.py and add a local source (a folder where Aleph will search for samples - **WARNING: ALEPH WILL MOVE THE SAMPLE THUS REMOVING FROM THE ORIGINAL FOLDER**) _The folder must exists as Aleph won't try to create them_

    SAMPLE_SOURCES = [
        ('local', {'path': '/opt/aleph/unprocessed_samples'}),
    ]

Review your Elasticsearch installation URI

    ELASTICSEARCH_URI = '127.0.0.1:9200'

** Workaround step **
As I still finish some of the code, there are some folders that are not on the repository and must be created manually and set accordingly on the *settings.py* file:

    SAMPLE_TEMP_DIR = '/opt/aleph/temp'
    SAMPLE_STORAGE_DIR = '/opt/aleph/samples'

And Aleph is ready to run!

#### Running 
Go to Aleph folder, activate the virtual environment and run the bin/aleph-server.py as following:

    cd /opt/aleph/
    source venv/bin/activate
    ./bin/aleph-server.py

And that's it. Check your logs under log/aleph.log to any troubleshooting.

#### Reviewing collected data

For now there's still no Web interface (but it will, I swear) so you must use other software to review and query data on elasticsearch. I strongly suggest this [Chrome REST client plugin](https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm?hl=en) or the great [Kibana](http://www.elasticsearch.org/guide/en/kibana/current/working-with-queries-and-filters.html)

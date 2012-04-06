# This fabric script tests localwiki on all supported versions of Ubuntu
from fabric.api import *
from vm import *
import fexpect


images = { 'ubuntu10.04': 'ami-8cb33ebc',
           'ubuntu10.10': 'ami-04f97434',
           'ubuntu11.04': 'ami-18f97428',
           'ubuntu11.10': 'ami-20f97410'
          }

prompts = []
prompts += fexpect.expect('3. Paste the API key below:', 'e886fd33ac5743868c31dfebecdb129b')
prompts += fexpect.expect('Would you like to create one now?', 'no')

def test_install(image_name):
    with temporary_ec2_instance(ami_id=images[image_name]):
        sudo('apt-get -y install python-software-properties')
        sudo('yes | apt-add-repository ppa:localwikidev/testing')
        sudo('apt-get update')
        with fexpect.expecting(prompts):
            fexpect.sudo('apt-get -y --force-yes install localwiki')
        # On Ubuntu 11.10, downgrade to psycopg2 v2.4.1 or else tests can't run
        # See https://code.djangoproject.com/ticket/16250
        if image_name == 'ubuntu11.10':
            sudo('apt-get -y install python-dev libpq-dev')
            sudo('pip install psycopg2==2.4.1')
        # Give localwiki db user permission to create a database, for tests
        sudo('psql -c "ALTER ROLE localwiki WITH CREATEDB;"', user='postgres')
        sudo('localwiki-manage test pages maps tags versioning diff ckeditor redirects users')

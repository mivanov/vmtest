# This fabric script tests localwiki on all supported versions of Ubuntu
from fabric.api import *
from vm import *

images = { 'ubuntu10.04': 'ami-8cb33ebc',
           'ubuntu10.10': 'ami-04f97434',
           'ubuntu11.04': 'ami-18f97428',
           'ubuntu11.10': 'ami-20f97410'
          }

def test_install(os):
    with temporary_ec2_instance(ami_id=images[os]):
        sudo('apt-get install python-software-properties')
        sudo('apt-add-repository ppa:localwikidev/testing')
        sudo('apt-get update')
        sudo('apt-get install localwiki')
        sudo('localwiki-manage test pages maps tags versioning diff ckeditor redirects users')

import sys
import time

try:
    import settings
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    EC2_REGION = getattr(settings, 'EC2_REGION', 'us-west-2')
    EC2_SECURITY_GROUP = getattr(settings, 'EC2_SECURITY_GROUP', 'default')
    EC2_KEY_NAME = settings.EC2_KEY_NAME
    EC2_KEY_FILE = settings.EC2_KEY_FILE
except:
    sys.exit('Missing settings file! Copy settings.py.template to settings.py'
             ' and fill in your AWS credentials.')

from boto import ec2
from fabric.api import env


class dummy_instance:
    def __init__(self, ami_id='ami-8cb33ebc'):
        self.ami_id = ami_id

    def __enter__(self):
        print "spinning up dummy"
        self.instance = "dummy_instance"
        self.old_host_string = env.host_string

        return self.instance

    def __exit__(self, type, value, traceback):
        print "terminating dummy"
        env.host_string = self.old_host_string
        return True


class temporary_ec2_instance:
    def __init__(self, ami_id='ami-8cb33ebc'):
        self.instance = None
        self.ami_id = ami_id
    
    def wait_until_state(self, state):
        while self.instance.state != state:
            print '.',
            sys.stdout.flush()
            time.sleep(1)
            self.instance.update()

    def wait_until_booted(self):
        time.sleep(30)

    def __enter__(self):
        conn = ec2.connect_to_region(EC2_REGION,
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        res = conn.run_instances(self.ami_id,
                   key_name=EC2_KEY_NAME,
                   instance_type='t1.micro',
                   security_groups=[EC2_SECURITY_GROUP])
        self.instance = res.instances[0]
        print "Spinning up instance. Waiting for it to start. "
        self.wait_until_state('running')
        print " Instance running."
        print "Hostname: %s" % self.instance.public_dns_name
        print "Waiting for instance to finish booting up. "
        self.wait_until_booted()
        print "Instance ready to receive connections. "
        env.host_string = '%s@%s' % ('ubuntu', self.instance.public_dns_name)
        env.key_filename = EC2_KEY_FILE
        return self.instance

    def __exit__(self, type, value, traceback):
        if self.instance:
            self.instance.terminate()
            print "Terminating instance. "
            self.wait_until_state('terminated')
            print " Instance terminated."
            return True

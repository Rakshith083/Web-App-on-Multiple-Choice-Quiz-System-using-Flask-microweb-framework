from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

def cassandra_connect():
    cloud_config = {
    'secure_connect_bundle': 'secure-connect-intership.zip'
    }
    auth_provider = PlainTextAuthProvider(username='rakshith', password='rakshith12')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    csession = cluster.connect()
    csession.execute('USE quiz')
    return csession
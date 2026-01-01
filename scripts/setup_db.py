from cassandra.cluster import Cluster

cluster = Cluster(['localhost'], port=9042)
session = cluster.connect()

with open('scripts/init_cassandra.cql', 'r') as f:
    cql_script = f.read()
commands = [cmd.strip() for cmd in cql_script.split(';') if cmd.strip()]
for cmd in commands:
    cmd = cmd.strip()
    session.execute(cmd)

print("Database creation successful")
cluster.shutdown()
import docker
client = docker.from_env()
server = client.containers.list()[0].logs().decode()
checker_logs = 'GET / HTTP/1.1'
print(*server.split('\n'), sep='\n')
print(checker_logs in server.split('\n')[-2])
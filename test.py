from py2neo import Graph, Node, Relationship

# Graph()中第一个为local host链接，auth为认证，包含 username 和 password
graph = Graph('bolt://localhost:7687', auth = ('neo4j', 'Wsh021006'))

a = Node("Person", name="Alice", sex="female", ID="222")
b = Node("Person", name="Bob", sex="male", ID="123")
ab = Relationship(a, "KNOWS", b)
graph.create(ab)
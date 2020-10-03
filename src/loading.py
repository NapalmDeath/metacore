from bson import ObjectId

from core.entities import Metavertex, Metaedge
from core.metacore import Metacore, MetacoreConfig

if __name__ == '__main__':
    metacore = Metacore(MetacoreConfig(
        db_connect_url='mongodb://localhost:27017/',
        db_name="metacore"
    ))

    mg = metacore.initialize()

    Metavertex.load(mg, ObjectId("5f78550c91fef687ac76bb06"))
    # Metaedge.load(mg, ObjectId("5f78507b1e90eb81ac2a8006"))

    # mg.load_all()
    print([str(v) for v in mg.vertices.values()], [str(e) for e in mg.edges.values()])



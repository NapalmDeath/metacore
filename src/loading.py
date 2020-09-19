from core.metacore import Metacore, MetacoreConfig

if __name__ == '__main__':
    metacore = Metacore(MetacoreConfig(
        db_connect_url='mongodb://localhost:27017/',
        db_name="metacore"
    ))

    mg = metacore.initialize()
    mg.load_all()
    print([v.id for v in mg.vertices.values()], [e.id for e in mg.edges.values()])



# [х] Сетап
# [] Создание всех элементов
#   [] Добавить в метаребра метавершины
# [] Загрузка из базы
# [] Удаление элементов
# [] Алгоритмы поиска элементов
# [] Визуализация
# [] Добавление абстракций для работы без базы / с базой

# [] Создание агентов
# [] Алгоритм запуска агентов


from core.Metacore import Metacore, MetacoreConfig
from core.entities import Metaedge, Metavertex

if __name__ == '__main__':
    metacore = Metacore(MetacoreConfig(
        db_connect_url='mongodb://localhost:27017/',
        db_name="metacore"
    ))

    mg = metacore.initialize()

    v1 = Metavertex(name="v1")
    v2 = Metavertex(name="v2")
    v3 = Metavertex(name="v3")

    mg.save_entities(v1, v2, v3)

    v1.add_child(v2)

    e1 = Metaedge(name="v1_v3", source=v1, dest=v3, zhopa="azaaza")

    mg.save_entities(v1, e1)

    print(mg.vertices)
    print(mg.edges)



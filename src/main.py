# [х] Сетап
# [x] Создание всех элементов
#   [] Добавить в метаребра метавершины
# [x] Сохранение всего графа
# [x] Загрузка из базы
# [x] Удаление элементов
# [x] Сохранение через mg.save_entities в любой последовательности
# [x] Сохранение куска графа (через mg.save)
# [] Алгоритмы поиска элементов
# [] Получение части графа из базы
# [] Визуализация
# [] Добавление абстракций для работы без базы / с базой

# [] Создание агентов
# [] Алгоритм запуска агентов


from core.metacore import Metacore, MetacoreConfig
from core.entities import Metaedge, Metavertex

if __name__ == '__main__':
    metacore = Metacore(MetacoreConfig(
        db_connect_url='mongodb://localhost:27017/',
        db_name="metacore"
    ))

    mg = metacore.initialize()

    metacore.drop()

    v1 = Metavertex(name="v1")
    v2 = Metavertex(name="v2")
    v3 = Metavertex(name="v3")
    v4 = Metavertex(name="v4")

    v1.add_child(v2)

    e1 = Metaedge(name="v1_v3", source=v1, dest=v3, zhopa="azaaza")
    e2 = Metaedge(name="v1_v4", source=v1, dest=v4, zhopa="azaaza")

    # Сохранять нужно в правильной последовательности для генерации idшников
    mg.register(v1, v2, v3, v4, e1, e2)

    mg.save_entities(e1)

    # mg.delete_entity(e1)
    # mg.delete_entity(v3)
    #
    # print(mg.vertices)
    # print(mg.edges)

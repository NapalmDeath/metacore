# [х] Сетап
# [x] Создание всех элементов
#   [] Добавить в метаребра метавершины
# [x] Сохранение всего графа
# [x] Загрузка из базы
# [x] Удаление элементов
# [x] Сохранение через mg.save_entities в любой последовательности
# [x] Сохранение куска графа (через mg.save)
# [x] Алгоритмы поиска элементов
#   [x] Поиск вложенных вершин по условию
#   [x] Поиск родительских вершин по условию
#   [x] Проверка, является ли вершина листовой
#   [x] Получение родительских вершин (всех, до которых можно дотянуться)
# [x] Получение части графа из базы
# [] Визуализация
# [x] Добавление абстракций для работы без базы / с базой

# [x] Создание агентов
# [x] Алгоритм запуска агентов
# [x] Алгоритмы обработки
#   [x] Сегментация
#   [x] Предобработка
#   [x] Морфология
#   [x] Синтаксис
#       [x] dependency
#       [] иерархия

# Доп работы:
# [x] Поддержка проверки схождения графа. Например, нельзя вложить родительскую вершину в дочернюю


from core.metacore import Metacore, MetacoreConfig
from core.entities import Metaedge, Metavertex
from core.utils import visualize

if __name__ == '__main__':
    metacore = Metacore(MetacoreConfig(
        db_connect_url='mongodb://localhost:27017/',
        db_name="metacore"
    ))

    mg = metacore.initialize()

    metacore.drop()

    v0 = Metavertex(name="v0")
    v1 = Metavertex(name="v1")
    v2 = Metavertex(name="v2")
    v3 = Metavertex(name="v3")
    # v5 = Metavertex(name="v5")
    # v6 = Metavertex(name="v6")

    v0.add_child(v1)
    v1.add_child(v3)
    # v2.add_child(v3)
    # v2.add_child(v6)
    #
    # v2.attrs.a = 5
    # v2.attrs.b = 10
    # v3.attrs.a = 5
    #
    e1 = Metaedge(name="v1_v2", source=v1, dest=v2)
    e2 = Metaedge(name="v3_v2", source=v3, dest=v2)
    # e2 = Metaedge(name="v1_v4", source=v1, dest=v4, attr2="some_attr")
    # e3 = Metaedge(name="v5_v2", source=v5, dest=v2)

    # Сохранять нужно в правильной последовательности для генерации idшников
    # mg.register(v1, v2, v3, v4, v5, v6, e1, e2, e3)
    mg.register(v0, v1, v2, v3, e1, e2)
    mg.save_all()

    # v1.save()

    # mg.load_all()

    print('---TEST---')

    v1.delete()

    # v1.drop_child(v2)
    # v1.save()

    # mg.save_entities(e1)

    # mg.delete_entity(e1)
    # mg.delete_entity(v2)
    #
    print(list(map(lambda x: x.name, mg.vertices.values())))
    # print(mg.edges)
    # mg.save_all()

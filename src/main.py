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
# Поддержка проверки схождения графа. Например, нельзя вложить родительскую вершину в дочернюю


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

    v1 = Metavertex(name="v1")
    v2 = Metavertex(name="v2")
    v3 = Metavertex(name="v3")
    v4 = Metavertex(name="v4")
    v5 = Metavertex(name="v5")
    v6 = Metavertex(name="v6")

    # v1.add_child(v2)
    # v2.add_child(v3)
    v2.add_child(v4)
    v2.add_child(v6)

    v2.attrs.a = 5
    v2.attrs.b = 10

    v3.attrs.a = 5

    e1 = Metaedge(name="v1_v3", source=v1, dest=v3, zhopa="azaaza")
    e2 = Metaedge(name="v1_v4", source=v1, dest=v4, zhopa1x="azaaza")
    e3 = Metaedge(name="v5_v2", source=v5, dest=v2)

    # Сохранять нужно в правильной последовательности для генерации idшников
    mg.register(v1, v2, v3, v4, v5, v6, e1, e2, e3)

    visualize(mg, 'img.png')

    # mg.save_entities(e1)
    # mg.save_all()

    # mg.delete_entity(e1)
    # mg.delete_entity(v3)
    #
    # print(mg.vertices)
    # print(mg.edges)

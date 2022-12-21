from matplotlib import pyplot as plt
import os
import re

def prePlotMax(nums, fname):
    ''' Подготовка данных к построению графика
    1. Берем данные из второй половины матрицы данных
    каждого файла
    2. Находим максимум среди этих чисел
    3. Записываем найденный максимум в список
    4. Записываем имя файла с текущим максимумом в список
    '''
    IND = 2
    COLUMN = 1
    rang = round(len(nums)/IND)
    maximums = []
    r = []
    for i in range (0, rang):
        vals = []
        for k in range (round(len(nums[i][COLUMN])/IND), len(nums[i][COLUMN])):
            vals.append(nums[i][COLUMN][k])
        maximums.append(max(vals))
        r.append((float)(splitR(fname[i]))) 
    plotMax(maximums, r)

def plotMax(maximums, r):   
    ''' Построение графика с максимумами
    1. Устанавливаем форматирование графика
    (оси, название, цвет, тип, сетка, шрифт)
    2. Строим график по заданным данным
    '''
    FONTSIZE = 14
    NAMEGRAPH = "Maximums"
    Y = 'Ψ'
    X = 'R'

    fig, ax = plt.subplots()
    ax.plot(r, maximums, label = '$\mathit{\Psi_{max}}$', marker = 'o', color = 'seagreen')

    plt.grid(True)
    plt.title(NAMEGRAPH)
    plt.ylabel(Y, fontsize = FONTSIZE)   
    plt.xlabel(X, fontsize = FONTSIZE)

    plt.legend()
    plt.show()

def plotGraph(data, column0, column1):
    ''' Построение графиков зависимости 2 столбца от 1
    1. Рассматриваем только файлы psi2_*
    2. В каждой матрице синхронно сотрируем 0 и 1 столбцы (по 0 столбцу)
    3. Устанавливаем форматирование графика
    (оси, название, цвет, тип, сетка, шрифт)
    4. Строим графики по заданным данным
    '''
    FONTSIZE = 14
    IND = 2
    Y = 'Ψ'
    X = 'R'

    nums = data[0]
    fname = data[1]
    nums = sortData(nums, column0, column1)

    for i in range(0, round(len(fname)/IND)):
        fig, ax = plt.subplots()
        ax.plot(nums[i+7][column0], nums[i+7][column1], label = '$\mathit{Psi_{loc}}$')
        ax.plot(nums[i][column0], nums[i][column1], label = '$\mathit{\Psi_{max}}$', linestyle = '--', color = 'red')
        plt.grid(True)

        plt.title("{0}{1}".format('R = ', str(splitR(fname[i]))))
        plt.ylabel(Y, fontsize=FONTSIZE)   
        plt.xlabel(X, fontsize=FONTSIZE)

        plt.savefig(fname[i].replace('dat', 'png'))
        plt.legend()
        plt.show()

def splitR(name):
    ''' Выделение R из названия файла
    '''
    return re.search(r'(\d+\.\d+[D|E][+|-]\d+)', name).group(1).replace('D', 'E')

def dataFormat(nums):
    ''' Форматирование данных для построения графиков зависимости
    1. Разделяем строки матрицы на отдельные элементы
    2. Приводим данные к вещественному типу
    3. Транспонируем матрицу
    '''
    matr = []
    for line in nums:
        matr.append(list(map(float, line.strip().replace('D', 'E').split(' '))))
    matr = list(map(list, zip(*matr)))
    return matr

def sortData(data, COLUMN0, COLUMN1):
    ''' Обертка для функции сортировки
    1. Проходит по списку с матрицами
    2. Отправляет на сортировку конкретную матрицу
    и индексы стобцов, которые необходимо
    в ней отсортировать
    '''
    for matr in data:
        matr = sortM(matr, COLUMN0, COLUMN1)
    return data
    
def sortM(data, column0, column1):
    ''' Синхронная сотрировка заданных столбцов матрицы данных
    1. Сортируем по столбцу x 0 и 1 столбцы матрицы
    '''
    data[column1] = [y for x,y in sorted(zip(data[column0],data[column1]))]
    data[column0] = sorted(data[column0])
    return data

def readFile(path, column0, column1):
    ''' Чтение данных из файлов
    1. Читаем данные из файла полностью
    2. Рабиваем их по переносу строки
    3. Добавляем их в список после форматирования
    4. Добавляем в список название файла с данными
    '''
    nums = []   
    data = []
    nfile = []
    for filename in os.listdir(path):
        with open(os.path.join(path, filename), 'r') as f:
            nums = f.read().replace("  ", " ").split('\n')            
            data.append(dataFormat(nums))
            nfile.append(filename)
    return (data, nfile)

def plotting():
    ''' Главная функция, старт
    1. Устанавливаем директорию с файлами данных
    2. Устанавливаем столбцы, по которым строим графики
    3. Читаем данные из файла
    4. Строим по считанным данным графики
    '''
    PATH = "data"   
    COLUMN0 = 0
    COLUMN1 = 1   
    data = readFile(PATH, COLUMN0, COLUMN1)
    prePlotMax(data[0], data[1])
    plotGraph(data, COLUMN0, COLUMN1)
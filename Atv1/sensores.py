from pymongo import MongoClient 
import threading
import time
import random

Client = MongoClient("mongodb://localhost:27017/")
db = Client['bancoiot']
sensor = db["sensores"]

def sensorTemperatura(nome, intervalo):

    while True:
        temperaturaNova = random.sample(range(30, 41), 1)
        print(nome, ' - Nova temperatura: ', temperaturaNova[0], '°C')
        if temperaturaNova[0] > 38:
            print('Atenção! Temperatura muito alta! Verificar o sensor', nome)
            sensor.update_one(
                {'nomeSensor': nome},
                {'$set': {'valorSensor': temperaturaNova}, '$set': {'sensorAlarmado': True}}
            )
            break
        if temperaturaNova[0] <= 38:
            sensor.update_one(
                {'nomeSensor': nome},
                {'$set': {'valorSensor': temperaturaNova}}
            )
            print('Temperatura normal', nome, 'atualizado com sucesso.')
        time.sleep(intervalo)

# Cada Thread será responsável por simular a temperatura de um sensor em uma rede de internet das coisas (IOT)
x = threading.Thread(target=sensorTemperatura, args=(sensor.find_one({'nomeSensor': 'Temp1'}, {'nomeSensor': 1, '_id': 0}), 2))
x.start()

y = threading.Thread(target=sensorTemperatura, args=(sensor.find_one({'nomeSensor': 'Temp2'}, {'nomeSensor': 1, '_id': 0}) , 2))
y.start()

z = threading.Thread(target=sensorTemperatura, args=(sensor.find_one({'nomeSensor': 'Temp3'}, {'nomeSensor': 1, '_id': 0}), 2))
z.start()

# Inserindo 3 sensores:

novoSensor1 = {
    'nomeSensor': 'Temp1',
    'valorSensor': random.sample(range(30, 40), 1),
    'unidadeMedida': 'Celsius',
    'sensorAlarmado': False
}

result1 = db.sensores.insert_one(novoSensor1)
if result1.acknowledged:
    print('Documento 1 inserido com sucesso. ID:', result1.inserted_id)
else:
    print('Falha ao inserir o documento 1.')

novoSensor2 = {
    'nomeSensor': 'Temp2',
    'valorSensor': random.sample(range(30, 40), 1),
    'unidadeMedida': 'Celsius',
    'sensorAlarmado': False
}

result2 = sensor.insert_one(novoSensor2)
if result2.acknowledged:
    print('Documento 2 inserido com sucesso. ID:', result2.inserted_id)
else:
    print('Falha ao inserir o documento 2.')

novoSensor3 = {
    'nomeSensor': 'Temp3',
    'valorSensor': random.sample(range(30, 40), 1),
    'unidadeMedida': 'Celsius',
    'sensorAlarmado': False
}

result3 = sensor.insert_one(novoSensor3)
if result3.acknowledged:
    print('Documento 3 inserido com sucesso. ID:', result3.inserted_id)
else:
    print('Falha ao inserir o documento 3.')



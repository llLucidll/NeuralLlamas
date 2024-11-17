from pymongo import MongoClient

link = 'mongodb+srv://srivanthchitta52:focusflow123@neuralllama.nep0f.mongodb.net/NeuralLlama?tlsAllowInvalidCertificates=true'
cluster = MongoClient(link)
db = cluster['NeuralLlama']
collection = db['concentration']
collection.insert_one({'name': 'John Doe', 'age': 30})
cluster.close()

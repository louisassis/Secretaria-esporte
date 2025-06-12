from pymongo import MongoClient

try:
    client = MongoClient("mongodb+srv://assisluis111:senha@cluster0.0ohfzwd.mongodb.net/?retryWrites=true&w=majority")
    client.server_info()
    print("✅ Conexão bem-sucedida com o MongoDB Atlas!")
except Exception as e:
    print("❌ Erro na conexão:", e)


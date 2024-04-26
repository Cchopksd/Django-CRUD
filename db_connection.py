import pymongo

uri = "mongodb+srv://kasiditsuwa:Hello.1234@product.zrk6tjy.mongodb.net/?retryWrites=true&w=majority&appName=product"

client = pymongo.MongoClient(uri)
db = client["interview"]
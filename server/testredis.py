import redis
import requests
from redis.commands.search.field import (
    NumericField, 
    TagField, 
    TextField, 
    VectorField
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

url = "https://raw.githubusercontent.com/bsbodden/redis_vss_getting_started/main/data/bikes.json"
response = requests.get(url)
bikes = response.json()

print(response, bikes)
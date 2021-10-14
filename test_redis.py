#import redis
#import datetime

#for l in range(10):
#    print(l)


#pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
#r = redis.Redis(connection_pool=pool)
#if print(r.lrange('mess', 0, -1)) == None:
 #   print(r.llen('id'))
  #  mess = input('mess')
   # mess = str.replace(mess, ' ', '_')
    #print(r.lpush('mess', {'mess': mess, 'date': datetime.datetime.utcnow()}))
#else:
 #   print(r.llen('id'))
  #  mess = input('mess')
   # mess = str.replace(mess, ' ', '_')
    #print(r.lpush('mess', {'mess': mess, 'date': datetime.datetime.utcnow()}))

#ll = r.lrange('mess', 0, -1)
#for l in ll:
 #   print(list.index(ll, l))
  #  l = str.replace(str(l), '_', ' ')
   # print(str(l[2:-1]))
import base64, hashlib
from werkzeug.security import generate_password_hash, check_password_hash


pas = generate_password_hash('77', method='sha256')
print(pas)
dd = generate_password_hash('77', method='sha256')
print(check_password_hash(pas, '77'))

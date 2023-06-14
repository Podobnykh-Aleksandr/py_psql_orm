import sqlalchemy
from sqlalchemy.orm import sessionmaker
import json
from functools import or_

from models import create_tables, Publisher, Sale, Book, Stock, Shop

SQLsystem = 'postgresql'
login = 'postgres'
password = 'postgres'
host = 'localhost'
port = 5432
db_name = "orm_2"
DSN = f'{SQLsystem}://{login}:{password}@{host}:{port}/{db_name}'
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

create_tables(engine)

with open('tests_data.json', 'r') as db:
    data = json.load(db)

for line in data:
    method = {
        'publisher': Publisher,
        'shop': Shop,
        'book': Book,
        'stock': Stock,
        'sale': Sale,
    }[line['model']]
    session.add(method(id=line['pk'], **line.get('fields')))

session.commit()

publ_name = input('Ведите имя писателя или id для вывода: ')
if publ_name.isnumeric():
    for c in session.query(Publisher).filter(
            Publisher.id == int(publ_name)).all():
        print(c)
else:
    for c in session.query(Publisher).filter(
            Publisher.name.like(f'%{publ_name}%')).all():
        print(c)

        
author_id, author_name = input('Введите идентификатор или имя автора: ')
res = session.query(Book.title, Shop.name, Sale.price, Sale.count, Sale.date_sale).\
      join(Publisher).join(Stock).join(Sale).join(Shop).\
      filter(or_(Publisher.id==author_id, Publisher.name==author_name))

for book, shop, price, count, date in res:
    print(f'{book: <40} | {shop: <10} | {price*count: <8} | {date.strftime('%d-%m-%Y')}')

session.close()

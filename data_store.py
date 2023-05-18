# импорты
import sqlalchemy as sq
import psycopg2
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config import db_url_object

# схема БД
metadata = MetaData()
Base = declarative_base()

def delete_table(con):
    with con.cursor() as cur:
        cur.execute("""
            DROP TABLE if exists cl_v;
            """)


def create_db(conn):
    with conn.cursor() as cur:
        delete_table(conn)
        cur.execute("""
            create table if not exists cl_v (
            profile_id Integer,
            worksheet_id Integer, primary key(profile_id, worksheet_id));""")
        conn.commit()
    print("БД cоздана")



# class Viewed(Base):
#     __tablename__ = 'cl_v'
#     profile_id = sq.Column(sq.Integer, primary_key=True)
#     worksheet_id = sq.Column(sq.Integer, primary_key=True)


def add_db(conn, id_cl,id_search):
    """добавление записи в бд"""
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO cl_v (profile_id,worksheet_id) VALUES (%s,%s);
                """, (id_cl,id_search))
        conn.commit()
def sel_db(conn,id_cl,id_search):
    with conn.cursor() as cur:
        cur.execute("""
                    select cl_v.worksheet_id from cl_v where profile_id=%s and cl_v.worksheet_id=%s;
                    """, (id_cl,id_search))
        conn.commit()
        list_sear=cur.fetchall()
        print(f'list_sear= {list_sear}')
        return list_sear

# извлечение записей из БД

# engine = create_engine(db_url_object)
# with Session(engine) as session:
#     from_bd = session.query(Viewed).filter(Viewed.profile_id==1).all()
#     for item in from_bd:
#         print(item.worksheet_id)
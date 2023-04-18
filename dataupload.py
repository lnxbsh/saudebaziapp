import sqlalchemy as sa
import pandas as pd

con = sa.create_engine('postgresql://saudebaz:emJNrMiFX83SRCwFcokOnwhzNJkaU7Fn@dpg-cgtv1paut4mcfrnp2b70-a.singapore-postgres.render.com/saudebazi')
chunks = pd.read_csv('Combined - Sheet1.csv', chunksize=100000)
for chunk in chunks:
    chunk.to_sql(name='table', if_exists='append', con=con)
    
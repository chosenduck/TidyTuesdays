import duckdb
from utils.constants import DB_DIR
from utils.data_transformer import gerar_silver

db_path = DB_DIR / "games_movies.duckdb"
con = duckdb.connect(str(db_path))

df_bronze = con.sql("SELECT * FROM game_films").df()
df_silver = gerar_silver(df_bronze)  # aplica pipeline completo com filtros novos
df_silver["poster_url"] = df_silver["poster_url"].astype("string")
con.execute("DROP TABLE IF EXISTS game_films_silver")
con.execute("CREATE TABLE game_films_silver AS SELECT * FROM df_silver")
print(f"Silver regenerada: {len(df_silver)} linhas")
con.close()
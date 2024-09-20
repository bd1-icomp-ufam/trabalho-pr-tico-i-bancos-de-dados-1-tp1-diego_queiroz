DB_HOST = "localhost"
DB_NAME = "Amazon-metadata"
DB_USER = "postgres"
DB_PASS = "icomp123"

import psycopg2
import pandas as pd

queries = [
    """
    -- (a) Listar os 5 comentários mais úteis e com maior avaliação
    (SELECT titulo, rating, nohelpful
    FROM produtos, review
    WHERE produtos.asin=review.asin
    ORDER BY nohelpful DESC, rating DESC
    LIMIT 5)
    UNION ALL
    (SELECT titulo, rating, nohelpful
    FROM produtos, review
    WHERE produtos.asin=review.asin
    ORDER BY nohelpful DESC, rating ASC
    LIMIT 5);
    """,
    """
    -- (b) Dado um produto, listar os produtos similares com maiores vendas do que ele
    SELECT p.titulo, p.asin
    FROM Produtos p, Similarp s
    WHERE p.asin=s.asin AND p.salesrank < (
                   SELECT salesrank
                   FROM Produtos
                   WHERE Produtos.asin='0486220125'
    );
    """,
    """
    -- (c) Dado um produto, mostrar a evolução diária das médias de avaliação
    SELECT data, AVG(rating)
    FROM Review
    WHERE asin='0486220125'
    GROUP BY data
    ORDER BY data;
    """,
    """
    -- (d) Listar os 10 produtos líderes de venda em cada grupo de produtos
    WITH ProdutosOrdenados AS (
        SELECT
            id,
            grupo,
            titulo,
            salesrank,
            asin,
            ROW_NUMBER() OVER (PARTITION BY grupo ORDER BY salesrank) AS ranking_vendas
        FROM
            Produtos
    )
    SELECT
        grupo,
        titulo
    FROM
        ProdutosOrdenados
    WHERE
        ranking_vendas <= 10;
    """,
    """
    -- (e) Listar os 10 produtos com a maior média de avaliações úteis positivas por produto
    SELECT p.titulo, AVG(r.nohelpful) AS media
    FROM Produtos p, Review r
    WHERE p.asin=r.asin
    GROUP BY p.titulo
    ORDER BY media DESC
    LIMIT 10;
    """,
    """
    -- (f) Listar a 5 categorias de produto com a maior média de avaliações úteis positivas por produto
    SELECT c.categoria, AVG(r.nohelpful) as media
    FROM Review r, Categorias c
    WHERE r.asin=c.asin
    GROUP BY c.categoria
    ORDER BY media DESC
    LIMIT 5;
    """,
    """
    -- (g) Listar os 10 clientes que mais fizeram comentários por grupo de produto
    SELECT grupo, customer, coment_count
    FROM (
        SELECT p.grupo, r.customer, COUNT(*) AS coment_count, ROW_NUMBER() OVER (PARTITION BY p.grupo ORDER BY COUNT(*) DESC) AS ranking
        FROM Produtos p, Review r
        WHERE p.asin = r.asin
        GROUP BY p.grupo, r.customer
    ) AS comentarios_por_cliente
    WHERE
        ranking <= 10
    ORDER BY
        grupo, coment_count DESC;
    """
]


messages = [
    "\nResultados da Consulta (a)",
    "\nResultados da Consulta (b)",
    "\nResultados da Consulta (c)",
    "\nResultados da Consulta (d)",
    "\nResultados da Consulta (e)",
    "\nResultados da Consulta (f)",
    "\nResultados da Consulta (g)",
]

def exec_query(query, message, file):
    try:
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        file.write(message + '\n\n')
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            file.write(str(row) + '\n')

        print(f"Resultados da consulta foram adicionados ao arquivo.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro: {error}")

    finally:
        if conn:
            conn.close()


filename = f'out.txt'
with open(filename, 'w') as file:
    for query, message in zip(queries, messages):
        exec_query(query, message, file)

print(f"Todos os resultados foram gravados em {filename}")

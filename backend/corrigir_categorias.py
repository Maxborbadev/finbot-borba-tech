from db.database import get_connection
from services.categoria_auto import detectar_categoria

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT id, descricao
FROM gastos_cartao
WHERE categoria IS NULL OR categoria = 'Outros'
""")

compras = cursor.fetchall()

for compra in compras:
    id_compra = compra[0]
    descricao = compra[1]

    categoria = detectar_categoria(descricao)

    cursor.execute(
        "UPDATE gastos_cartao SET categoria = ? WHERE id = ?",
        (categoria, id_compra)
    )

conn.commit()
conn.close()

print(f"{len(compras)} compras atualizadas com categoria correta")
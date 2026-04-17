from database import query_to_df

sql = """
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'aperturas'
ORDER BY ORDINAL_POSITION
"""

df = query_to_df(sql)
print("\nColumnas en tabla 'aperturas':")
print(df.to_string(index=False))

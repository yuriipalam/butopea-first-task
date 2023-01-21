import sqlite3


class Database:
    def __init__(self, path_to_db="data.sqlite"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = tuple(), fetchone=False, fetchall=False):
        connection = self.connection
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql, parameters)
        data = None
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def select_all_products(self, **kwargs):
        if kwargs:
            sql = """SELECT * FROM product WHERE """
            sql, parameters = self.formatted_args(sql, kwargs)
            return self.execute(sql, parameters, fetchall=True)
        sql = """SELECT * FROM product"""
        return self.execute(sql, fetchall=True)

    def select_products_feed(self):
        sql = """SELECT DISTINCT p.product_id AS id,
                                 p_desc.name AS title,
                                 p_desc.description AS description,
                                 'https://butopea.com/p/' || p.product_id AS link,
                                 'https://butopea.com/' || p.image AS image_link,
                                 p_img.additional_image_link,
                                 IIF(p.quantity > CAST (1 AS INT), 'in_stock', 'out_of_stock') AS availability,
                                 p.price || 'HUF' AS price,
                                 m.name AS brand,
                                 'new' AS condition
                   FROM product AS p,
                        product_description AS p_desc,
                        manufacturer AS m,
                        (
                            SELECT product_id,
                                   group_concat(image) AS additional_image_link
                              FROM (
                                       SELECT product_id,
                                              'https://butoepa.com/' || image AS image,
                                              sort_order
                                         FROM product_image AS p
                                        ORDER BY product_id,
                                                 sort_order ASC
                                   )
                             GROUP BY product_id
                        )
                        AS p_img
                  WHERE p.product_id = p_desc.product_id AND 
                        p_img.product_id = p.product_id AND 
                        m.manufacturer_id = p.manufacturer_id AND 
                        status = '1';"""
        return self.execute(sql, fetchall=True)

    @staticmethod
    def formatted_args(sql, parameters: dict):
        sql += " AND ".join([f"{item}=?" for item in parameters])
        return sql, tuple(parameters.values())

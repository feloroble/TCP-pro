from datetime import datetime
from app.database import  BaseModel
from peewee import  CharField, ForeignKeyField, IntegerField, FloatField, TextField, DateTimeField, fn


from app.models.tcp import TCPBusiness
from app.models.user import User


class Category(BaseModel):
    name = CharField(max_length=255)  # Nombre de la categoría
    description = TextField(null=True)  # Descripción opcional
    business = ForeignKeyField(TCPBusiness, backref='categories', on_delete='CASCADE')  # Relación con el negocio
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación

    class Meta:
        table_name = 'category'
        indexes = (
            (('name', 'tcpbusiness'), True),  # Asegura que el nombre de la categoría sea único dentro de un negocio
        )


class SubCategory(BaseModel):
    name = CharField(max_length=255)  # Nombre de la subcategoría
    description = TextField(null=True)  # Descripción opcional
    category = ForeignKeyField(Category, backref='subcategories', on_delete='CASCADE')  # Relación con la categoría
    business = ForeignKeyField(TCPBusiness, backref='subcategories', on_delete='CASCADE')  # Relación con el negocio
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación

    class Meta:
        table_name = 'subcategory'
        indexes = (
            (('name', 'category', 'tcpbusiness'), True),  # Asegura que el nombre de la subcategoría sea único dentro de una categoría y un negocio
        )




class Product(BaseModel):
    PRODUCT_TYPES = (
        ('physical', 'Físico'),
        ('digital', 'Digital'),
        ('service', 'Servicio'),
    )

    name = CharField(max_length=255)
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref='products', on_delete='CASCADE')
    tipo = CharField(choices=PRODUCT_TYPES)
    stock = IntegerField(default=0)
    price = FloatField()
    costo = FloatField()
    business = ForeignKeyField(TCPBusiness, backref='products', on_delete='CASCADE')  # Relación con negocio
    created_at = DateTimeField(default=datetime.now)
    um = CharField(null=False)  # Unidad de medida definida en el producto
    created_by = ForeignKeyField(User, backref='products', on_delete='SET NULL', null=True)  # Usuario creador
    code = CharField(unique=True)  # Código único del producto
    image_path = CharField(null=True) 

    @classmethod
    def generate_product_code(cls, business_id, user_id):
        """
        Genera un código único para un producto con el formato:
        INV-(consecutivo dentro del negocio)-(id del negocio)-(id del usuario)
        """
        product_count = cls.select().where(cls.business_id == business_id).count() + 1
        return f"INV-{product_count}-{business_id}-{user_id}-TT"

    def save(self, *args, **kwargs):
        """Sobreescribe el método save para generar automáticamente el código."""
        if not self.code:
            self.code = self.generate_product_code(self.business_id, self.created_by_id)
        super().save(*args, **kwargs)

    class Meta:
        indexes = (
            (('name', 'business'), True),  # Nombre único por negocio
        )


class CostSheet(BaseModel):
    product = ForeignKeyField(Product, backref='cost_sheet', unique=True, on_delete='CASCADE')  # Relación con producto
    business = ForeignKeyField(TCPBusiness, backref='cost_sheets', on_delete='CASCADE')  # Relación con negocio
    user = ForeignKeyField(User, backref='edited_cost_sheets', on_delete='SET NULL', null=True)  # Usuario que editó
    production_level = IntegerField()  # Nivel de producción
    utilization_percentage = FloatField()  # Porcentaje de utilización
    created_by_role = CharField()  # Cargo del usuario que crea
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación
    updated_at = DateTimeField(default=datetime.now)  # Fecha de última edición
    nombre_user = CharField(max_length=50)  # Nombre del usuario
    precio_de_costo = FloatField()  # Precio de costo

    class Meta:
        indexes = (
            (('product', 'business'), True),  # Ficha única por producto y negocio
        )


class Concept(BaseModel):
    FORM_TYPES = (
        ('material', 'Gastos materiales'),  # Fila 1
        ('salary', 'Salario directo'),      # Fila 2
        ('direct', 'Gastos directos'),      # Fila 3
        ('production', 'Gastos asociados a la producción'),  # Fila 4
        ('sum_1_4', 'Suma de filas 1 a 4'),  # Fila 5
        ('admin', 'Gastos generales de administración'),  # Fila 6
        ('sales', 'Gastos de distribución de ventas'),  # Fila 7
        ('financial', 'Gastos financieros'),  # Fila 8
        ('osde', 'Gastos por financiamiento de la OSDE'),  # Fila 9
        ('taxes', 'Gastos por conceptos de impuestos'),  # Fila 10
        ('sum_6_10', 'Suma de filas 6 a 10'),  # Fila 11
        ('sum_1_10', 'Suma de filas 1 a 10'),  # Fila 12
        ('utility', 'Utilidad'),  # Fila 13
        ('price', 'Precio o tarifa'),  # Fila 14
        ('adjusted_price', 'Precio o tarifa ajustada'),  # Fila 15
        ('reference_price', 'Precio de referencia'),  # Fila 16
        ('other', 'Otros gastos'),  # Fila 17
    )
    
    
    cost_sheet = ForeignKeyField(CostSheet, backref='concepts', on_delete='CASCADE')  # Relación con ficha de costo
    concept = CharField()  # Nombre del concepto
    row = CharField() # Número de fila
    base_cost = FloatField()  # Costo base
    new_cost = FloatField()  # Costo nuevo
    concept_type = CharField(choices=FORM_TYPES)  # Tipo de concepto
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación
    
    
    # Método para obtener el label del tipo de concepto
    def get_concept_type_display(self):
           for code, label in self.FORM_TYPES:
              if code == self.concept_type:
                return label
           return self.concept_type  # fallback en caso de que no se encuentre el tipo
    
    @classmethod
    def generate_row_number(cls, cost_sheet_id, concept_type):
        """
        Genera un número de fila único para un concepto dentro de una ficha de costo.
        - Los tipos de concepto tienen un número de fila base.
        - Las subfilas se generan automáticamente para tipos que lo permiten.
        """
        # Mapeo de tipos de concepto a números de fila base
        type_to_base_row = {
            'material': 1,
            'salary': 2,
            'direct': 3,
            'production': 4,
            'sum_1_4': 5,
            'admin': 6,
            'sales': 7,
            'financial': 8,
            'osde': 9,
            'taxes': 10,
            'sum_6_10': 11,
            'sum_1_10': 12,
            'utility': 13,
            'price': 14,
            'adjusted_price': 15,
            'reference_price': 16,
            'other': 17,
        }

        # Obtener el número de fila base
        base_row = type_to_base_row.get(concept_type)
        if base_row is None:
            raise ValueError(f"Tipo de concepto no válido: {concept_type}")
        
        

        # Si el tipo de concepto no permite subfilas, devolver el número base
        if concept_type in ['salary', 'sum_1_4', 'sum_6_10', 'sum_1_10', 'utility', 'price', 'adjusted_price', 'reference_price']:
            return str(base_row)

        # Si permite subfilas, generar el siguiente número disponible
        last_row = (
            cls.select()
            .where(
                (cls.cost_sheet == cost_sheet_id) &
                (cls.concept_type == concept_type)
            )
            .order_by(cls.row.desc())
            .first()
        )

        if last_row:
            # Extraer el último número y aumentar en 0.1
            last_number = float(last_row.row)
            new_number = last_number + 0.1
        else:
            # Si no hay conceptos de este tipo, empezar con el primer número
            new_number = float(f"{base_row}.1")

        return f"{new_number:.1f}"  # Formatear a un decimal (ejemplo: "1.1")

    def save(self, *args, **kwargs):
        """Sobreescribe el método save para generar automáticamente el número de fila."""
        if not self.row:
            self.row = self.generate_row_number(self.cost_sheet_id, self.concept_type)
        super().save(*args, **kwargs)

    @classmethod
    def calculate_sum(cls, cost_sheet_id, start_row, end_row):
        """
        Calcula la suma de los costos de los conceptos dentro de un rango de filas.
        """
        total = (
            cls.select(fn.SUM(cls.new_cost))
            .where(
                (cls.cost_sheet == cost_sheet_id) &
                (cls.row >= str(start_row)) &
                (cls.row <= str(end_row))
            )
            .scalar()
        )
        return total or 0.0

    class Meta:
        indexes = (
            (('cost_sheet', 'row'), True),  # Asegura que el número de fila sea único dentro de una ficha de costo
        )
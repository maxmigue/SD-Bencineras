from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Clase para validar ObjectId de MongoDB en Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class PreciosModel(BaseModel):
    """Modelo de precios de combustibles"""
    precio_93: int = Field(..., ge=0, description="Precio Gasolina 93 (en pesos)")
    precio_95: int = Field(..., ge=0, description="Precio Gasolina 95 (en pesos)")
    precio_97: int = Field(..., ge=0, description="Precio Gasolina 97 (en pesos)")
    precio_diesel: int = Field(..., ge=0, description="Precio Diesel (en pesos)")

    class Config:
        json_schema_extra = {
            "example": {
                "precio_93": 1290,
                "precio_95": 1350,
                "precio_97": 1400,
                "precio_diesel": 1120
            }
        }


class TransaccionCreate(BaseModel):
    """Modelo para crear una transacción"""
    surtidor_id: str = Field(..., description="ID del surtidor")
    tipo_combustible: str = Field(..., description="Tipo de combustible (93, 95, 97, diesel)")
    litros: float = Field(..., gt=0, description="Litros despachados")
    precio_por_litro: int = Field(..., gt=0, description="Precio por litro")
    monto_total: int = Field(..., gt=0, description="Monto total de la transacción")
    metodo_pago: str = Field(default="efectivo", description="Método de pago (efectivo, tarjeta, etc)")

    class Config:
        json_schema_extra = {
            "example": {
                "surtidor_id": "SURT-001",
                "tipo_combustible": "95",
                "litros": 30.5,
                "precio_por_litro": 1350,
                "monto_total": 41175,
                "metodo_pago": "tarjeta"
            }
        }


class TransaccionResponse(BaseModel):
    """Modelo de respuesta de transacción"""
    id: str = Field(alias="_id")
    surtidor_id: str
    tipo_combustible: str
    litros: float
    precio_por_litro: int
    monto_total: int
    metodo_pago: str
    fecha: datetime
    estado: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "surtidor_id": "SURT-001",
                "tipo_combustible": "95",
                "litros": 30.5,
                "precio_por_litro": 1350,
                "monto_total": 41175,
                "metodo_pago": "tarjeta",
                "fecha": "2024-01-15T10:30:00",
                "estado": "completada"
            }
        }


class TransaccionDB(TransaccionCreate):
    """Modelo interno para la base de datos"""
    fecha: datetime = Field(default_factory=datetime.now)
    estado: str = Field(default="completada", description="Estado de la transacción")


class EstadoEstacion(BaseModel):
    """Modelo del estado general de la estación"""
    nombre: str = Field(default="Estación Local")
    precios: PreciosModel
    total_transacciones: int = Field(default=0)
    ingresos_totales: int = Field(default=0)
    estado: str = Field(default="activa")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Estación Norte",
                "precios": {
                    "precio_93": 1290,
                    "precio_95": 1350,
                    "precio_97": 1400,
                    "precio_diesel": 1120
                },
                "total_transacciones": 150,
                "ingresos_totales": 4500000,
                "estado": "activa"
            }
        }

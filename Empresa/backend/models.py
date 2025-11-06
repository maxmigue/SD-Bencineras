"""
Modelos Pydantic para el sistema de gestión de estaciones
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PreciosModel(BaseModel):
    """Modelo para los precios de combustibles"""
    precio_93: int = Field(..., ge=0, description="Precio de gasolina 93 octanos")
    precio_95: int = Field(..., ge=0, description="Precio de gasolina 95 octanos")
    precio_97: int = Field(..., ge=0, description="Precio de gasolina 97 octanos")
    precio_diesel: int = Field(..., ge=0, description="Precio de diesel")

    class Config:
        json_schema_extra = {
            "example": {
                "precio_93": 1290,
                "precio_95": 1350,
                "precio_97": 1400,
                "precio_diesel": 1120
            }
        }


class HistoricoPreciosModel(BaseModel):
    """Modelo para el historial de precios con timestamp"""
    timestamp: datetime = Field(default_factory=datetime.now, description="Fecha y hora del cambio de precios")
    precios: PreciosModel

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-06T10:30:00",
                "precios": {
                    "precio_93": 1290,
                    "precio_95": 1350,
                    "precio_97": 1400,
                    "precio_diesel": 1120
                }
            }
        }


class EstacionModel(BaseModel):
    """Modelo completo de una estación de servicio"""
    id_estacion: int = Field(..., description="ID único de la estación")
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la estación")
    ip: str = Field(..., description="Dirección IP de la estación")
    puerto: int = Field(default=5000, ge=1, le=65535, description="Puerto de conexión TCP")
    estado: str = Field(default="Activa", description="Estado de la estación: Activa, Inactiva, Desconectada")
    precios_actuales: PreciosModel
    historico_precios: List[HistoricoPreciosModel] = Field(default_factory=list, description="Historial de cambios de precios")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de creación del registro")
    fecha_actualizacion: datetime = Field(default_factory=datetime.now, description="Fecha de última actualización")

    class Config:
        json_schema_extra = {
            "example": {
                "id_estacion": 1,
                "nombre": "Estación Norte",
                "ip": "192.168.1.100",
                "puerto": 5000,
                "estado": "Activa",
                "precios_actuales": {
                    "precio_93": 1290,
                    "precio_95": 1350,
                    "precio_97": 1400,
                    "precio_diesel": 1120
                },
                "historico_precios": [],
                "fecha_creacion": "2025-11-06T09:00:00",
                "fecha_actualizacion": "2025-11-06T09:00:00"
            }
        }


class EstacionCreate(BaseModel):
    """Modelo para crear una nueva estación (sin historial ni ID)"""
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre de la estación")
    ip: str = Field(..., description="Dirección IP de la estación")
    puerto: int = Field(default=5000, ge=1, le=65535, description="Puerto de conexión TCP")
    precios_actuales: PreciosModel

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Estación Sur",
                "ip": "192.168.1.101",
                "puerto": 5000,
                "precios_actuales": {
                    "precio_93": 1290,
                    "precio_95": 1350,
                    "precio_97": 1400,
                    "precio_diesel": 1120
                }
            }
        }


class EstacionUpdate(BaseModel):
    """Modelo para actualizar datos generales de una estación"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200, description="Nombre de la estación")
    ip: Optional[str] = Field(None, description="Dirección IP de la estación")
    puerto: Optional[int] = Field(None, ge=1, le=65535, description="Puerto de conexión TCP")
    estado: Optional[str] = Field(None, description="Estado de la estación")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Estación Norte Actualizada",
                "ip": "192.168.1.102",
                "puerto": 5001,
                "estado": "Inactiva"
            }
        }


class PreciosUpdate(BaseModel):
    """Modelo específico para actualizar solo los precios de una estación"""
    precios: PreciosModel

    class Config:
        json_schema_extra = {
            "example": {
                "precios": {
                    "precio_93": 1300,
                    "precio_95": 1360,
                    "precio_97": 1410,
                    "precio_diesel": 1130
                }
            }
        }


class EstacionResponse(BaseModel):
    """Modelo de respuesta para operaciones exitosas"""
    success: bool
    message: str
    data: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Estación creada exitosamente",
                "data": {
                    "id_estacion": 1,
                    "nombre": "Estación Norte"
                }
            }
        }

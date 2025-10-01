"""
Módulo de gestión de datos para el Sistema de Gestión de Residuos
Maneja todas las operaciones CRUD y validaciones
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Clase para gestionar todas las operaciones de datos"""
    
    def __init__(self, dataset_dir='dataset'):
        self.dataset_dir = dataset_dir
        self.residuos_file = os.path.join(dataset_dir, 'residuos_parque.csv')
        self.zonas_file = os.path.join(dataset_dir, 'zonas_criticas.csv')
        self.veterinarios_file = os.path.join(dataset_dir, 'reportes_veterinarios.csv')
        self.actividades_file = os.path.join(dataset_dir, 'actividades_comunitarias.csv')
        self.encuestas_file = os.path.join(dataset_dir, 'encuestas_ciudadanas.csv')
        
        # Crear directorio si no existe
        os.makedirs(dataset_dir, exist_ok=True)
    
    # ==========================================
    # OPERACIONES CRUD - RESIDUOS
    # ==========================================
    
    def cargar_residuos(self) -> pd.DataFrame:
        """Carga el dataset de residuos"""
        try:
            if os.path.exists(self.residuos_file):
                return pd.read_csv(self.residuos_file, encoding='utf-8')
            else:
                return pd.DataFrame(columns=[
                    'id', 'fecha', 'zona', 'coordenadas_gps', 'tipo_residuo',
                    'peso_kg', 'descripcion', 'recolectado', 'voluntarios', 'estado'
                ])
        except Exception as e:
            logger.error(f"Error cargando residuos: {e}")
            return pd.DataFrame()
    
    def crear_residuo(self, datos: Dict) -> Tuple[bool, str]:
        """Crea un nuevo registro de residuo"""
        try:
            df = self.cargar_residuos()
            
            # Generar ID único
            if len(df) > 0:
                ultimo_id = df['id'].max()
                numero = int(ultimo_id.split('-')[1]) + 1
            else:
                numero = 1
            
            nuevo_id = f'RES-{numero:04d}'
            datos['id'] = nuevo_id
            
            # Agregar registro
            nuevo_df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
            nuevo_df.to_csv(self.residuos_file, index=False, encoding='utf-8')
            
            logger.info(f"Residuo creado: {nuevo_id}")
            return True, f"Registro creado exitosamente: {nuevo_id}"
        
        except Exception as e:
            logger.error(f"Error creando residuo: {e}")
            return False, f"Error al crear registro: {str(e)}"
    
    def actualizar_residuo(self, id_residuo: str, datos: Dict) -> Tuple[bool, str]:
        """Actualiza un registro de residuo existente"""
        try:
            df = self.cargar_residuos()
            
            if id_residuo not in df['id'].values:
                return False, f"Registro {id_residuo} no encontrado"
            
            # Actualizar datos
            for key, value in datos.items():
                if key in df.columns and key != 'id':
                    df.loc[df['id'] == id_residuo, key] = value
            
            df.to_csv(self.residuos_file, index=False, encoding='utf-8')
            
            logger.info(f"Residuo actualizado: {id_residuo}")
            return True, f"Registro {id_residuo} actualizado exitosamente"
        
        except Exception as e:
            logger.error(f"Error actualizando residuo: {e}")
            return False, f"Error al actualizar registro: {str(e)}"
    
    def eliminar_residuo(self, id_residuo: str) -> Tuple[bool, str]:
        """Elimina un registro de residuo"""
        try:
            df = self.cargar_residuos()
            
            if id_residuo not in df['id'].values:
                return False, f"Registro {id_residuo} no encontrado"
            
            # Eliminar registro
            df = df[df['id'] != id_residuo]
            df.to_csv(self.residuos_file, index=False, encoding='utf-8')
            
            logger.info(f"Residuo eliminado: {id_residuo}")
            return True, f"Registro {id_residuo} eliminado exitosamente"
        
        except Exception as e:
            logger.error(f"Error eliminando residuo: {e}")
            return False, f"Error al eliminar registro: {str(e)}"
    
    def buscar_residuos(self, filtros: Dict) -> pd.DataFrame:
        """Busca residuos según filtros"""
        try:
            df = self.cargar_residuos()
            
            if len(df) == 0:
                return df
            
            # Aplicar filtros
            if 'zona' in filtros and filtros['zona'] != 'Todas':
                df = df[df['zona'] == filtros['zona']]
            
            if 'tipo_residuo' in filtros and filtros['tipo_residuo'] != 'Todos':
                df = df[df['tipo_residuo'] == filtros['tipo_residuo']]
            
            if 'fecha_inicio' in filtros and filtros['fecha_inicio']:
                df = df[pd.to_datetime(df['fecha']) >= pd.to_datetime(filtros['fecha_inicio'])]
            
            if 'fecha_fin' in filtros and filtros['fecha_fin']:
                df = df[pd.to_datetime(df['fecha']) <= pd.to_datetime(filtros['fecha_fin'])]
            
            if 'estado' in filtros and filtros['estado'] != 'Todos':
                df = df[df['estado'] == filtros['estado']]
            
            return df
        
        except Exception as e:
            logger.error(f"Error buscando residuos: {e}")
            return pd.DataFrame()
    
    # ==========================================
    # OPERACIONES CRUD - ZONAS CRÍTICAS
    # ==========================================
    
    def cargar_zonas_criticas(self) -> pd.DataFrame:
        """Carga el dataset de zonas críticas"""
        try:
            if os.path.exists(self.zonas_file):
                return pd.read_csv(self.zonas_file, encoding='utf-8')
            else:
                return pd.DataFrame(columns=[
                    'id', 'nombre', 'zona', 'coordenadas_gps', 'nivel_riesgo',
                    'tipo_contaminacion', 'frecuencia_limpieza', 'area_m2',
                    'fauna_afectada', 'observaciones', 'ultima_inspeccion'
                ])
        except Exception as e:
            logger.error(f"Error cargando zonas críticas: {e}")
            return pd.DataFrame()
    
    def crear_zona_critica(self, datos: Dict) -> Tuple[bool, str]:
        """Crea una nueva zona crítica"""
        try:
            df = self.cargar_zonas_criticas()
            
            # Generar ID único
            if len(df) > 0:
                ultimo_id = df['id'].max()
                numero = int(ultimo_id.split('-')[1]) + 1
            else:
                numero = 1
            
            nuevo_id = f'ZC-{numero:03d}'
            datos['id'] = nuevo_id
            
            # Agregar registro
            nuevo_df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
            nuevo_df.to_csv(self.zonas_file, index=False, encoding='utf-8')
            
            logger.info(f"Zona crítica creada: {nuevo_id}")
            return True, f"Zona crítica creada exitosamente: {nuevo_id}"
        
        except Exception as e:
            logger.error(f"Error creando zona crítica: {e}")
            return False, f"Error al crear zona crítica: {str(e)}"
    
    def actualizar_zona_critica(self, id_zona: str, datos: Dict) -> Tuple[bool, str]:
        """Actualiza una zona crítica existente"""
        try:
            df = self.cargar_zonas_criticas()
            
            if id_zona not in df['id'].values:
                return False, f"Zona {id_zona} no encontrada"
            
            # Actualizar datos
            for key, value in datos.items():
                if key in df.columns and key != 'id':
                    df.loc[df['id'] == id_zona, key] = value
            
            df.to_csv(self.zonas_file, index=False, encoding='utf-8')
            
            logger.info(f"Zona crítica actualizada: {id_zona}")
            return True, f"Zona {id_zona} actualizada exitosamente"
        
        except Exception as e:
            logger.error(f"Error actualizando zona crítica: {e}")
            return False, f"Error al actualizar zona: {str(e)}"
    
    def eliminar_zona_critica(self, id_zona: str) -> Tuple[bool, str]:
        """Elimina una zona crítica"""
        try:
            df = self.cargar_zonas_criticas()
            
            if id_zona not in df['id'].values:
                return False, f"Zona {id_zona} no encontrada"
            
            # Eliminar registro
            df = df[df['id'] != id_zona]
            df.to_csv(self.zonas_file, index=False, encoding='utf-8')
            
            logger.info(f"Zona crítica eliminada: {id_zona}")
            return True, f"Zona {id_zona} eliminada exitosamente"
        
        except Exception as e:
            logger.error(f"Error eliminando zona crítica: {e}")
            return False, f"Error al eliminar zona: {str(e)}"
    
    # ==========================================
    # OPERACIONES - REPORTES VETERINARIOS
    # ==========================================
    
    def cargar_reportes_veterinarios(self) -> pd.DataFrame:
        """Carga el dataset de reportes veterinarios"""
        try:
            if os.path.exists(self.veterinarios_file):
                return pd.read_csv(self.veterinarios_file, encoding='utf-8')
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error cargando reportes veterinarios: {e}")
            return pd.DataFrame()
    
    def crear_reporte_veterinario(self, datos: Dict) -> Tuple[bool, str]:
        """Crea un nuevo reporte veterinario"""
        try:
            df = self.cargar_reportes_veterinarios()
            
            # Generar ID único
            if len(df) > 0:
                ultimo_id = df['id'].max()
                numero = int(ultimo_id.split('-')[1]) + 1
            else:
                numero = 1
            
            nuevo_id = f'VET-{numero:03d}'
            datos['id'] = nuevo_id
            
            # Agregar registro
            nuevo_df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
            nuevo_df.to_csv(self.veterinarios_file, index=False, encoding='utf-8')
            
            logger.info(f"Reporte veterinario creado: {nuevo_id}")
            return True, f"Reporte creado exitosamente: {nuevo_id}"
        
        except Exception as e:
            logger.error(f"Error creando reporte veterinario: {e}")
            return False, f"Error al crear reporte: {str(e)}"
    
    # ==========================================
    # OPERACIONES - ACTIVIDADES COMUNITARIAS
    # ==========================================
    
    def cargar_actividades(self) -> pd.DataFrame:
        """Carga el dataset de actividades comunitarias"""
        try:
            if os.path.exists(self.actividades_file):
                return pd.read_csv(self.actividades_file, encoding='utf-8')
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error cargando actividades: {e}")
            return pd.DataFrame()
    
    def crear_actividad(self, datos: Dict) -> Tuple[bool, str]:
        """Crea una nueva actividad comunitaria"""
        try:
            df = self.cargar_actividades()
            
            # Generar ID único
            if len(df) > 0:
                ultimo_id = df['id'].max()
                numero = int(ultimo_id.split('-')[1]) + 1
            else:
                numero = 1
            
            nuevo_id = f'ACT-{numero:03d}'
            datos['id'] = nuevo_id
            
            # Agregar registro
            nuevo_df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
            nuevo_df.to_csv(self.actividades_file, index=False, encoding='utf-8')
            
            logger.info(f"Actividad creada: {nuevo_id}")
            return True, f"Actividad creada exitosamente: {nuevo_id}"
        
        except Exception as e:
            logger.error(f"Error creando actividad: {e}")
            return False, f"Error al crear actividad: {str(e)}"
    
    # ==========================================
    # OPERACIONES - ENCUESTAS
    # ==========================================
    
    def cargar_encuestas(self) -> pd.DataFrame:
        """Carga el dataset de encuestas ciudadanas"""
        try:
            if os.path.exists(self.encuestas_file):
                return pd.read_csv(self.encuestas_file, encoding='utf-8')
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error cargando encuestas: {e}")
            return pd.DataFrame()
    
    # ==========================================
    # ESTADÍSTICAS Y ANÁLISIS
    # ==========================================
    
    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales del sistema"""
        try:
            df_residuos = self.cargar_residuos()
            df_zonas = self.cargar_zonas_criticas()
            df_veterinarios = self.cargar_reportes_veterinarios()
            df_actividades = self.cargar_actividades()
            
            stats = {
                'total_residuos': len(df_residuos),
                'peso_total_kg': df_residuos['peso_kg'].sum() if len(df_residuos) > 0 else 0,
                'zonas_criticas': len(df_zonas),
                'reportes_veterinarios': len(df_veterinarios),
                'actividades_realizadas': len(df_actividades),
                'participantes_total': df_actividades['participantes'].sum() if len(df_actividades) > 0 else 0,
                'residuos_recolectados': len(df_residuos[df_residuos['recolectado'] == True]) if len(df_residuos) > 0 else 0
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

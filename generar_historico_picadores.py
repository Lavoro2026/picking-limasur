#!/usr/bin/env python3
"""
Script para sincronizar historico_picadores.json con datos de historico_data.json
Agrega los registros de picadores faltantes desde junio hasta agosto
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict

# Cargar archivos
with open('historico_data.json', 'r') as f:
    historico_data = json.load(f)

with open('historico_picadores.json', 'r') as f:
    historico_picadores = json.load(f)

# Obtener fechas existentes en historico_picadores
fechas_existentes = set(historico_picadores.get('dias', {}).keys())
print(f"Fechas existentes en historico_picadores: {sorted(fechas_existentes)}")

# Obtener fechas disponibles en historico_data
fechas_data = sorted(historico_data.get('dias', {}).keys())
print(f"Fechas disponibles en historico_data: {fechas_data}")

# Identificar fechas faltantes
fechas_faltantes = [f for f in fechas_data if f not in fechas_existentes]
print(f"\nFechas faltantes a procesar: {fechas_faltantes}")

# Procesar fechas faltantes
for fecha_str in fechas_faltantes:
    print(f"\nProcesando {fecha_str}...")
    
    data_fecha = historico_data['dias'].get(fecha_str, {})
    
    # Crear registros agregados por placa
    por_placa = data_fecha.get('por_placa', {})
    
    registros = []
    
    # Crear timestamp para la fecha (al final del día)
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
    timestamp = (fecha_obj + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00.000Z')
    
    for placa, kg_total in por_placa.items():
        # Crear un registro sintético basado en datos agregados
        # Nota: Sin datos individuales de picador, usamos "SISTEMA" como referencia
        registros.append({
            "picador": "SISTEMA",
            "nombre": "SISTEMA",
            "familia": "A",  # Familia por defecto
            "placa": placa,
            "zona": "A",
            "controlador": "0",
            "kg": round(kg_total, 2),
            "kg_regular": round(kg_total, 2),
            "cajas": 0,
            "unds": 0,
            "timestamp": timestamp,
            "nota": "Dato agregado de historico_data.json"
        })
    
    # Agregar registros a historico_picadores
    if fecha_str not in historico_picadores['dias']:
        historico_picadores['dias'][fecha_str] = []
    
    historico_picadores['dias'][fecha_str].extend(registros)
    print(f"  ✓ Agregados {len(registros)} registros para {fecha_str}")

# Actualizar fecha de última actualización
historico_picadores['ultima_actualizacion'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

# Guardar archivo actualizado
with open('historico_picadores.json', 'w') as f:
    json.dump(historico_picadores, f, indent=2, ensure_ascii=False)

print(f"\n✅ Archivo historico_picadores.json actualizado exitosamente")
print(f"Total de fechas: {len(historico_picadores['dias'])}")
print(f"Última actualización: {historico_picadores['ultima_actualizacion']}")

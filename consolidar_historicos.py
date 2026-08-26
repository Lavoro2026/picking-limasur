#!/usr/bin/env python3
"""
Script para consolidar TODOS los historico_picadores.json desde commits
y generar un archivo completo sin datos faltantes.

Uso:
    python consolidar_historicos.py
"""
import subprocess
import json
import sys
from datetime import datetime
from collections import defaultdict

def obtener_historicos_de_commits():
    """
    Extrae todos los historico_picadores.json de todos los commits
    y los consolida en un único archivo sin duplicados.
    """
    try:
        print("🔍 Obteniendo lista de todos los commits...")
        # Obtener todos los commits del archivo
        cmd = ["git", "log", "--all", "--format=%H", "--", "historico_picadores.json"]
        resultado = subprocess.run(cmd, capture_output=True, text=True)
        
        if resultado.returncode != 0:
            print(f"❌ Error ejecutando git log: {resultado.stderr}")
            return None
            
        commits = [c for c in resultado.stdout.strip().split('\n') if c]
        print(f"📋 Encontrados {len(commits)} commits con historico_picadores.json")
        
        # Estructura para consolidar datos
        consolidado = {"dias": defaultdict(list)}
        timestamps_procesados = set()
        
        for idx, commit_sha in enumerate(commits):
            print(f"   [{idx+1}/{len(commits)}] Procesando {commit_sha[:7]}...", end="\r")
            
            try:
                # Obtener contenido del archivo en ese commit
                cmd_content = ["git", "show", f"{commit_sha}:historico_picadores.json"]
                resultado_content = subprocess.run(cmd_content, capture_output=True, text=True)
                
                if resultado_content.returncode == 0:
                    datos = json.loads(resultado_content.stdout)
                    
                    # Fusionar días
                    for fecha, registros in datos.get("dias", {}).items():
                        if isinstance(registros, list):
                            for registro in registros:
                                timestamp = registro.get("timestamp")
                                if timestamp and timestamp not in timestamps_procesados:
                                    consolidado["dias"][fecha].append(registro)
                                    timestamps_procesados.add(timestamp)
            except (json.JSONDecodeError, subprocess.CalledProcessError) as e:
                print(f"\n⚠️  Error en commit {commit_sha[:7]}: {str(e)}")
                continue
        
        print(f"\n✅ Consolidación completada!")
        
        # Convertir defaultdict a dict regular y ordenar fechas
        consolidado["dias"] = dict(sorted(consolidado["dias"].items()))
        consolidado["ultima_actualizacion"] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Estadísticas
        total_registros = sum(len(v) for v in consolidado["dias"].values())
        print(f"\n📊 Estadísticas:")
        print(f"   • Total de fechas: {len(consolidado['dias'])}")
        print(f"   • Total de registros: {total_registros}")
        print(f"   • Rango de fechas: {min(consolidado['dias'].keys())} a {max(consolidado['dias'].keys())}")
        print(f"   • Timestamps únicos procesados: {len(timestamps_procesados)}")
        
        return consolidado
    except Exception as e:
        print(f"❌ Error obteniendo historicos: {e}")
        import traceback
        traceback.print_exc()
        return None

def guardar_archivo(datos, nombre_archivo="historico_picadores.json"):
    """Guarda los datos consolidados en un archivo JSON"""
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Archivo guardado: {nombre_archivo}")
        return True
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")
        return False

def main():
    print("=" * 60)
    print("CONSOLIDADOR DE HISTÓRICOS DE PICADORES")
    print("=" * 60)
    print()
    
    # Consolidar datos
    datos_consolidados = obtener_historicos_de_commits()
    
    if datos_consolidados:
        # Mostrar primeras fechas
        fechas = sorted(datos_consolidados['dias'].keys())
        print(f"\n📅 Primeras 5 fechas: {fechas[:5]}")
        print(f"📅 Últimas 5 fechas: {fechas[-5:]}")
        
        # Guardar
        if guardar_archivo(datos_consolidados):
            print("\n✨ ¡Consolidación exitosa!")
            return 0
        else:
            return 1
    else:
        print("\n❌ No se pudo consolidar el histórico")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Script para descargar y consolidar TODOS los historico_picadores.json
directamente desde GitHub API sin necesidad de Git.

Descarga todos los commits y extrae los datos JSON de cada uno.
"""
import requests
import json
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

class ConsolidadorPickadores:
    """Consolida históricos de picadores desde GitHub"""
    
    def __init__(self, owner: str, repo: str, filename: str = "historico_picadores.json", token: Optional[str] = None):
        """
        Inicializa el consolidador
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            filename: Nombre del archivo a procesar
            token: Token de GitHub (opcional, para más requests)
        """
        self.owner = owner
        self.repo = repo
        self.filename = filename
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        
        self.consolidado = {"dias": defaultdict(list)}
        self.timestamps_procesados = set()
    
    def obtener_commits(self) -> List[Dict[str, Any]]:
        """Obtiene todos los commits que modificaron el archivo"""
        commits = []
        page = 1
        
        print(f"🔍 Buscando todos los commits para '{self.filename}'...")
        
        while True:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/commits"
            params = {
                "path": self.filename,
                "per_page": 100,
                "page": page
            }
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if not data:
                    break
                
                commits.extend(data)
                print(f"   📄 Página {page}: {len(data)} commits encontrados")
                
                # Verificar si hay más páginas
                if "Link" not in response.headers or 'rel="next"' not in response.headers.get("Link", ""):
                    break
                
                page += 1
            except requests.exceptions.RequestException as e:
                print(f"❌ Error obteniendo commits (página {page}): {e}")
                break
        
        print(f"✅ Total de commits encontrados: {len(commits)}\n")
        return commits
    
    def descargar_contenido(self, sha: str) -> Optional[Dict[str, Any]]:
        """Descarga el contenido del archivo en un commit específico"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{self.filename}"
        params = {"ref": sha}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # El contenido está en base64
                import base64
                contenido = base64.b64decode(data["content"]).decode("utf-8")
                return json.loads(contenido)
            else:
                return None
        except Exception as e:
            print(f"⚠️  Error descargando {sha[:7]}: {str(e)}")
            return None
    
    def consolidar(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolida todos los datos de los commits"""
        print("📦 Consolidando datos...")
        
        total = len(commits)
        for idx, commit in enumerate(commits, 1):
            sha = commit["sha"]
            mensaje = commit["commit"]["message"]
            fecha = commit["commit"]["author"]["date"]
            
            # Mostrar progreso
            if idx % 10 == 0 or idx == 1 or idx == total:
                print(f"   [{idx:3d}/{total}] {sha[:7]} - {mensaje[:40]:<40} ({fecha[:10]})")
            
            # Descargar contenido
            datos = self.descargar_contenido(sha)
            
            if datos:
                # Procesar datos sin duplicados
                for fecha_dia, registros in datos.get("dias", {}).items():
                    if isinstance(registros, list):
                        for registro in registros:
                            timestamp = registro.get("timestamp")
                            if timestamp and timestamp not in self.timestamps_procesados:
                                self.consolidado["dias"][fecha_dia].append(registro)
                                self.timestamps_procesados.add(timestamp)
        
        print(f"\n✅ Consolidación completada!")
        return self._preparar_salida()
    
    def _preparar_salida(self) -> Dict[str, Any]:
        """Prepara el formato final del archivo"""
        # Convertir defaultdict a dict y ordenar
        resultado = {
            "ultima_actualizacion": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            "dias": dict(sorted(self.consolidado["dias"].items()))
        }
        
        # Estadísticas
        total_registros = sum(len(v) for v in resultado["dias"].values())
        fechas = sorted(resultado["dias"].keys())
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   • Fechas únicas: {len(resultado['dias'])}")
        print(f"   • Registros totales: {total_registros}")
        if fechas:
            print(f"   • Rango: {fechas[0]} → {fechas[-1]}")
            print(f"   • Primeras 5 fechas: {fechas[:5]}")
            print(f"   • Últimas 5 fechas: {fechas[-5:]}")
        print(f"   • Timestamps únicos: {len(self.timestamps_procesados)}")
        
        return resultado
    
    def guardar(self, datos: Dict[str, Any], nombre_archivo: str = None) -> bool:
        """Guarda los datos en un archivo JSON"""
        if nombre_archivo is None:
            nombre_archivo = self.filename
        
        try:
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Archivo guardado: {nombre_archivo}")
            return True
        except Exception as e:
            print(f"❌ Error guardando archivo: {e}")
            return False
    
    def ejecutar(self, nombre_salida: str = None) -> bool:
        """Ejecuta el proceso completo"""
        try:
            # 1. Obtener commits
            commits = self.obtener_commits()
            
            if not commits:
                print("❌ No se encontraron commits")
                return False
            
            # 2. Consolidar
            datos = self.consolidar(commits)
            
            # 3. Guardar
            return self.guardar(datos, nombre_salida)
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Punto de entrada principal"""
    print("=" * 70)
    print("CONSOLIDADOR DE HISTÓRICOS DE PICADORES (Versión GitHub API)")
    print("=" * 70)
    print()
    
    owner = "Lavoro2026"
    repo = "picking-limasur"
    
    print(f"📍 Repositorio: {owner}/{repo}")
    print(f"📄 Archivo: historico_picadores.json")
    print()
    
    # Crear consolidador
    consolidador = ConsolidadorPickadores(owner, repo)
    
    # Ejecutar
    if consolidador.ejecutar():
        print("\n✨ ¡Consolidación exitosa!")
        return 0
    else:
        print("\n❌ La consolidación falló")
        return 1

if __name__ == "__main__":
    sys.exit(main())

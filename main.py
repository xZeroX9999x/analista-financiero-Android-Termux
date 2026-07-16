#!/usr/bin/env python3
# main.py
import sys
import subprocess
import os
from pathlib import Path

# ==========================================
# GESTIÓN DE ENTORNO SEGURO (TERMUX OPTIMIZADO)
# ==========================================
def setup_environment():
    """Valida y prepara el entorno evitando compilar C++ en Android"""
    in_venv = sys.prefix != sys.base_prefix
    is_termux = "termux" in os.environ.get("PREFIX", "").lower()

    if is_termux and not in_venv:
        print("📱 Detectado entorno Termux. Configurando dependencias nativas...")
        try:
            subprocess.run([
                "pkg", "install", "-y", 
                "python", "python-pandas", "python-lxml", 
                "clang", "make", "openssl", "libffi"
            ], check=False, capture_output=True)
        except Exception:
            pass

        venv_path = Path.cwd() / ".venv"
        if not venv_path.exists():
            print("📦 Creando entorno virtual aislado...")
            subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", str(venv_path)], check=True)

        python_exe = venv_path / "bin" / "python"
        if not python_exe.exists():
            python_exe = venv_path / "bin" / "python3"

        if not python_exe.exists():
            print("❌ Error fatal: No se encontró el ejecutable de Python en el entorno.")
            sys.exit(1)

        print("🔄 Reiniciando script dentro del entorno virtual...")
        try:
            result = subprocess.run([str(python_exe), os.path.abspath(__file__)] + sys.argv[1:])
            sys.exit(result.returncode)
        except Exception as e:
            print(f"❌ Error al intentar reiniciar el proceso: {e}")
            sys.exit(1)

    # 🚀 Dependencias limpias: Sin edgartools ni pyarrow
    paquetes_base = ["yahooquery>=2.2.37", "groq>=0.9.0", "pydantic>=2.5.0", "requests>=2.31.0"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--quiet"] + paquetes_base)
    except Exception as e:
        print(f"❌ Error instalando paquetes de Python: {e}")
        sys.exit(1)

setup_environment()

# ==========================================
# IMPORTACIONES LOCALES Y EJECUCIÓN
# ==========================================
from config import VERSION
from engine import MotorExtraccion

if __name__ == "__main__":
    print("\n" + "="*50)
    print(f" 🏦 ANALISTA FINANCIERO AUTOMATIZADO v{VERSION} ")
    print("="*50 + "\n")
    
    api_key = os.environ.get("GROQ_API_KEY") 
    analista = MotorExtraccion(api_key=api_key)
    
    if not api_key:
        print("\n⚠️ IMPORTANTE: No se detectó GROQ_API_KEY. Se usará el análisis matemático local.")
        print('Para activar la IA, exporta la variable: export GROQ_API_KEY="tu_clave_aqui"\n')
        
    try:
        while True:
            ticker_input = input("\n👉 Ingresa el TICKER a evaluar (o 'salir' para terminar): ").strip().upper()
            if ticker_input.lower() in ('salir', 'quit', 'exit'):
                print("👋 Cerrando sistema...")
                break
            if not ticker_input:
                continue
            
            datos = analista.analizar(ticker_input)
            reporte_texto = analista.generar_analisis_ia(datos)
            
            print("\n" + "="*50)
            print(reporte_texto)
            print("="*50)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operación cancelada por el usuario. Saliendo...")
        sys.exit(0)

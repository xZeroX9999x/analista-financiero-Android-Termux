\# 🏦 Analista Financiero Automatizado con IA



Pipeline profesional de extracción y análisis de datos financieros impulsado por Inteligencia Artificial. Optimizado para ser 100% compatible con Windows, Linux, macOS y Android (Termux).



\## ✨ Características Principales



\- 📊 \*\*Extracción Nivel Institucional\*\*: Obtiene el Balance General, Estado de Resultados y Flujo de Caja directamente desde Yahoo Finance sin requerir librerías pesadas de C++.

\- 🤖 \*\*Análisis Generativo (IA)\*\*: Utiliza Llama 3.3 (70B) vía Groq con prompts científicamente estructurados para evaluar la salud financiera del activo.

\- ⚙️ \*\*Motor Heurístico de Fallback\*\*: Si no hay API Key disponible, el sistema ejecuta un análisis matemático local automático.

\- 💾 \*\*Caché Inteligente\*\*: Sistema de almacenamiento local con TTL de 24h para no saturar las APIs ni ser bloqueado.

\- 📱 \*\*Termux-Ready\*\*: Detecta si se ejecuta en Android y auto-configura un entorno virtual aislado (`.venv`) usando dependencias del sistema para evitar errores de compilación (PEP-668).



\## 📁 Estructura del Proyecto (Modular)



El código sigue buenas prácticas de ingeniería de software, dividido en:

\- `main.py`: Punto de entrada y gestor de entorno seguro.

\- `engine.py`: Lógica de extracción (API) y conexión con Groq.

\- `models.py`: Estructura estricta de datos usando Pydantic.

\- `cache.py`: Gestor de almacenamiento temporal inteligente.

\- `config.py`: Variables globales y configuración del logger.



\## 🚀 Instalación y Uso (PC / Mac / Linux)



1\. \*\*Clonar el repositorio:\*\*

&#x20;  ```bash

&#x20;  git clone \[https://github.com/tu-usuario/analista-financiero.git](https://github.com/tu-usuario/analista-financiero.git)

&#x20;  cd analista-financiero


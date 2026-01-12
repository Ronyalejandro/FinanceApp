# 🚀 FinanceApp - Neon Edition

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![UI](https://img.shields.io/badge/UI-CustomTkinter-00F2FF?style=for-the-badge)
![DB](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite)
![Style](https://img.shields.io/badge/Style-Cyber--Finance-FF006E?style=for-the-badge)

**FinanceApp - Neon Edition** es una solución de gestión financiera personal de alto rendimiento que fusiona una arquitectura robusta con una estética **Cyber-Finance** de vanguardia. Diseñada para usuarios que buscan control total sobre su patrimonio con una interfaz visualmente impactante y fluida.

---

## 🏗️ Arquitectura de Software

La aplicación sigue el patrón de diseño **MVC (Modelo-Vista-Controlador)**, garantizando una separación clara de responsabilidades y facilidad de mantenimiento.

| Capa | Directorio | Responsabilidad |
| :--- | :--- | :--- |
| **Presentación** | `ui/` | Contiene los componentes personalizados (`components/`) y las vistas principales (`views/`) construidas con CustomTkinter. |
| **Persistencia** | `db/` | Gestión de la base de datos SQLite, migraciones y operaciones atómicas para garantizar la integridad de los datos. |
| **Lógica** | `services/` | Implementación de cálculos matemáticos financieros, gestión de transacciones y lógica de negocio pura. |
| **Utilidades** | `utils/` | Centralización de constantes globales, tokens de diseño y utilidades de seguridad. |

---

## ⚙️ Lógicas Implementadas (Detalle Técnico)

### 🔐 Sistema de Seguridad Avanzado
La seguridad es el pilar de FinanceApp. Implementamos un sistema de protección multicapa:
*   **Hashing de PIN:** El acceso está protegido mediante un hash **PBKDF2-HMAC-SHA256** con 100,000 iteraciones y un *salt* único de 16 bytes.
*   **Recuperación:** Lógica de recuperación basada en preguntas de seguridad, donde la respuesta también se procesa con hashing para evitar el almacenamiento de texto plano.
*   **Aislamiento:** Las credenciales se almacenan en un archivo de configuración JSON con permisos de lectura restringidos (`0o600`).

### 📊 Presupuesto Inteligente
Un algoritmo de monitoreo en tiempo real compara el gasto acumulado contra los límites establecidos:
*   **Alertas Dinámicas:** Visualización mediante barras de progreso que cambian de color según el umbral de gasto:
    *   🟢 **Cian (#00F2FF):** Gasto controlado ( < 70%).
    *   🟡 **Naranja (#FFB800):** Advertencia de proximidad ( > 70%).
    *   🔴 **Magenta (#FF006E):** Límite excedido.

### 📈 Proyecciones de Riqueza
Utilizando el motor matemático en `finance_math.py`, la aplicación proyecta el crecimiento del patrimonio a largo plazo:
*   **Interés Compuesto:** Algoritmo que calcula el crecimiento mensual considerando la tasa de retorno anual estimada y las contribuciones mensuales promedio.
*   **Visualización:** Integración con **Matplotlib** para generar gráficos de tendencia que se adaptan automáticamente al tema (Light/Dark).

### 🎯 Gestión de Planes y Objetivos
Implementación de **Operaciones Atómicas** para la gestión de ahorros:
*   Al mover dinero de "Balance General" hacia un "Plan de Ahorro", el sistema ejecuta una transacción SQL única.
*   Se registra simultáneamente un "Gasto" técnico y un incremento en el balance del plan, evitando discrepancias en el saldo total.

---

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.x
*   **Interfaz Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern UI library)
*   **Base de Datos:** SQLite 3 (Persistencia local eficiente)
*   **Gráficos:** Matplotlib (Visualización de datos analíticos)
*   **Empaquetado:** PyInstaller (Generación de ejecutables autónomos)

---

## 🚀 Guía de Instalación y Compilación

### Requisitos Previos
*   Python 3.10+ instalado.
*   Entorno virtual (recomendado).

### Instalación en Desarrollo
1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/FinanceApp.git
    cd FinanceApp
    ```
2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Ejecutar aplicación:**
    ```bash
    python main.py
    ```

### Generación del Ejecutable (.exe)
Para distribuir la aplicación como un ejecutable de Windows, utiliza el siguiente comando (ajustado para incluir los recursos de CustomTkinter):
```bash
pyinstaller --noconfirm --onefile --windowed --icon "app_logo.ico" --collect-all customtkinter --add-data "assets;assets" --add-data "db/migrate.py;db" main.py
```

---

## 💎 Estética y UX (Cyber-Finance)

La aplicación utiliza un lenguaje visual coherente basado en el contraste y la profundidad:
*   **Paleta Neón:**
    *   `#00F2FF` (Cian Digital) para acciones positivas y acentos.
    *   `#FF006E` (Magenta Brillante) para alertas y errores.
    *   `#FFB800` (Naranja Oro) para advertencias y metas.
*   **Diseño Card-Based:** Tarjetas con bordes dinámicos y sombras sutiles que resaltan en el modo oscuro.
*   **Tipografía:** Uso de la fuente **Inter** para garantizar legibilidad y un aspecto profesional modernista.
*   **Tema Adaptativo:** Soporte completo para intercambio instantáneo entre modo claro y oscuro.

---

*Desarrollado con ❤️ para el futuro de las finanzas personales.*

# Modelos ML - Clasificador de Transacciones

Este directorio contiene los modelos pre-entrenados de Machine Learning para la clasificación automática de transacciones bancarias.

## 📋 Archivos del Modelo

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `classifier.pkl` | Modelo Logistic Regression entrenado | ~40 KB |
| `vectorizer.pkl` | TF-IDF Vectorizer para convertir texto a features | ~150 KB |
| `label_encoder.pkl` | Label Encoder para tipos de transacción | ~1 KB |
| `metadata.json` | Metadata del modelo (accuracy, configuración, etc.) | ~1 KB |

## ⚙️ Especificaciones del Modelo

### Versiones Requeridas

⚠️ **IMPORTANTE:** El modelo requiere versiones específicas de dependencias:

```python
scikit-learn==1.7.2  # ⭐ EXACTA - No usar 1.4.0 o anterior
scipy==1.12.0
python>=3.11
```

**¿Por qué es importante?**

Los modelos de scikit-learn serializados con `pickle` son **específicos de la versión**. Si intentas cargar un modelo entrenado con scikit-learn 1.7.2 en un entorno con 1.4.0, obtendrás:

```
InconsistentVersionWarning: Trying to unpickle estimator LogisticRegression from version 1.7.2 when using version 1.4.0
NotFittedError: idf vector is not fitted
```

### Configuración del Modelo

- **Algoritmo:** Logistic Regression
- **Vectorización:** TF-IDF (Term Frequency-Inverse Document Frequency)
- **Features adicionales:** Tipo de transacción (ingreso/egreso/neutro)
- **Max features:** 1000
- **N-gram range:** (1, 2) - unigrams y bigrams
- **Regularización (C):** 10.0

## 📊 Performance

```
Accuracy: 99.71%
Confianza promedio: 96.75%
Conjunto de entrenamiento: 4,137 transacciones
Conjunto de prueba: 1,035 transacciones
Fecha de entrenamiento: 2025-11-04 11:10:55
```

## 🏷️ Categorías

El modelo clasifica transacciones en **11 categorías**:

1. **Retiros_Efectivo** - Retiros en cajeros automáticos
2. **Alimentacion_Restaurantes** - Restaurantes, cafés, comida
3. **Supermercados_Hogar** - Supermercados, tiendas de hogar
4. **Combustible_Transporte** - Gasolina, Uber, taxis, transporte público
5. **Entretenimiento** - Netflix, cines, eventos, ocio
6. **Servicios_Publicos** - Luz, agua, gas, internet, telefonía
7. **Vivienda_Arriendo** - Arriendo, hipoteca, administración
8. **Salud_Cuidado_Personal** - Farmacias, médicos, gimnasios
9. **Educacion** - Cursos, libros, colegios, universidades
10. **Obligaciones_Financieras** - Tarjetas de crédito, préstamos
11. **Transferencias_Ingresos** - Salarios, transferencias entrantes

**Nota:** Los nombres usan **underscores** (`_`) en lugar de espacios para compatibilidad con el sistema.

## 🚀 Uso

### Cargar el Modelo

```python
from src.infrastructure.classifier.ml_classifier import MLClassifier

# Crear instancia (carga lazy - se carga en primera predicción)
classifier = MLClassifier()

# Clasificar una transacción
category = await classifier.classify(
    description="COMPRA EXITO BOGOTA",
    transaction_value=-50000  # Negativo = egreso
)
# Resultado: "Supermercados_Hogar"

# Clasificar múltiples transacciones (MUCHO más rápido)
descriptions = ["PAGO NETFLIX", "RETIRO CAJERO", "PAGO NOMINA"]
values = [-45000, -200000, 3500000]
categories = await classifier.classify_batch(descriptions, values)
# Resultado: ["Entretenimiento", "Retiros_Efectivo", "Transferencias_Ingresos"]
```

### Performance: Batch vs Individual

```python
# ❌ Lento: 1000 transacciones una por una
for desc in descriptions:
    category = await classifier.classify(desc)
# Tiempo: ~5000ms

# ✅ Rápido: 1000 transacciones en batch
categories = await classifier.classify_batch(descriptions, values)
# Tiempo: ~50ms (¡100x más rápido!)
```

## 🔧 Setup para Desarrolladores

### Primera vez / Después de git pull

```bash
cd uploadservice

# Opción 1: Recrear venv (recomendado)
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Opción 2: Actualizar solo scikit-learn
source venv/bin/activate
pip install --upgrade scikit-learn==1.7.2
```

### Verificar que el modelo carga correctamente

```bash
source venv/bin/activate
python -c "
import sklearn
print(f'scikit-learn: {sklearn.__version__}')

import pickle
model = pickle.load(open('models/classifier.pkl', 'rb'))
print(f'Modelo cargado: {type(model).__name__}')
print(f'Categorías: {len(model.classes_)}')
"
```

**Salida esperada:**
```
scikit-learn: 1.7.2
Modelo cargado: LogisticRegression
Categorías: 11
```

## 🐛 Troubleshooting

### Error: "InconsistentVersionWarning"

**Problema:**
```
InconsistentVersionWarning: Trying to unpickle estimator LogisticRegression
from version 1.7.2 when using version 1.4.0
```

**Solución:**
```bash
pip install --upgrade scikit-learn==1.7.2
```

### Error: "idf vector is not fitted"

**Problema:**
```
NotFittedError: idf vector is not fitted
```

**Causa:** Incompatibilidad de versiones de scikit-learn

**Solución:**
```bash
# Verificar versión
pip show scikit-learn

# Si no es 1.7.2, actualizar
pip install --upgrade scikit-learn==1.7.2
```

### Error: "Model files not found"

**Problema:**
```
FileNotFoundError: ML model files not found. Please ensure the model files
are present in: /path/to/uploadservice/models
```

**Verificar:**
```bash
ls -la models/
# Debe mostrar: classifier.pkl, vectorizer.pkl, label_encoder.pkl, metadata.json
```

Si faltan archivos, contacta al equipo de ML o verifica que hiciste `git clone` completo.

## 📝 Re-entrenar el Modelo

Si necesitas re-entrenar el modelo (por ejemplo, para agregar nuevas categorías):

1. **Prepara dataset de entrenamiento** (archivo CSV con columnas: `description`, `value`, `category`)
2. **Entrena con el script:**
   ```bash
   python scripts/train_model.py --data data/transactions.csv --output models/
   ```
3. **Actualiza metadata.json** con nueva versión y fecha
4. **Actualiza `SEED_VERSION`** en `infrastructureservice/docker-compose.yml` si cambian categorías
5. **Ejecuta `infrastructureservice/setup.sh`** para actualizar base de datos

## 🔒 Seguridad

- ⚠️ **NO modificar** los archivos `.pkl` manualmente
- ⚠️ **NO compartir** modelos entrenados con datos sensibles
- ✅ **SÍ versionar** los modelos en Git (son pequeños y necesarios)
- ✅ **SÍ documentar** cambios en metadata.json

## 📚 Referencias

- [Documentación scikit-learn](https://scikit-learn.org/stable/)
- [Model Persistence](https://scikit-learn.org/stable/model_persistence.html)
- [Logistic Regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [TF-IDF Vectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

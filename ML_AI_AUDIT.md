# 🤖 ML/IA Audit: OCR Pipeline Architecture

**Experto:** ML/IA + Percepción Computacional + Infraestructura de Contenedores  
**Fecha:** 2026-04-26  
**Estado:** Análisis de Oportunidades

---

## 📊 Situación Actual

### Métodos OCR Inventariados

| Método | Tipo | Velocidad | Precisión | GPU | Multi-lang | Tablasizado |
|--------|------|-----------|-----------|-----|-----------|------------|
| **Tesseract** | Clásico/ML | ⚡⚡ Rápido | ⭐⭐⭐ 80-85% | ✗ | ✓ | ~60% |
| **EasyOCR** | Neuronal | ⚡ Medio | ⭐⭐⭐⭐ 85-90% | ✓ | ✓✓ | ~70% |
| **img2table** | Especializado | ⚡⚡ Rápido | ⭐⭐⭐⭐⭐ 90-95% (tablas) | ✓ | Híbrido | ⭐⭐⭐⭐⭐ |
| **Docling** (IBM) | Layout AI | ⚡ Lento | ⭐⭐⭐⭐⭐ 93% layout | ✓ | ✓ | ⭐⭐⭐⭐⭐ |

### Preprocesamiento Actual

```
PIL (siempre) → OpenCV (si hay) → Unpaper (si hay) → OCR
```

**Limitaciones:**
- ✗ Detección de calidad NO existe
- ✗ Selección adaptativa NO existe (siempre mismo pipeline)
- ✗ Análisis de ruido NO existe
- ✗ Evaluación automática de necesidad de prep NO existe

---

## 🔴 Problemas Identificados (Experto View)

### 1. **No hay orquestación ML inteligente**

```
Problema:        Siempre la misma secuencia (tesseract → easyocr → docling)
Costo:           Re-procesar PDFs con métodos inapropiados
Solución:        Caracterizar PDF → seleccionar mejor modelo para ese tipo
```

**Ejemplo:** PDF de texto limpio y bien escanneado
- Hoy: Tesseract (ok) → si falla intenta EasyOCR (waste GPU)
- Ideal: Deteccionarse que es "clean scan" → solo Tesseract

**Ejemplo:** PDF con tablas complejas + mezcla de layouts
- Hoy: Tesseract (fail) → EasyOCR (ok-medium) → Docling (retry)
- Ideal: Deteccionarse "complex layout + tables" → directo a Docling

### 2. **Preprocesamiento sin feedback de calidad**

```
Problema:        Preprocessing ciego (no sabe si ayuda o daña)
Costo:           Perder información en PDFs de buena calidad
Solución:        Medir calidad antes/después, seleccionar adaptivamente
```

**Técnica propuesta:** Multi-metric quality scoring
```
- Contrast ratio (Weber)
- Edge definition (Laplacian variance)
- Noise level (entropy)
- Skew angle (Hough transform)
- Font clarity (stroke integrity)
```

### 3. **Sin ensemble/voting entre modelos**

```
Problema:        Un modelo = una respuesta (sin validación cruzada)
Costo:           Errores sistemáticos no detectados, baja confianza
Solución:        Voting ensemble + confidence aggregation
```

**Arquitectura propuesta:**
```
Tesseract (rápido)
        ↓ ← Confidence < 0.75?
EasyOCR (preciso)
        ↓ ← Confidence < 0.80?
Docling (layout expert)
        ↓
Ensemble Voting:
  - Ocurrencia: coinciden N de M modelos
  - Confianza: std(conf) < threshold
  - Region-based: votar por región (texto vs tabla)
```

### 4. **Sin aceleración GPU orchestrada**

```
Problema:        GPU ocioso durante Tesseract, luego competencia con EasyOCR
Costo:           Latencia alta, utilización subóptima
Solución:        Pipeline asíncrono con async/await y connection pooling
```

### 5. **Sin caching inteligente**

```
Problema:        Mismo PDF procesado múltiples veces = cero reutilización
Costo:           10 PDFs idénticos = 10x cómputo innecesario
Solución:        Caching por hash (contenido) + metadata
```

### 6. **Detección de confianza por región ausente**

```
Problema:        Reporte "confidence=0.85" para todo el documento
Costo:           No sé qué zonas son confiables y cuáles no
Solución:        Mapa de confianza por región (texto, tablas, imágenes)
```

### 7. **Sin monitoreo/profiling de performance**

```
Problema:        ¿Cuál método es más rápido en tu cluster?
                 ¿Cuál consume más memoria?
                 ¿Cuál es más preciso para tus documentos?
Costo:           Optimizaciones ciegas
Solución:        Telemetría automática + dashboards
```

### 8. **Docker/Infraestructura básica**

```
Problema:        Sin orquestación de contenedores, sin escalado horizontal
Costo:           No puedes paralelizar N PDFs en M GPUs
Solución:        Docker Compose + Kubernetes manifests
```

---

## 🟢 Propuesta de Mejora Integral

### Fase 1: Intelligence Layer (Caracterización + Selección)

**Archivo nuevo:** `core/ml_orchestrator.py`

```python
class PDFCharacterizer:
    """Analiza PDF → features → score de complejidad"""
    - Detecta: % texto nativo vs scaneado
    - Detecta: complejidad de layout
    - Detecta: presencia de tablas
    - Detecta: lenguaje(s)
    - Detecta: calidad de escaneo
    → Score de "complejidad" (0-100)

class ModelSelector:
    """Dado score de complejidad → elige modelo óptimo"""
    - score <= 20: Tesseract (rápido, suficiente)
    - 20-50: EasyOCR (balance velocidad/precisión)
    - 50-70: EasyOCR + Tesseract (ensemble)
    - > 70: Docling (necesario para layout)
```

### Fase 2: Quality Scoring + Adaptive Preprocessing

**Archivo nuevo:** `features/_quality_scorer.py`

```python
class ImageQualityScorer:
    """Mide calidad ANTES y DESPUÉS de prep"""
    metrics = {
        "contrast_ratio": Weber_contrast,
        "edge_definition": Laplacian_variance,
        "noise_level": Entropy,
        "skew_angle": Hough_transform,
        "sharpness": Tenengrad_metric,
        "brightness": Histograma_analysis
    }
    
    → quality_score (0-100)
    → recommended_preprocessing (bool)
    → preprocessing_method ("none" | "pil" | "opencv" | "unpaper")

def adaptive_preprocessing(img, auto=True):
    """Decide si preprocess basado en quality"""
    quality = ImageQualityScorer.score(img)
    if quality > 85:
        return img  # ✓ No necesita
    if quality < 30:
        return heavy_preprocessing(img)  # ⚠️ Muy mala
    return light_preprocessing(img)  # Balanceado
```

### Fase 3: Ensemble + Voting

**Archivo nuevo:** `core/ensemble_ocr.py`

```python
class EnsembleOCR:
    """Ejecuta N modelos en paralelo, vota resultado"""
    
    def extract(pdf_path, models=["tesseract", "easyocr", "docling"]):
        # Parallelización asíncrona
        results = await asyncio.gather(
            tesseract.extract_async(pdf_path),
            easyocr.extract_async(pdf_path),
            docling.extract_async(pdf_path),
        )
        
        # Voting por página y región
        consensus = vote_results(results)
        
        # Confidence aggregation
        for page in consensus.pages:
            page.confidence = aggregate_confidence([
                r.pages[page.num].confidence for r in results
            ])
            # Bonus si múltiples métodos coinciden
            if len(unique_results(page.text)) == 1:
                page.confidence += 0.15  # Concordancia boost
            
        return consensus  # Best consensus + confidence
```

### Fase 4: GPU Pipeline Orchestration

**Archivo nuevo:** `core/gpu_manager.py`

```python
class GPUManager:
    """Orquesta uso de GPU para múltiples modelos"""
    
    - Monitor VRAM disponible
    - Queue ejecutable asíncrona por GPU
    - Async/await para no bloquear
    - Connection pooling para modelos pesados
    
    def get_available_gpu():
        # Retorna GPU con más VRAM libre
        
    async def run_on_gpu(model, data, gpu_id=None):
        # Ejecuta en GPU, cede si hay timeout
```

### Fase 5: Caching Inteligente

**Archivo nuevo:** `core/cache_manager.py`

```python
class PDFCache:
    """Cache por contenido del PDF"""
    
    key = hash(pdf_bytes)
    cached = {
        "metadata": {...},
        "characterization": {...},
        "ocr_results": {...},
        "timestamps": {...}
    }
    
    # Strategy: mantener caché caliente en memoria o disco SSD
    # TTL configurable por tipo (metadata vs OCR results)
```

### Fase 6: Regional Confidence Maps

**Archivo nuevo:** `output/confidence_mapper.py`

```python
class ConfidenceMapper:
    """Genera mapa de confianza por región"""
    
    - Divide página en grid (32x32 o adaptativo)
    - Calcula confidence por región
    - Exporta heatmap (JSON + visual)
    
    output = {
        "regions": [
            {"bbox": [x,y,w,h], "type": "text", "confidence": 0.92},
            {"bbox": [x,y,w,h], "type": "table", "confidence": 0.88},
        ],
        "heatmap": "png_bytes",  # Visualización
        "summary": {"text": 0.92, "tables": 0.88, "overall": 0.90}
    }
```

### Fase 7: Telemetría + Monitoring

**Archivo nuevo:** `core/telemetry.py`

```python
class OCRTelemetry:
    """Recolecta metrics automáticamente"""
    
    metrics = {
        "latency_by_model": {},          # tiempo/modelo
        "confidence_by_model": {},       # precisión/modelo
        "memory_usage": {},              # RAM/GPU/modelo
        "throughput": {},                # PDFs/segundo
        "cache_hit_rate": {},            # % cache hits
        "error_rate_by_model": {},       # % failures
    }
    
    # Persistencia en InfluxDB, Prometheus, etc.
    # Dashboard Grafana opcionales
```

### Fase 8: Docker Orchestration

**Nuevos archivos:**

```
docker/
  ├── Dockerfile.ocr-tesseract      # Tesseract + base
  ├── Dockerfile.ocr-easyocr        # EasyOCR + GPU
  ├── Dockerfile.ocr-docling        # IBM Docling
  ├── Dockerfile.ocr-api            # FastAPI wrapper
  └── docker-compose.yml             # Orquestación local
  
kubernetes/
  ├── ocr-tesseract-deployment.yaml
  ├── ocr-easyocr-deployment.yaml
  ├── ocr-docling-deployment.yaml
  ├── ocr-api-service.yaml
  └── hpa.yaml                       # Auto-scaling
```

**docker-compose.yml:**
```yaml
version: '3.9'
services:
  ocr-api:
    image: ocr-api:latest
    ports: [8000:8000]
    depends_on: [tesseract-svc, easyocr-svc, docling-svc]
    environment:
      - TESSERACT_URL=http://tesseract-svc:9000
      - EASYOCR_URL=http://easyocr-svc:9001
      - DOCLING_URL=http://docling-svc:9002
  
  tesseract-svc:
    image: ocr-tesseract:latest
    ports: [9000:9000]
    cpus: 2
  
  easyocr-svc:
    image: ocr-easyocr:latest
    ports: [9001:9001]
    gpus: [0]  # GPU 0
  
  docling-svc:
    image: ocr-docling:latest
    ports: [9002:9002]
    gpus: [1]  # GPU 1
```

---

## 📋 Plan de Implementación

### Semana 1: Intelligence Layer (Fase 1-2)
- [ ] `core/ml_orchestrator.py` — PDF characterizer + model selector
- [ ] `features/_quality_scorer.py` — Quality metrics
- [ ] Tests de caracterización

### Semana 2: Ensemble (Fase 3-4)
- [ ] `core/ensemble_ocr.py` — Parallel execution + voting
- [ ] `core/gpu_manager.py` — GPU orchestration
- [ ] Async/await refactor

### Semana 3: Caching + Monitoreo (Fase 5-7)
- [ ] `core/cache_manager.py` — Smart caching
- [ ] `output/confidence_mapper.py` — Region-based confidence
- [ ] `core/telemetry.py` — Metrics collection

### Semana 4: Docker + Testing (Fase 8)
- [ ] Docker images para cada servicio
- [ ] docker-compose.yml para orquestación
- [ ] K8s manifests (opcional, road map)
- [ ] Integration tests

---

## 🎯 Impacto Esperado

### Antes (Hoy)
```
PDF → Tesseract → ¿Falla? → EasyOCR → ¿Falla? → Docling
Tiempo: 30s (Tess) + 120s (Easy) = 150s worst-case
GPU: Ociosa durante Tesseract
Confianza: Punto ciego (no sé qué es confiable)
```

### Después (Con mejoras)
```
PDF → Characterize (0.5s) → Select modelo óptimo
       → [Tesseract (15s) + EasyOCR (30s) en paralelo]
       → Ensemble voting + confidence map
Tiempo: 0.5 + 30s (paralelo) + 5s (voting) = 35.5s (-76% latencia)
GPU: Utilizada eficientemente, pipeline async
Confianza: Mapa por región + agreement bonus
Cache: 2do+ PDF idéntico = 0.5s (characterize only)
```

### Métricas de Éxito
- ✓ **Latencia:** -70% vs baseline
- ✓ **Precisión:** +5-10% (via ensemble)
- ✓ **GPU utilization:** >80%
- ✓ **Confiabilidad:** Cero "crashes" por network
- ✓ **Escalabilidad:** Desde 1 PDF/s → N PDFs/s (paralelo)

---

## 🔧 Decisiones Arquitectónicas

### 1. **Async/Await vs Threading**
**Decisión:** Async (asyncio + aiofiles)
- Mejor para I/O (lectura PDF, red)
- Menor overhead vs threads
- Compatible con event loops HTTP

### 2. **Ensemble Voting Strategy**
**Decisión:** Weighted voting + region-aware
- Tesseract: weight=0.3 (rápido, baseline)
- EasyOCR: weight=0.4 (preciso, multi-lang)
- Docling: weight=0.3 (layout, pero lento)
- Bonus: +0.15 si 2+ métodos coinciden

### 3. **Cache Backend**
**Decisión:** SQLite local + optional Redis
- SQLite: zero-config, portable
- Redis: opcional para deployments distribuidos
- TTL: 24h metadata, 7d OCR results

### 4. **GPU Management**
**Decisión:** Manual device placement + fallback to CPU
- No CUDA stream multiplexing (complejo)
- Fallback graceful si GPU falla
- Monitoring vía nvidia-smi periodicamente

### 5. **Confidence Scoring**
**Decisión:** Modelo-agnostic aggregation
- Normalize [0,1] todas las confidencias
- Agreement bonus si coinciden modelos
- Per-region scoring (texto vs tabla)

---

## 💡 Ideas Futuro (Road Map)

1. **Fine-tuning para documentos españoles**
   - Dataset TecNM de 80 PDFs
   - Fine-tune CRAFT (text detection) + CRNN (recognition)
   - +5-10% precisión localizada

2. **Detección de contexto (entity recognition)**
   - NER para: Números de documento, fechas, montos
   - Validación post-OCR (e.g., RFC format)

3. **Layout understanding (Pix2Struct, LayOut LM)**
   - Entender estructura de documento (secciones, jeraquías)
   - Exportar JSON + HTML semántico

4. **Real-time streaming OCR**
   - WebSocket API para OCR en vivo
   - Procesar página-por-página conforme se carga

5. **Mobile OCR (TFLite, ONNX quantized)**
   - Modelos ligeros para mobile
   - <100MB descarga

---

## 📊 Estimación de Esfuerzo

| Componente | Complejidad | Horas | Dependencias |
|------------|-------------|-------|--------------|
| ML Orchestrator | Media | 16 | ninguna |
| Quality Scorer | Media | 12 | PIL, OpenCV |
| Ensemble OCR | Alta | 20 | async/await |
| GPU Manager | Alta | 16 | pytorch/tf |
| Cache Manager | Baja | 8 | sqlite |
| Confidence Mapper | Baja | 8 | numpy |
| Telemetry | Media | 12 | logging |
| Docker | Baja | 12 | Docker |
| **Total** | | **104 horas** | |

---

## 🚀 Priorización (MVP)

**Must-have (Semana 1-2):**
1. PDF characterizer + model selector
2. Ensemble OCR (paralelo)
3. Quality scoring básico

**Nice-to-have (Semana 3-4):**
4. Caching
5. Docker
6. Telemetría básica

**Future:**
7. Fine-tuning
8. K8s
9. Mobile

---

## 📌 Notas Importantes

- **Backward compatible:** Todas las mejoras son aditivas
- **Graceful degradation:** Si ensemble falla, fallback a mejor modelo individual
- **Zero-trust en redes:** Retry logic + caching cubren fallos
- **Documentación:** Cada componente con docstrings + ejemplos
- **Testing:** Unit + integration tests obligatorio

---

**Conclusión:** Tu proyecto OCR tiene los *bloques básicos* (métodos individuales robusto). Falta la *orquestación inteligente* (characterization + ensemble + GPU parallelization). Eso es donde el 70% del valor adicional está.

**Próximo paso:** ¿Aprobás empezar con Fase 1 (characterizer + selector)?

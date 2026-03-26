---
name: Dependency Mapping
description: Bağımlılık haritası çıkarma ve analiz skill'i
---

# 🗺️ Dependency Mapping Skill

Proje modülleri arasındaki bağımlılık yapısını haritalandırır.

## Ne Zaman Kullanılır?

- "Bu modülün bağımlılıklarını göster"
- "En çok bağımlılığa sahip dosya hangisi?"
- "Modül coupling'i ne durumda?"

## Adımlar

### 1. Bağımlılık Haritası
```
get_dependency_graph(path="...", root_file="src/core/engine.py", depth=3)
```

### 2. Coupling Metrikleri
```
get_module_coupling(path="...", module="src/core/engine.py")
```

### 3. Döngüsel Bağımlılık Kontrolü
```
find_circular_dependencies(path="...")
```

### 4. Bağımlılık Matrisi
```
generate_dependency_matrix(path="...")
```

## Coupling Yorumlama

| Ca (Afferent) | Ce (Efferent) | Yorum |
|:---:|:---:|--------|
| Yüksek | Düşük | Kararlı, çekirdek modül |
| Düşük | Yüksek | Değişken, çok bağımlı |
| Yüksek | Yüksek | Riskli — refactor gerekli |
| Düşük | Düşük | İzole modül |

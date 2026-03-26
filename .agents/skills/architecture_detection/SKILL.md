---
name: Architecture Detection
description: Mimari pattern tespiti ve katman analizi skill'i
---

# 🏛️ Architecture Detection Skill

Projenin mimari yapısını otomatik tespit eder ve görselleştirir.

## Ne Zaman Kullanılır?

- "Bu projenin mimarisi ne?"
- "Katman yapısını göster"
- "Modüller arası coupling ne durumda?"

## Adımlar

### 1. Mimari Tespit
```
detect_architecture(path="...")
```

### 2. Coupling Analizi
Yüksek coupling'li modüller için:
```
get_module_coupling(path="...", module="src/services/user_service.py")
```

### 3. Bağımlılık Grafı
```
get_dependency_graph(path="...", root_file="src/main.py")
```

### 4. Code Smell Taraması
```
detect_code_smells(path="...")
```

## Desteklenen Pattern'ler

| Pattern | İpuçları |
|---------|----------|
| MVC | models/, views/, controllers/ dizinleri |
| Layered | api/, services/, repositories/ |
| Clean Architecture | domain/, use_cases/, adapters/, infrastructure/ |
| Hexagonal | ports/, adapters/ |
| Microservices | docker-compose, services/ alt projeleri |
| Event-Driven | events/, handlers/, listeners/ |
| Monolith | Belirgin pattern yok (default) |

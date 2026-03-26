---
description: Tam proje analizi — tarama, graf, mimari, metrikler, rapor
---

# Full Analysis Workflow

// turbo-all

## Adımlar

1. Projeyi tara:
```
scan_project(path="<PROJECT_PATH>")
```

2. Proje özetini al:
```
get_project_summary(path="<PROJECT_PATH>")
```

3. Mimari tespit:
```
detect_architecture(path="<PROJECT_PATH>")
```

4. Döngüsel bağımlılık kontrolü:
```
find_circular_dependencies(path="<PROJECT_PATH>")
```

5. Code smell taraması:
```
detect_code_smells(path="<PROJECT_PATH>")
```

6. Dead code tespiti:
```
find_dead_code(path="<PROJECT_PATH>")
```

7. Hotspot haritası:
```
generate_hotspot_map(path="<PROJECT_PATH>")
```

8. Sonuçları birleştirip kullanıcıya kapsamlı bir rapor sun.

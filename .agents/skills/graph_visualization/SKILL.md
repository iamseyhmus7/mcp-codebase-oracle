---
name: Graph Visualization
description: Bağımlılık ve çağrı grafı görselleştirme skill'i
---

# 🕸️ Graph Visualization Skill

Kod ilişkilerini Mermaid diyagramları ile görselleştirir.

## Ne Zaman Kullanılır?

- "Bağımlılık grafını göster"
- "Bu fonksiyonu kim çağırıyor?"
- "Sınıf hiyerarşisini göster"
- "Döngüsel bağımlılık var mı?"

## Araçlar

### Bağımlılık Grafı
```
get_dependency_graph(path="...", root_file="src/main.py")
```

### Çağrı Grafı
```
get_call_graph(path="...", function_name="process_data", direction="both")
```

### Sınıf Hiyerarşisi
```
get_class_hierarchy(path="...", class_name="BaseParser")
```

### Döngüsel Bağımlılık
```
find_circular_dependencies(path="...")
```

### Mimari Diyagram
```
generate_architecture_diagram(path="...")
```

### Bağımlılık Matrisi
```
generate_dependency_matrix(path="...")
```

## Mermaid Çıktı Tipleri

Tüm diyagramlar `mermaid` code block içinde sunulur:
- **flowchart**: Bağımlılık ve çağrı grafları
- **classDiagram**: Sınıf hiyerarşisi
- **graph**: Genel ilişki grafları

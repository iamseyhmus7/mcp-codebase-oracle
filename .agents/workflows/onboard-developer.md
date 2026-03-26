---
description: Yeni geliştirici onboarding rehberi üretimi
---

# Onboard Developer Workflow

// turbo-all

## Adımlar

1. Projeyi tara:
```
scan_project(path="<PROJECT_PATH>")
```

2. Onboarding rehberi üret:
```
generate_onboarding_guide(path="<PROJECT_PATH>")
```

3. En kritik dosyayı açıkla (en çok bağımlılığa sahip):
```
explain_file(path="<PROJECT_PATH>", file="<CRITICAL_FILE>")
```

4. Mimari diyagram üret:
```
generate_architecture_diagram(path="<PROJECT_PATH>")
```

5. Bağımlılık matrisini göster:
```
generate_dependency_matrix(path="<PROJECT_PATH>")
```

6. Sonuçları kapsamlı bir onboarding guide olarak sun.

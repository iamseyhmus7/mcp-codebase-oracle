---
description: Tek dosya/fonksiyon değişiklik etki analizi
---

# Impact Check Workflow

// turbo-all

## Adımlar

1. Projenin tarandığından emin ol. Taranmadıysa:
```
scan_project(path="<PROJECT_PATH>")
```

2. Etki analizi yap:
```
analyze_impact(path="<PROJECT_PATH>", file="<FILE_PATH>", symbol="<SYMBOL_NAME>", change_type="modify")
```

3. Risk seviyesine göre ek analiz:
   - 🟢 Low: Raporu sun, geç
   - 🟡 Medium: Coupling bilgisi ekle
   - 🟠 High/🔴 Critical: what_if_delete veya what_if_rename çalıştır

4. Etkilenen testleri listele ve koşulması gereken test komutlarını öner.

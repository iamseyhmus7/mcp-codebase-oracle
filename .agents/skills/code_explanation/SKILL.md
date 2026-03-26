---
name: Code Explanation
description: Dosya ve fonksiyon bazlı kod açıklama skill'i
---

# 📖 Code Explanation Skill

Legacy veya unfamiliar kodu insan tarafından anlaşılır şekilde açıklar.

## Ne Zaman Kullanılır?

- "Bu dosya ne yapıyor?"
- "Bu fonksiyonu açıkla"
- "Bu sınıfın amacı ne?"

## Adımlar

### Dosya Açıklama
```
explain_file(path="...", file="src/core/engine.py")
```

### Fonksiyon Açıklama
```
explain_function(path="...", file="src/core/engine.py", function="process_data")
```

### Dosya Yapı Özeti
```
get_file_overview(path="...", file="src/core/engine.py")
```

## Açıklama Stratejisi

1. **Amaç**: Dosya/fonksiyon ne için var?
2. **Bileşenler**: İçinde hangi sınıflar/fonksiyonlar var?
3. **Bağımlılıklar**: Neye bağımlı, kim buna bağımlı?
4. **Veri Akışı**: Veri nasıl giriyor, nasıl çıkıyor?
5. **Yan Etkiler**: DB yazma, dosya I/O, network call var mı?

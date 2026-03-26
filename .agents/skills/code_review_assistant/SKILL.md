---
name: Code Review Assistant
description: PR/commit bazlı kod review ve etki değerlendirme skill'i
---

# 🔍 Code Review Assistant Skill

Kod değişikliklerini review eder, etki değerlendirmesi yapar ve code smell tarar.

## Ne Zaman Kullanılır?

- "Bu dosyadaki değişikliklerin etkisini kontrol et"
- "Code review yap"
- "Bu modülde code smell var mı?"
- "Dead code var mı?"

## Review Adımları

### 1. Etki Analizi
```
analyze_impact(path="...", file="src/changed_file.py", change_type="modify")
```

### 2. Code Smell Kontrolü
```
detect_code_smells(path="...", file="src/changed_file.py")
```

### 3. Dead Code Tespiti
```
find_dead_code(path="...", file="src/changed_file.py")
```

### 4. Coupling Kontrolü
```
get_module_coupling(path="...", module="src/changed_file.py")
```

## Review Çıktı Şablonu

```markdown
## Code Review Raporu

### ✅ Geçen Kontroller
- [ ] Etki analizi tamamlandı
- [ ] Code smell tarandı
- [ ] Dead code kontrol edildi

### ⚠️ Bulgular
- Risk seviyesi: [emoji + level]
- Etkilenen dosya sayısı: X
- Code smell: Y adet
- Dead code: Z adet

### 💡 Öneriler
- ...
```

---
name: Impact Analysis
description: Kod değişikliklerinin etkisini analiz etme skill'i
---

# 💥 Impact Analysis Skill

Bu skill, bir kod değişikliğinin projenin geri kalanını nasıl etkileyeceğini analiz eder.

## Ne Zaman Kullanılır?

- "Bu dosyayı değiştirirsem ne olur?"
- "Bu fonksiyonu silsem sorun olur mu?"
- "Bu sınıfı rename etsem nereleri değiştirmem lazım?"
- "Kullanılmayan kod var mı?"

## Adımlar

### 1. Projenin Tarandığından Emin Ol
Proje daha önce taranmadıysa:
```
scan_project(path="...")
```

### 2. Etki Analizi
```
analyze_impact(path="...", file="src/module.py", symbol="my_function", change_type="modify")
```

### 3. Risk Değerlendirmesi
Çıktıdaki risk seviyesini kontrol et:
- 🟢 **Low**: Güvenle değiştirebilirsin
- 🟡 **Medium**: Dikkatli ol, 2-5 dosya etkilenecek
- 🟠 **High**: Kapsamlı test gerekli, 6-15 dosya etkilenecek
- 🔴 **Critical**: Çok riskli, 15+ dosya etkilenecek

### 4. Silme Senaryosu (Opsiyonel)
```
what_if_delete(path="...", target="old_utils.py", target_type="file")
```

### 5. Rename Senaryosu (Opsiyonel)
```
what_if_rename(path="...", target="old_name", new_name="new_name")
```

### 6. Dead Code Tespiti (Opsiyonel)
```
find_dead_code(path="...", file="src/module.py")
```

## Çıktı Formatı

1. 💥 Risk badge'i ve açıklama
2. 🎯 Doğrudan etkilenen dosyalar listesi
3. 🔗 Dolaylı etkilenen dosyalar
4. 🧪 Çalıştırılması gereken testler
5. 📊 Mermaid etki diyagramı

## Dikkat Edilecekler

- Statik analiz bazlıdır, dinamik çağrılar (reflection, getattr) tespit edilemez
- Test dosyaları ayrıca listelenir
- Mermaid diyagramında kırmızı = doğrudan, sarı = dolaylı etki

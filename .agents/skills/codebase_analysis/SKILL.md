---
name: Codebase Analysis
description: Proje tarama, indeksleme ve genel analiz skill'i
---

# 🔍 Codebase Analysis Skill

Bu skill, herhangi bir projeyi tarayıp analiz etmek için kullanılır.

## Ne Zaman Kullanılır?

- Kullanıcı bir projeyi ilk kez analiz etmek istediğinde
- "Bu projeyi tara", "projeyi analiz et", "proje yapısını göster" gibi isteklerde

## Adımlar

### 1. Proje Taraması
```
scan_project(path="/absolute/path/to/project")
```
Bu tool projeyi tarar, tüm dosyaları parse eder ve indeksler. **Her zaman ilk adım budur.**

### 2. Proje Özeti
```
get_project_summary(path="/absolute/path/to/project")
```
Taranan projenin genel özetini al: dil dağılımı, dosya sayısı, framework tespiti.

### 3. Mimari Tespit
```
detect_architecture(path="/absolute/path/to/project")
```
Projenin mimari pattern'ini tespit et (MVC, Layered, Clean Architecture vb.)

### 4. Kritik Dosyaları Bul
```
find_symbol(path="...", name="main", kind="function")
```
Giriş noktalarını ve kritik sembolleri bul.

## Çıktı Formatı

Sonuçları şu sırada sun:
1. 📊 Genel özet tablosu
2. 🏛️ Mimari pattern ve Mermaid diyagramı
3. 📁 Dosya ağacı (önemli dizinler)
4. 💡 Öneriler

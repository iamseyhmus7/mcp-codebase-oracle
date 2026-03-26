# 🔮 MCP Codebase Oracle — AGENTS.md

> **"Bu kodu kim yazdı, ne yapıyor anlamıyorum" sorusunu tarihe gömüyoruz.**

## 📌 Proje Vizyonu

**MCP Codebase Oracle**, herhangi bir yazılım projesini analiz ederek:
- Tüm **mimari yapıyı** otomatik olarak çıkarır
- **Fonksiyon ilişkilerini** (call graph, dependency graph) görselleştirir
- **"Bu kodu değiştirirsem nereleri etkiler?"** sorusuna kesin cevap verir
- Legacy code'u anlaşılır ve yönetilebilir hale getirir

Bu, bir **MCP (Model Context Protocol) sunucusu** olarak çalışır. AI istemcileri (Claude Desktop, Gemini, VS Code Copilot, vb.) bu sunucuya bağlanarak herhangi bir codebase hakkında derinlemesine soru sorabilir.

---

## 🏗️ Proje Mimarisi

```
mcp-codebase-oracle/
├── AGENTS.md                          # Bu dosya — proje rehberi
├── README.md                          # Proje açıklaması ve kullanım kılavuzu
├── pyproject.toml                     # Python paket yapılandırması (uv/pip)
├── Dockerfile                         # Container desteği
├── .env.example                       # Ortam değişkenleri şablonu
│
├── src/
│   └── mcp_codebase_oracle/
│       ├── __init__.py
│       ├── __main__.py                # Entry point (python -m mcp_codebase_oracle)
│       ├── server.py                  # MCP Server ana modülü (FastMCP)
│       ├── config.py                  # Konfigürasyon yönetimi
│       │
│       ├── core/                      # 🧠 Çekirdek Analiz Motorları
│       │   ├── __init__.py
│       │   ├── parser.py              # AST tabanlı multi-language parser
│       │   ├── indexer.py             # Codebase indeksleme ve cache
│       │   ├── graph_builder.py       # Dependency & call graph oluşturucu
│       │   ├── impact_analyzer.py     # Değişiklik etki analizi motoru
│       │   ├── architecture_detector.py  # Mimari pattern tespiti (MVC, Hexagonal, vb.)
│       │   └── complexity_analyzer.py # Karmaşıklık metrikleri (cyclomatic, cognitive)
│       │
│       ├── parsers/                   # 🔤 Dil-Spesifik Parser'lar
│       │   ├── __init__.py
│       │   ├── base_parser.py         # Abstract base parser sınıfı
│       │   ├── python_parser.py       # Python AST parser (ast modülü)
│       │   ├── typescript_parser.py   # TypeScript/JavaScript parser (tree-sitter)
│       │   ├── java_parser.py         # Java parser (tree-sitter)
│       │   ├── go_parser.py           # Go parser (tree-sitter)
│       │   ├── rust_parser.py         # Rust parser (tree-sitter)
│       │   ├── csharp_parser.py       # C# parser (tree-sitter)
│       │   └── generic_parser.py      # Fallback regex-based parser
│       │
│       ├── models/                    # 📦 Veri Modelleri
│       │   ├── __init__.py
│       │   ├── codebase.py            # Codebase, Module, Package modelleri
│       │   ├── symbols.py             # Function, Class, Variable, Import modelleri
│       │   ├── relationships.py       # Edge, Dependency, CallSite modelleri
│       │   ├── graph.py               # CodeGraph — ana graf veri yapısı
│       │   ├── metrics.py             # ComplexityMetrics, CoverageInfo modelleri
│       │   └── analysis.py            # ImpactReport, ArchitectureReport modelleri
│       │
│       ├── tools/                     # 🔧 MCP Tool Tanımları
│       │   ├── __init__.py
│       │   ├── scan_tools.py          # Proje tarama ve indeksleme tool'ları
│       │   ├── query_tools.py         # Sorgulama tool'ları (fonksiyon ara, sınıf bul)
│       │   ├── graph_tools.py         # Graf sorgulama tool'ları
│       │   ├── impact_tools.py        # Etki analizi tool'ları
│       │   ├── architecture_tools.py  # Mimari analiz tool'ları
│       │   ├── explain_tools.py       # Kod açıklama tool'ları
│       │   └── visualization_tools.py # Görselleştirme tool'ları (Mermaid, DOT)
│       │
│       ├── resources/                 # 📊 MCP Resource Tanımları
│       │   ├── __init__.py
│       │   ├── graph_resources.py     # Graf verileri resource olarak
│       │   ├── metrics_resources.py   # Metrik verileri resource olarak
│       │   └── report_resources.py    # Rapor resource'ları
│       │
│       ├── prompts/                   # 💬 MCP Prompt Tanımları
│       │   ├── __init__.py
│       │   ├── analysis_prompts.py    # Analiz prompt şablonları
│       │   ├── explain_prompts.py     # Kod açıklama prompt şablonları
│       │   └── review_prompts.py      # Kod review prompt şablonları
│       │
│       └── utils/                     # 🛠️ Yardımcı Modüller
│           ├── __init__.py
│           ├── file_utils.py          # Dosya okuma/yazma, gitignore desteği
│           ├── git_utils.py           # Git entegrasyonu (blame, log, diff)
│           ├── cache.py               # LRU & disk cache sistemi
│           ├── mermaid.py             # Mermaid diagram üretici
│           └── formatters.py          # Çıktı formatlama (Markdown, JSON)
│
├── tests/                             # 🧪 Test Dosyaları
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_parser.py
│   ├── test_graph_builder.py
│   ├── test_impact_analyzer.py
│   ├── test_architecture_detector.py
│   ├── test_tools.py
│   └── fixtures/                      # Test projeleri (mini codebase'ler)
│       ├── python_project/
│       ├── typescript_project/
│       └── mixed_project/
│
├── docs/                              # 📚 Dokümantasyon
│   ├── architecture.md
│   ├── tool-reference.md
│   ├── supported-languages.md
│   └── examples.md
│
└── .agents/                           # 🤖 Agent Konfigürasyonu
    ├── skills/
    │   ├── codebase_analysis/
    │   │   └── SKILL.md
    │   ├── impact_analysis/
    │   │   └── SKILL.md
    │   ├── architecture_detection/
    │   │   └── SKILL.md
    │   ├── code_explanation/
    │   │   └── SKILL.md
    │   ├── graph_visualization/
    │   │   └── SKILL.md
    │   ├── dependency_mapping/
    │   │   └── SKILL.md
    │   └── code_review_assistant/
    │       └── SKILL.md
    └── workflows/
        ├── full-analysis.md
        ├── quick-scan.md
        ├── impact-check.md
        └── onboard-developer.md
```

---

## ⚙️ Teknoloji Stack'i

| Katman | Teknoloji | Neden? |
|--------|-----------|--------|
| **Dil** | Python 3.11+ | MCP SDK desteği, zengin AST ekosistemi |
| **MCP Framework** | `mcp[cli]` (FastMCP) | Resmi Anthropic MCP SDK |
| **AST Parsing** | `tree-sitter` + Python `ast` | Multi-language desteği, hızlı parsing |
| **Graf Yapısı** | `networkx` | Güçlü graf algoritmaları, traversal |
| **Görselleştirme** | Mermaid.js diyagramları | AI istemcilerinde render edilebilir |
| **Cache** | `diskcache` + `functools.lru_cache` | Büyük projelerde performans |
| **Git Entegrasyonu** | `gitpython` | Blame, diff, commit history |
| **Paketleme** | `uv` / `pip` | Modern Python paket yönetimi |
| **Test** | `pytest` + `pytest-asyncio` | Async test desteği |
| **Linting** | `ruff` | Hız + kapsamlı kurallar |
| **Tip Kontrolü** | `mypy` | Statik tip güvenliği |

---

## 🔧 MCP Tool Tanımları (Detaylı)

### 1. 📂 Tarama & İndeksleme Tool'ları (`scan_tools.py`)

#### `scan_project`
```
Bir projeyi tarar ve indeksler.
- Input: { "path": string, "exclude_patterns": string[], "max_depth": int }
- Output: { "summary": ProjectSummary, "file_count": int, "language_breakdown": dict }
- Davranış: .gitignore'u otomatik okur, binary dosyaları atlar, sembolik linkleri takip eder
```

#### `rescan_project`
```
Daha önce taranan projeyi günceller (incremental).
- Input: { "path": string }
- Output: { "changes_detected": int, "new_files": string[], "modified_files": string[], "deleted_files": string[] }
```

#### `get_project_summary`
```
Taranan projenin genel özetini döndürür.
- Input: { "path": string }
- Output: { "name": string, "languages": dict, "total_files": int, "total_lines": int, 
            "frameworks_detected": string[], "architecture_pattern": string }
```

### 2. 🔍 Sorgulama Tool'ları (`query_tools.py`)

#### `find_symbol`
```
Fonksiyon, sınıf veya değişken arar.
- Input: { "name": string, "kind": "function"|"class"|"variable"|"all", "path": string? }
- Output: { "matches": Symbol[], "total": int }
```

#### `get_symbol_detail`
```
Bir sembolün detaylı bilgisini döndürür.
- Input: { "file": string, "name": string, "line": int? }
- Output: { "symbol": Symbol, "docstring": string?, "signature": string, 
            "complexity": int, "callers": string[], "callees": string[] }
```

#### `search_code`
```
Kod içinde regex veya semantic arama yapar.
- Input: { "query": string, "is_regex": bool, "file_pattern": string? }
- Output: { "matches": SearchResult[], "total": int }
```

#### `get_file_overview`
```
Bir dosyanın yapısal özetini çıkarır.
- Input: { "file": string }
- Output: { "imports": string[], "classes": ClassInfo[], "functions": FunctionInfo[], 
            "exports": string[], "dependencies": string[] }
```

### 3. 🕸️ Graf Sorgulama Tool'ları (`graph_tools.py`)

#### `get_dependency_graph`
```
Modüller/paketler arası bağımlılık grafını döndürür.
- Input: { "scope": "module"|"package"|"file", "root": string?, "depth": int? }
- Output: { "nodes": Node[], "edges": Edge[], "mermaid": string }
```

#### `get_call_graph`
```
Fonksiyon çağrı grafını döndürür.
- Input: { "function": string, "direction": "callers"|"callees"|"both", "depth": int? }  
- Output: { "nodes": Node[], "edges": Edge[], "mermaid": string }
```

#### `get_class_hierarchy`
```
Sınıf kalıtım hiyerarşisini döndürür.
- Input: { "class_name": string?, "direction": "parents"|"children"|"both" }
- Output: { "hierarchy": TreeNode, "mermaid": string }
```

#### `find_circular_dependencies`
```
Döngüsel bağımlılıkları tespit eder.
- Input: { "scope": "module"|"package" }
- Output: { "cycles": Cycle[], "severity": "low"|"medium"|"high", "suggestions": string[] }
```

### 4. 💥 Etki Analizi Tool'ları (`impact_tools.py`)

#### `analyze_impact`
```
Bir değişikliğin etkisini analiz eder — PROJENİN KALBİ.
- Input: { "file": string, "symbol": string?, "change_type": "modify"|"delete"|"rename" }
- Output: { 
    "directly_affected": AffectedItem[], 
    "indirectly_affected": AffectedItem[],
    "test_files_to_run": string[],
    "risk_level": "low"|"medium"|"high"|"critical",
    "risk_explanation": string,
    "mermaid_diagram": string 
  }
```

#### `what_if_delete`
```
"Bu dosyayı/fonksiyonu silersem ne olur?" senaryosu.
- Input: { "target": string, "target_type": "file"|"function"|"class" }
- Output: { "broken_imports": string[], "broken_calls": string[], "orphaned_code": string[],
            "safe_to_delete": bool, "explanation": string }
```

#### `what_if_rename`
```
"Bu sembolü yeniden adlandırsam nereleri değiştirmem gerekir?"
- Input: { "target": string, "new_name": string }
- Output: { "files_to_update": FileUpdate[], "total_changes": int }
```

#### `find_dead_code`
```
Kullanılmayan (dead) kodu tespit eder.
- Input: { "scope": "file"|"project", "path": string? }
- Output: { "unused_functions": string[], "unused_classes": string[], 
            "unused_imports": string[], "unused_variables": string[] }
```

### 5. 🏛️ Mimari Analiz Tool'ları (`architecture_tools.py`)

#### `detect_architecture`
```
Projenin mimari pattern'ini tespit eder.
- Input: { "path": string }
- Output: { "pattern": string, "confidence": float, "evidence": string[],
            "layer_map": dict, "mermaid_diagram": string }
- Desteklenen pattern'ler: MVC, MVVM, Hexagonal, Clean Architecture, Microservices, 
                            Monolith, Event-Driven, Layered, Plugin-based
```

#### `get_module_coupling`
```
Modüller arası bağlılık (coupling) metriklerini hesaplar.
- Input: { "module_a": string, "module_b": string? }
- Output: { "afferent_coupling": int, "efferent_coupling": int, "instability": float,
            "coupling_matrix": dict }
```

#### `detect_code_smells`
```
Kod kokularını (code smells) tespit eder.
- Input: { "path": string?, "categories": string[]? }
- Output: { "smells": CodeSmell[], "summary": dict }
- Kategoriler: god_class, long_method, feature_envy, shotgun_surgery, 
               circular_dependency, deep_nesting, duplicate_code
```

### 6. 📖 Kod Açıklama Tool'ları (`explain_tools.py`)

#### `explain_file`
```
Bir dosyayı insan tarafından anlaşılır şekilde açıklar.
- Input: { "file": string, "detail_level": "brief"|"detailed"|"comprehensive" }
- Output: { "purpose": string, "key_components": ComponentInfo[], 
            "data_flow": string, "side_effects": string[] }
```

#### `explain_function`
```
Bir fonksiyonun ne yaptığını açıklar.
- Input: { "file": string, "function": string }
- Output: { "purpose": string, "parameters": ParamInfo[], "return_value": string,
            "side_effects": string[], "complexity": string, "example_usage": string }
```

#### `generate_onboarding_guide`
```
Yeni geliştiriciler için proje rehberi oluşturur.
- Input: { "path": string, "role": "frontend"|"backend"|"fullstack"|"devops"? }
- Output: { "overview": string, "key_directories": DirInfo[], "entry_points": string[],
            "critical_files": string[], "architecture_diagram": string,
            "getting_started_steps": string[] }
```

### 7. 📊 Görselleştirme Tool'ları (`visualization_tools.py`)

#### `generate_architecture_diagram`
```
Proje mimarisi diyagramını üretir (Mermaid formatında).
- Input: { "path": string, "style": "detailed"|"simplified"|"layers" }
- Output: { "mermaid": string, "description": string }
```

#### `generate_dependency_matrix`
```
Bağımlılık matrisini tablo olarak üretir.
- Input: { "scope": "module"|"package" }
- Output: { "matrix": dict[][], "markdown_table": string }
```

#### `generate_hotspot_map`
```
Kod değişiklik sıcaklık haritasını üretir (git blame tabanlı).
- Input: { "path": string, "time_range": string? }
- Output: { "hotspots": Hotspot[], "mermaid_treemap": string }
```

---

## 📊 MCP Resource Tanımları

Resources, AI istemcilerinin pasif olarak erişebileceği veri kaynaklarıdır:

| Resource URI | Açıklama |
|-------------|----------|
| `oracle://project/{path}/summary` | Proje özet bilgileri |
| `oracle://project/{path}/graph` | Tam bağımlılık grafı (JSON) |
| `oracle://project/{path}/metrics` | Proje metrikleri |
| `oracle://project/{path}/architecture` | Mimari rapor |
| `oracle://project/{path}/file/{filepath}` | Dosya detay bilgisi |
| `oracle://project/{path}/smells` | Code smell raporu |

---

## 💬 MCP Prompt Şablonları

Prompts, AI istemcilerinin önceden tanımlı iş akışlarını tetiklemesini sağlar:

| Prompt | Açıklama |
|--------|----------|
| `analyze-codebase` | Tam proje analizi başlatır |
| `explain-legacy-code` | Legacy kod açıklama modu  |
| `impact-review` | Değişiklik öncesi etki değerlendirmesi |
| `onboard-me` | Yeni geliştirici onboarding rehberi |
| `find-tech-debt` | Teknik borç keşfi ve raporlama |
| `review-architecture` | Mimari review ve öneriler |

---

## 🧠 Agent Davranış Kuralları

### Temel Prensipler

1. **Doğruluk Öncelikli**: Tahmin etme, analiz et. AST parsing sonuçlarını kullan.
2. **Kademeli Derinlik**: Önce genel özet, sonra detay. Kullanıcıyı bilgiyle boğma.
3. **Bağlam Farkındalığı**: Önceki tarama sonuçlarını cache'le ve tekrar kullan.
4. **Dil Agnostik**: Desteklenen tüm dillerde tutarlı davran.
5. **Güvenli Öneriler**: Etki analizi yaparken "en kötü durum" senaryosunu da belirt.

### Cevap Formatı Kuralları

- **Mermaid diyagramları** kullan — AI istemcileri bunları render edebilir
- **Markdown tabloları** ile metrik karşılaştırmaları göster
- **Dosya referansları** tam path ile ver
- **Risk seviyeleri** her zaman renk kodu ile belirt:
  - 🟢 Low: Güvenli değişiklik
  - 🟡 Medium: Dikkatli ilerle
  - 🟠 High: Kapsamlı test gerekli
  - 🔴 Critical: Çok sayıda bağımlılık etkilenecek

### Hata Yönetimi

- Parse edilemeyen dosyaları atla ama logla
- Desteklenmeyen diller için `generic_parser` kullan
- Büyük projeler (>10K dosya) için otomatik sampling yap
- Timeout'ları graceful handle et

---

## 🔒 Güvenlik Kuralları

1. **Sadece okuma**: Hiçbir tool kaynak kodu değiştirmez
2. **Path traversal koruması**: `..` ile üst dizin erişimi engellenir
3. **Dosya boyutu limiti**: Tek dosya max 5MB
4. **Proje boyutu limiti**: Max 100K dosya (konfigüre edilebilir)
5. **Sensitive data**: `.env`, credentials gibi dosyaları içerik olarak gösterme
6. **Sandbox**: Docker container içinde çalışabilir

---

## 📋 Geliştirme Rehberi

### Yeni Dil Parser'ı Ekleme

1. `parsers/base_parser.py` → `BaseParser` abstract sınıfını extend et
2. Şu metodları implement et:
   - `parse_file(path) -> FileAST`
   - `extract_symbols(ast) -> List[Symbol]`
   - `extract_relationships(ast) -> List[Relationship]`
   - `get_supported_extensions() -> List[str]`
3. `parsers/__init__.py` → Registry'ye kaydet
4. `tests/fixtures/` → Test projesi ekle
5. `tests/test_parser.py` → Test case'leri ekle

### Yeni MCP Tool Ekleme

1. İlgili `tools/*.py` dosyasına fonksiyon ekle
2. `@mcp.tool()` decorator'ı ile MCP'ye kaydet
3. Tip annotasyonları ve docstring'ler zorunlu
4. `tools/__init__.py` → Export et
5. Test ekle

### Commit Mesajı Formatı

```
<type>(<scope>): <description>

feat(parser): add Rust language parser
fix(impact): correct transitive dependency calculation
docs(tools): update tool reference documentation
test(graph): add circular dependency detection tests
refactor(core): extract common graph traversal logic
```

### Branch Stratejisi

- `main`: Kararlı sürüm
- `develop`: Geliştirme
- `feature/*`: Yeni özellikler
- `fix/*`: Bug düzeltmeleri
- `docs/*`: Dokümantasyon

---

## 🚀 Çalıştırma

### Development
```bash
# Bağımlılıkları kur
uv sync

# Development modunda çalıştır
uv run mcp dev src/mcp_codebase_oracle/server.py

# Test
uv run pytest

# Lint
uv run ruff check .
```

### Production
```bash
# MCP Inspector ile test
uv run mcp dev src/mcp_codebase_oracle/server.py

# Claude Desktop'a ekle
uv run mcp install src/mcp_codebase_oracle/server.py --name "Codebase Oracle"

# Docker
docker build -t mcp-codebase-oracle .
docker run -v /project:/project:ro mcp-codebase-oracle
```

---

## 🎯 Başarı Kriterleri

1. ✅ Herhangi bir Python/TS/JS projesini < 30 saniyede tarayabilmeli
2. ✅ Dependency graph'ı doğru oluşturabilmeli (>95% accuracy)
3. ✅ Impact analysis sonuçları gerçek etkileri yansıtmalı
4. ✅ Mimari pattern tespiti doğru olmalı
5. ✅ 10K+ dosyalık projelerde performanslı çalışmalı
6. ✅ MCP standardına tam uyumlu olmalı
7. ✅ PyPI'da paket olarak yayınlanabilmeli

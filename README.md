# 🔮 MCP Codebase Oracle

> **"Bu kodu kim yazdı, ne yapıyor anlamıyorum" sorusunu tarihe gömüyoruz.**

MCP Codebase Oracle, herhangi bir yazılım projesini analiz eden, mimari yapıyı çıkaran ve kod değişikliklerinin etkisini önceden gösteren bir **Model Context Protocol (MCP)** sunucusudur.

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🏗️ **Mimari Tespit** | MVC, Layered, Hexagonal, Clean Architecture ve diğer pattern'leri otomatik tespit |
| 🕸️ **Bağımlılık Grafı** | Modüller, sınıflar ve fonksiyonlar arası ilişki haritası |
| 💥 **Etki Analizi** | "Bu kodu değiştirirsem ne bozulur?" sorusuna kesin cevap |
| 📊 **Karmaşıklık Metrikleri** | Cyclomatic, cognitive complexity ve maintainability index |
| 🔍 **Sembol Arama** | Fonksiyon, sınıf, değişken arama ve detay görüntüleme |
| 📖 **Kod Açıklama** | Dosya ve fonksiyon bazlı insan tarafından anlaşılır açıklamalar |
| 🎯 **Dead Code Tespiti** | Kullanılmayan kod parçalarını bulma |
| 🌊 **Görselleştirme** | Mermaid diyagramları ile grafik çıktılar |

## 🚀 Kurulum

### uv ile (önerilen)

```bash
# Projeyi klonla
git clone https://github.com/iamseyhmus7/mcp-codebase-oracle.git
cd mcp-codebase-oracle

# Bağımlılıkları kur
uv sync

# Çalıştır
uv run mcp-codebase-oracle
```

### pip ile

```bash
pip install mcp-codebase-oracle
```

### Docker ile

```bash
docker build -t mcp-codebase-oracle .
docker run -v /path/to/project:/project:ro mcp-codebase-oracle
```

## ⚡ MCP İstemci Konfigürasyonu

### Claude Desktop

`claude_desktop_config.json` dosyasına ekle:

```json
{
  "mcpServers": {
    "codebase-oracle": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/mcp-codebase-oracle",
        "run", "mcp-codebase-oracle"
      ]
    }
  }
}
```

### VS Code (Copilot / Continue)

```json
{
  "mcp.servers": {
    "codebase-oracle": {
      "command": "mcp-codebase-oracle",
      "args": []
    }
  }
}
```

## 🔧 Kullanılabilir Tool'lar

### Tarama & İndeksleme
- `scan_project` — Proje tarama ve indeksleme
- `rescan_project` — Incremental güncelleme
- `get_project_summary` — Proje özeti

### Sorgulama
- `find_symbol` — Fonksiyon/sınıf/değişken arama
- `get_symbol_detail` — Sembol detayları
- `search_code` — Kod içi arama
- `get_file_overview` — Dosya yapı özeti

### Graf Analizi
- `get_dependency_graph` — Bağımlılık grafı
- `get_call_graph` — Fonksiyon çağrı grafı
- `get_class_hierarchy` — Sınıf hiyerarşisi
- `find_circular_dependencies` — Döngüsel bağımlılık tespiti

### Etki Analizi
- `analyze_impact` — Değişiklik etki analizi
- `what_if_delete` — Silme senaryosu
- `what_if_rename` — Yeniden adlandırma senaryosu
- `find_dead_code` — Kullanılmayan kod tespiti

### Mimari
- `detect_architecture` — Mimari pattern tespiti
- `get_module_coupling` — Modül bağlılık metrikleri
- `detect_code_smells` — Kod kokusu tespiti

### Açıklama & Görselleştirme
- `explain_file` — Dosya açıklama
- `explain_function` — Fonksiyon açıklama
- `generate_onboarding_guide` — Onboarding rehberi
- `generate_architecture_diagram` — Mimari diyagram
- `generate_dependency_matrix` — Bağımlılık matrisi
- `generate_hotspot_map` — Hotspot haritası

## 🗣️ Desteklenen Diller

| Dil | Parser | Durum |
|-----|--------|-------|
| Python | `ast` (native) | ✅ Tam destek |
| JavaScript/TypeScript | tree-sitter | 🔜 Yakında |
| Java | tree-sitter | 🔜 Yakında |
| Go | tree-sitter | 🔜 Yakında |
| Rust | tree-sitter | 🔜 Yakında |
| C# | tree-sitter | 🔜 Yakında |
| Diğerleri | regex (generic) | ⚡ Temel destek |

## 🛠️ Geliştirme

```bash
# Dev bağımlılıklarını kur
uv sync --extra dev

# Testleri çalıştır
uv run pytest -v

# Linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# MCP Inspector ile test
uv run mcp dev src/mcp_codebase_oracle/server.py
```

## 📄 Lisans

MIT License — Detaylar için [LICENSE](LICENSE) dosyasına bakın.

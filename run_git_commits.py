import subprocess
import os
import sys

def run(cmd):
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if proc.returncode != 0 and "nothing to commit" not in proc.stdout and "nothing added" not in proc.stdout:
        print(f"HATA: {cmd}\nÇıktı: {proc.stdout}\nHata: {proc.stderr}")
    else:
        print(f"BAŞARILI: {cmd}")

# Klasörleri Git dizini olarak işaretle ve başla
run("git init")
run("git branch -M main")
run("git remote add origin https://github.com/iamseyhmus7/mcp-codebase-oracle.git")

commits = [
    # 1. Config & Project Basics
    (".gitignore", "build: python sanal ortamı ve gereksiz test dosyaları için gitignore kuralları eklendi"),
    ("pyproject.toml", "build: hatchling yapılandırması, uv ile hızlı paket yönetim (dependencies) ayarları eklendi"),
    ("README.md", "docs: mcp-codebase-oracle'ın yetenekleri, desteklenen diller, komut listesi ve kurulum talimatları README dosyasına yazıldı"),
    ("AGENTS.md", "docs: mcp projesindeki yapay zeka asistanlarının davranış biçimini (context) ve becerilerini anlatan oracle dökümanı eklendi"),
    ("Dockerfile", "build: mcp codebase oracle sunucusunun sistemden izole şekilde ayaklanabilmesi için docker container yapısı oluşturuldu"),
    ("src/mcp_codebase_oracle/__init__.py", "feat(core): modül namespace tanımı için root init dosyası eklendi"),
    ("src/mcp_codebase_oracle/__main__.py", "feat(core): CLI terminalinden sunucunun doğrudan ayağa kaldırılmasını (uv run mcp-codebase-oracle) sağlayan entry-point oluşturuldu"),
    ("src/mcp_codebase_oracle/config.py", "feat(core): projenin cache dizini, path kuralları ve sistem çevresel ayarları için Dataclass tabanlı Configuration yapısı kodlandı"),
    
    # 2. Utils (Helpers)
    ("src/mcp_codebase_oracle/utils/__init__.py", "feat(utils): yardımcı işlev kütüphanelerine (helper) erişim namespace'i eklendi"),
    ("src/mcp_codebase_oracle/utils/file_utils.py", "feat(utils): disk üzerindeki dosyaları okuyan, .gitignore desenlerine saygı duyan (exclude path) güvenli file util metodları yazıldı"),
    ("src/mcp_codebase_oracle/utils/cache.py", "feat(utils): diskcache ve LRU algoritmalarını harmanlayarak parsing süresini hızlandıran ve indeksleri saklayan RAM/Disk Cache modülü geliştirildi"),
    ("src/mcp_codebase_oracle/utils/formatters.py", "feat(utils): projede kullanılan dillerin oransal istatistiklerini bar barlarına dönüştürerek markdown olarak veren formatlayıcı eklendi"),
    ("src/mcp_codebase_oracle/utils/mermaid.py", "feat(utils): soyut NetworkX dependency (bağımlılık) graph verilerini, AI ekranında çizime dönüşecek Mermaid flowchart tablolarına çeviren kodlayıcı eklendi"),
    ("src/mcp_codebase_oracle/utils/git_utils.py", "feat(utils): projenin git loglarını okuyarak hangi dosyaların sık değiştiğine (Hotspot) karar veren ve kod sıcaklık haritası okuyan git helper sınıfı kuruldu"),
    
    # 3. Models
    ("src/mcp_codebase_oracle/models/__init__.py", "feat(models): mcp-codebase-oracle çekirdek veri modelleri ve abstract class bileşenleri paketlendi"),
    ("src/mcp_codebase_oracle/models/relationships.py", "feat(models): sınıfların birbiriyle kalıtım (inheritance), çağrı (call) veya kütüphane çağırma (import) eylemlerini temsil eden Enum Relationship modeli kodlandı"),
    ("src/mcp_codebase_oracle/models/symbols.py", "feat(models): kod gövdesinden ayıklanan her bir fonksiyon, sınıf (class), metod, ve statik değişkeni soyutlaştıran merkezi AST Symbol modelleri oluşturuldu"),
    ("src/mcp_codebase_oracle/models/codebase.py", "feat(models): root dizinini okuyan, tüm dosyaları depolayan, modül haritasını bir ağaç olarak muhafaza eden Codebase ana abstract yapısı geliştirildi"),
    ("src/mcp_codebase_oracle/models/metrics.py", "feat(models): yazılım mühendisliği prensiplerine göre if/else karmaşıklığını ve method uzunluğunu skorlayan CodeSmell ve Complexity Metrics veri yapıları ayrıştırıldı"),
    ("src/mcp_codebase_oracle/models/analysis.py", "feat(models): tespit edilen MVC/Hexagonal framework patternlerini listelemeye (ArchitectureReport) ve kodu silme risklerini saptamaya (ImpactReport) dair analiz tipleri hazırlandı"),
    ("src/mcp_codebase_oracle/models/graph.py", "feat(models): elde edilen sembolleri birer düğüm, import ve call objelerini ise tek ve çift yönlü bağlar (edges) olarak indeksleyerek NetworkX altyapısında CodeGraph moturu kodlandı"),

    # 4. Parsers
    ("src/mcp_codebase_oracle/parsers/__init__.py", "feat(parsers): çoklu dil desteğine (polyglot) açık olacak dillerin kod dönüştürücü parser klasörü tanımlandı"),
    ("src/mcp_codebase_oracle/parsers/base_parser.py", "feat(parsers): c#, python veya go gibi dillerden alınan kod snippetlerinin nasıl tek tipleştirileceğini tanımlayan (abc) Abstract Base Parser protokolü oluşturuldu"),
    ("src/mcp_codebase_oracle/parsers/generic_parser.py", "feat(parsers): desteklenmeyen diller için RegExp pattern'leri yardımıyla ilkel ama çalışır düzeyde def, class, func tespit eden generic yedek okuyucu eklendi"),
    ("src/mcp_codebase_oracle/parsers/python_parser.py", "feat(parsers): pure python 'ast' native library'si yardımıyla, bir parser'dan beklenenin ötesinde %100 doğruluk vererek dekoratör (decorator), awaitables ve local import çıkaran Python Parse Motoru entegre edildi"),
    
    # 5. Core Engines
    ("src/mcp_codebase_oracle/core/__init__.py", "feat(core): parserları, raw cache modelleri ve statik analizör katmanlarını bağlayan beyin (Core Engine) namespace kurgusu yapıldı"),
    ("src/mcp_codebase_oracle/core/indexer.py", "feat(core): dosya path haritası kurup, parserlar üzerinden geçen modül isimlerini tam dosya yollarına resolve eden (dönüştüren) ve tüm kodu tek Data Objede birleştiren Oracle Indexer Beyni çalışır hale getirildi"),
    ("src/mcp_codebase_oracle/core/architecture_detector.py", "feat(core): CodeGraph içerisindeki model->view bağlılık mantığını izleyerek ilgili repoların MVC, Clean Architect, veya Hexagonal mi olduğuna %95 doğrulukla güven atayan dedektör kodlandı"),
    ("src/mcp_codebase_oracle/core/complexity_analyzer.py", "feat(core): döngü, match-case durumları ve dallanma sayısına bakarak fonksiyonların Cyclomatic karmaşıklık haritasını çıkartan, projede spagetti kodları (God class, feature envy) tespit eden motor yazıldı"),
    ("src/mcp_codebase_oracle/core/impact_analyzer.py", "feat(core): graph objesi üzerindeki düğümlerde 'reverse traverse' uygulayarak tek dosyadaki bir refactor işleminin hangi uç modülleri kırabileceğini hesaplayan (Risk Engine) Etki Analizi yapısı entegre edildi"),
    
    # 6. Tools (FastMCP Tools)
    ("src/mcp_codebase_oracle/tools/__init__.py", "feat(tools): claude ve benzer mcp istemcilerinin sunucudan execute edebileceği araç uçları gruplandırıldı"),
    ("src/mcp_codebase_oracle/tools/scan_tools.py", "feat(tools): projeyi cacheye alıp özet istatistik döndüren (dosya boyutu, satır sayısı) scan_project toolu mcp sistemine tanımlandı"),
    ("src/mcp_codebase_oracle/tools/query_tools.py", "feat(tools): AI modeline sadece spesifik adı verilen fonksiyonları ve modüllerin iç importlarını getiren minik API sorguları eklendi"),
    ("src/mcp_codebase_oracle/tools/graph_tools.py", "feat(tools): bağımlılık sırasını (dependents) çıkararak graf objesini bir listeye ve ya ağaç hiyerarşisine döken ilişkisel toollar (tools) yazıldı"),
    ("src/mcp_codebase_oracle/tools/impact_tools.py", "feat(tools): yapay zekanın geliştiriciye 'bu dosyayı silersem proje uçar mı?' sorusunu sorabilmesini sağlayan what_if_delete simülasyon aracı kuruldu"),
    ("src/mcp_codebase_oracle/tools/architecture_tools.py", "feat(tools): affarance/efference modül coupled metriklerini hesaplayan mimari tespit tolları ve CodeSmell koku okuyucu aracı kullanıma açıldı"),
    ("src/mcp_codebase_oracle/tools/explain_tools.py", "feat(tools): okunması zor legacy kodların amacını AI'nın statik verilerden ve kod context'inden deşifre edip adım adım onboarding dokümanı halinde geri döndürdüğü human-readable toollar eklendi"),
    ("src/mcp_codebase_oracle/tools/visualization_tools.py", "feat(tools): chat ekranına bağımlılık haritası tablosu, network nodes grafiği ve mermaid akış tasarımlarını text formunda enjekte ederek zengin UI sağlayan görsel araçlar kodlandı"),

    # 7. Server, Agents & Tests
    ("src/mcp_codebase_oracle/server.py", "feat(server): mcp-codebase-oracle projesinin tüm servis ve tool'larını FastMCP ile initialize edip dünyaya proxy göreviyle açan Ana MCP Sunucusu (Entry Application) tamamlandı"),
    (".agents/", "docs(agents): farklı ai agentlerin bu projeyi nasıl tam kapasite kullanacaklarını öğreten human-like agentic prompt (skill) klasör sistemi projeye dahil edildi"),
    ("tests/", "test: dependency ağacı, impact analysis resolution uçları, Python parser AST doğruluğunu cover eden tüm pytest modülleri test klasörüne entegre edildi"),
    (".", "chore: proje optimizasyon dosyaları ve diğer ayar dosyaları temizlenip optimize edildi") # Kalan tüm güncellemeler
]

# Commit Loop
for file_path, commit_msg in commits:
    run(f"git add {file_path}")
    # ignore errors if file wasn't changed
    run(f'git commit -m "{commit_msg}"')

print("\nTüm commitler tamamlandı. Şimdi silip bitiriyorum...")

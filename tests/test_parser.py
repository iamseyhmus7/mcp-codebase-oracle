"""Python parser testleri."""

from mcp_codebase_oracle.parsers.python_parser import PythonParser


class TestPythonParser:
    def setup_method(self):
        self.parser = PythonParser()

    def test_supported_extensions(self):
        exts = self.parser.get_supported_extensions()
        assert ".py" in exts
        assert ".pyi" in exts

    def test_parse_functions(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        func_names = [s.name for s in result.symbols if s.kind.value == "function"]
        assert "helper_function" in func_names
        assert "main" in func_names

    def test_parse_classes(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        class_names = [s.name for s in result.symbols if s.kind.value == "class"]
        assert "BaseProcessor" in class_names
        assert "DataProcessor" in class_names

    def test_parse_methods(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        method_names = [s.name for s in result.symbols if s.kind.value == "method"]
        assert "process" in method_names
        assert "__init__" in method_names

    def test_parse_imports(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        import_modules = [i.module for i in result.imports]
        assert "os" in import_modules
        assert "pathlib" in import_modules

    def test_parse_inheritance(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        inherits = [r for r in result.relationships if r.kind.value == "inherits"]
        assert len(inherits) >= 1
        targets = [r.target for r in inherits]
        assert "BaseProcessor" in targets

    def test_parse_docstrings(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        funcs_with_docs = [s for s in result.symbols if s.docstring]
        assert len(funcs_with_docs) > 0

    def test_parse_constants(self, sample_python_code: str):
        result = self.parser.parse_file("test.py", sample_python_code)
        constants = [s for s in result.symbols if s.kind.value == "constant"]
        assert any(c.name == "CONSTANT_VALUE" for c in constants)

    def test_syntax_error_handling(self):
        result = self.parser.parse_file("bad.py", "def foo(:\n  pass")
        assert len(result.errors) > 0

    def test_empty_file(self):
        result = self.parser.parse_file("empty.py", "")
        assert len(result.symbols) == 0
        assert len(result.errors) == 0

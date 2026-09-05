#!/usr/bin/env python3
"""
Extractor de Triplas RDF da Apostila RAG com Grafos de Conhecimento
Demonstração prática do Módulo 7: Extração de Triplas com NLP e LLMs

Autor: Claude + Thiago Gnecco
Data: 2026-09-05
Uso: python extract_knowledge_graph.py
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class Triple:
    """Representa uma tripla RDF (Sujeito, Predicado, Objeto)"""
    subject: str
    predicate: str
    obj: str
    confidence: float = 0.8
    source_module: int = 0
    line_number: int = 0

    def to_turtle(self) -> str:
        """Converte para formato Turtle RDF"""
        return f"ex:{self.subject} ex:{self.predicate} ex:{self.obj} . # confidence: {self.confidence}"

    def to_ntriples(self) -> str:
        """Converte para formato N-Triples RDF"""
        return f"<http://example.com/{self.subject}> <http://example.com/{self.predicate}> <http://example.com/{self.obj}> ."

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return asdict(self)


class KnowledgeGraphExtractor:
    """
    Extrator de triplas RDF da apostila usando pattern matching e NLP básico.
    Implementação do pipeline de Módulo 7.
    """

    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self.triples: List[Triple] = []
        self.entities: Set[str] = set()
        self.relationships: Set[str] = set()

        # Carrega dados pré-processados
        self.load_knowledge_graph_data()

    def load_knowledge_graph_data(self):
        """Carrega knowledge_graph_data.json como base"""
        json_path = self.data_dir / "knowledge_graph_data.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                self.kg_data = json.load(f)
            print(f"✅ Carregado knowledge_graph_data.json ({len(self.kg_data['modulos'])} módulos)")
        else:
            print(f"⚠️  knowledge_graph_data.json não encontrado em {self.data_dir}")
            self.kg_data = {"modulos": []}

    def extract_from_json(self) -> List[Triple]:
        """Extrai triplas do knowledge_graph_data.json estruturado"""
        print("\n📊 Extraindo triplas do JSON estruturado...")

        # 1. Triplas Módulo → Conceitos
        for mod in self.kg_data.get("modulos", []):
            mod_uri = f"modulo_{mod['id']}"
            titulo = mod['titulo'].replace(" ", "_")

            # Módulo teaches conceitos
            for keyword in mod.get("keywords", []):
                t = Triple(
                    subject=mod_uri,
                    predicate="teaches",
                    obj=keyword,
                    confidence=0.95,
                    source_module=mod['id']
                )
                self.triples.append(t)
                self.entities.add(mod_uri)
                self.entities.add(keyword)
                self.relationships.add("teaches")

            # Módulo has_topic
            for conceito in mod.get("conceitos_chave", [])[:3]:  # Top 3
                conceito_norm = conceito.split(":")[0].replace(" ", "_")
                t = Triple(
                    subject=mod_uri,
                    predicate="has_topic",
                    obj=conceito_norm,
                    confidence=0.9,
                    source_module=mod['id']
                )
                self.triples.append(t)
                self.entities.add(conceito_norm)
                self.relationships.add("has_topic")

            # Módulo requires pré-requisitos
            for prereq in mod.get("pré_requisitos", []):
                prereq_uri = f"modulo_{prereq}"
                t = Triple(
                    subject=mod_uri,
                    predicate="requires",
                    obj=prereq_uri,
                    confidence=0.95,
                    source_module=mod['id']
                )
                self.triples.append(t)
                self.relationships.add("requires")

            # Módulo references outros módulos
            for ref in mod.get("referencia_cruzada", [])[:3]:  # Top 3
                ref_uri = f"modulo_{ref}"
                t = Triple(
                    subject=mod_uri,
                    predicate="references",
                    obj=ref_uri,
                    confidence=0.85,
                    source_module=mod['id']
                )
                self.triples.append(t)
                self.relationships.add("references")

            # Módulo uses tecnologias
            for tech in mod.get("tecnologias", [])[:2]:  # Top 2
                t = Triple(
                    subject=mod_uri,
                    predicate="uses",
                    obj=tech,
                    confidence=0.9,
                    source_module=mod['id']
                )
                self.triples.append(t)
                self.entities.add(tech)
                self.relationships.add("uses")

            # Módulo is_part_of bloco
            bloco = mod.get("bloco", "").replace(" ", "_")
            t = Triple(
                subject=mod_uri,
                predicate="is_part_of",
                obj=bloco,
                confidence=0.95,
                source_module=mod['id']
            )
            self.triples.append(t)
            self.relationships.add("is_part_of")

        # 2. Triplas de Conceitos Globais
        print("  → Processando conceitos chave globais...")
        for conceito, info in self.kg_data.get("conceitos_chave_globais", {}).items():
            modulos = info.get("modulos", [])
            for mod_id in modulos:
                t = Triple(
                    subject=conceito,
                    predicate="defined_in",
                    obj=f"modulo_{mod_id}",
                    confidence=0.9,
                    source_module=mod_id
                )
                self.triples.append(t)
                self.entities.add(conceito)
                self.relationships.add("defined_in")

        # 3. Triplas de Casos de Estudo
        print("  → Processando casos de estudo...")
        for case in self.kg_data.get("casos_estudo_reais", []):
            nome = case['nome'].replace(" ", "_")
            for mod_id in case.get("modulo", []):
                t = Triple(
                    subject=nome,
                    predicate="documented_in",
                    obj=f"modulo_{mod_id}",
                    confidence=0.95,
                    source_module=mod_id
                )
                self.triples.append(t)
                self.entities.add(nome)
                self.relationships.add("documented_in")

        print(f"  ✅ Extraídas {len(self.triples)} triplas do JSON")
        return self.triples

    def extract_from_markdown(self, module_num: int) -> List[Triple]:
        """Extrai triplas de arquivo markdown usando padrões"""
        print(f"\n📄 Extraindo triplas do Módulo {module_num}...")

        md_path = self.data_dir / f"modulo_{module_num}.md"
        if not md_path.exists():
            print(f"  ⚠️  Arquivo não encontrado: {md_path}")
            return []

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        mod_uri = f"modulo_{module_num}"
        count = 0

        # Pattern 1: Conceitos com bold (**conceito**)
        bold_pattern = r'\*\*([^*]+)\*\*'
        for match in re.finditer(bold_pattern, content):
            conceito = match.group(1).replace(" ", "_")
            # Filtrar apenas conceitos relevantes (3+ palavras ou técnicos)
            if len(conceito.split("_")) >= 2 or any(x in conceito.lower() for x in ["rag", "graph", "sparql", "embedding"]):
                t = Triple(
                    subject=mod_uri,
                    predicate="mentions",
                    obj=conceito,
                    confidence=0.75,
                    source_module=module_num,
                    line_number=content[:match.start()].count('\n') + 1
                )
                if t not in self.triples:
                    self.triples.append(t)
                    count += 1

        # Pattern 2: Código Python (imports indicam uso de tecnologia)
        code_pattern = r'from\s+(\w+)\s+import|import\s+(\w+)'
        for match in re.finditer(code_pattern, content):
            lib = match.group(1) or match.group(2)
            t = Triple(
                subject=mod_uri,
                predicate="imports",
                obj=lib,
                confidence=0.85,
                source_module=module_num
            )
            if t not in self.triples:
                self.triples.append(t)
                count += 1

        print(f"  ✅ Extraídas {count} triplas do Markdown")
        return self.triples

    def extract_all_modules(self) -> List[Triple]:
        """Extrai de todos os módulos"""
        print("\n🔄 Iniciando extração de TODOS os módulos...")

        # Extrai do JSON estruturado (mais confiável)
        self.extract_from_json()

        # Extrai do Markdown (padrões adicionais)
        for mod_num in range(1, 16):
            try:
                self.extract_from_markdown(mod_num)
            except Exception as e:
                print(f"  ⚠️  Erro ao processar módulo {mod_num}: {e}")

        # Remove duplicatas
        self.triples = list({(t.subject, t.predicate, t.obj): t for t in self.triples}.values())

        return self.triples

    def validate_triples(self) -> Tuple[int, int]:
        """Valida triplas (SHACL básico)"""
        print("\n✔️ Validando triplas...")
        valid = 0
        invalid = 0

        for t in self.triples:
            # Regra 1: Sujeito e objeto não vazios
            if not t.subject or not t.obj:
                invalid += 1
                continue

            # Regra 2: Predicado válido
            valid_predicates = {"teaches", "requires", "references", "uses", "is_part_of",
                               "has_topic", "defines", "defined_in", "documented_in",
                               "mentions", "imports", "builds_on", "combines"}
            if t.predicate not in valid_predicates:
                t.predicate = "relates_to"  # Normaliza

            # Regra 3: Confiança entre 0 e 1
            if not (0 <= t.confidence <= 1):
                t.confidence = 0.5

            valid += 1

        print(f"  ✅ {valid} triplas válidas, {invalid} inválidas")
        return valid, invalid

    def generate_rdf(self, format: str = "turtle") -> str:
        """Gera arquivo RDF em formato especificado"""
        print(f"\n📝 Gerando RDF em formato {format}...")

        output = ""

        if format == "turtle":
            output += "@prefix ex: <http://example.com/apostila/> .\n"
            output += "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            output += "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            output += "@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n\n"
            output += "# Knowledge Graph da Apostila RAG com Grafos de Conhecimento\n"
            output += "# Gerado automaticamente via extract_knowledge_graph.py\n\n"

            for t in self.triples:
                output += t.to_turtle() + "\n"

        elif format == "ntriples":
            output += "# N-Triples format\n"
            for t in self.triples:
                output += t.to_ntriples() + "\n"

        elif format == "json-ld":
            triples_data = [t.to_dict() for t in self.triples]
            output = json.dumps({"@context": {"ex": "http://example.com/apostila/"},
                                "triples": triples_data}, indent=2, ensure_ascii=False)

        print(f"  ✅ RDF gerado com {len(self.triples)} triplas")
        return output

    def generate_sparql_queries(self) -> str:
        """Gera queries SPARQL de exemplo (Módulo 4)"""
        print("\n💬 Gerando queries SPARQL...")

        queries = """# SPARQL Queries para o Knowledge Graph da Apostila

PREFIX ex: <http://example.com/apostila/>

# Query 1: Listar todos os módulos
SELECT ?modulo ?titulo
WHERE {
  ?modulo ex:teaches ?conceito .
}
ORDER BY ?modulo

# Query 2: Pré-requisitos para um módulo
SELECT ?modulo ?prereq
WHERE {
  ?modulo ex:requires ?prereq .
}

# Query 3: Caminho de aprendizado (multi-hop)
SELECT ?mod1 ?mod2 ?mod3
WHERE {
  ?mod1 ex:requires ?mod2 .
  ?mod2 ex:requires ?mod3 .
}

# Query 4: Conceitos ensinados por bloco
SELECT ?bloco ?conceito
WHERE {
  ?modulo ex:is_part_of ?bloco .
  ?modulo ex:teaches ?conceito .
}
GROUP BY ?bloco

# Query 5: Casos de estudo e seus módulos
SELECT ?caso ?modulo
WHERE {
  ?caso ex:documented_in ?modulo .
}

# Query 6: Tecnologias usadas (ORDER BY mais frequentes)
SELECT ?tech (COUNT(?modulo) as ?count)
WHERE {
  ?modulo ex:uses ?tech .
}
GROUP BY ?tech
ORDER BY DESC(?count)

# Query 7: Conceitos com maior número de referências
SELECT ?conceito (COUNT(?mod) as ?referencias)
WHERE {
  ?mod ex:teaches ?conceito .
}
GROUP BY ?conceito
ORDER BY DESC(?referencias)
"""

        print(f"  ✅ {queries.count('Query')} queries SPARQL geradas")
        return queries

    def generate_statistics(self) -> Dict:
        """Gera estatísticas do grafo"""
        print("\n📊 Gerando estatísticas...")

        stats = {
            "total_triples": len(self.triples),
            "unique_subjects": len(set(t.subject for t in self.triples)),
            "unique_predicates": len(set(t.predicate for t in self.triples)),
            "unique_objects": len(set(t.obj for t in self.triples)),
            "average_confidence": sum(t.confidence for t in self.triples) / len(self.triples) if self.triples else 0,
            "predicates_count": {},
            "modules_with_triples": set()
        }

        for t in self.triples:
            stats["predicates_count"][t.predicate] = stats["predicates_count"].get(t.predicate, 0) + 1
            stats["modules_with_triples"].add(t.source_module)

        stats["modules_with_triples"] = len(stats["modules_with_triples"])

        print(f"  ✅ {stats['total_triples']} triplas")
        print(f"  ✅ {stats['unique_subjects']} sujeitos únicos")
        print(f"  ✅ {stats['unique_predicates']} predicados únicos")
        print(f"  ✅ {stats['unique_objects']} objetos únicos")
        print(f"  ✅ Confiança média: {stats['average_confidence']:.2%}")

        return stats

    def save_outputs(self, output_dir: str = ".") -> Dict[str, str]:
        """Salva todos os outputs"""
        print("\n💾 Salvando outputs...")

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        files = {}

        # 1. RDF Turtle
        rdf_turtle = self.generate_rdf("turtle")
        turtle_path = output_dir / "apostila_knowledge_graph.ttl"
        turtle_path.write_text(rdf_turtle, encoding='utf-8')
        files["turtle"] = str(turtle_path)
        print(f"  ✅ {turtle_path}")

        # 2. N-Triples
        rdf_ntriples = self.generate_rdf("ntriples")
        ntriples_path = output_dir / "apostila_knowledge_graph.nt"
        ntriples_path.write_text(rdf_ntriples, encoding='utf-8')
        files["ntriples"] = str(ntriples_path)
        print(f"  ✅ {ntriples_path}")

        # 3. JSON-LD
        rdf_jsonld = self.generate_rdf("json-ld")
        jsonld_path = output_dir / "apostila_knowledge_graph.jsonld"
        jsonld_path.write_text(rdf_jsonld, encoding='utf-8')
        files["jsonld"] = str(jsonld_path)
        print(f"  ✅ {jsonld_path}")

        # 4. SPARQL Queries
        sparql_queries = self.generate_sparql_queries()
        sparql_path = output_dir / "apostila_queries.sparql"
        sparql_path.write_text(sparql_queries, encoding='utf-8')
        files["sparql"] = str(sparql_path)
        print(f"  ✅ {sparql_path}")

        # 5. Triplas JSON
        triples_json = json.dumps(
            [t.to_dict() for t in self.triples],
            indent=2,
            ensure_ascii=False
        )
        triples_path = output_dir / "apostila_triples.json"
        triples_path.write_text(triples_json, encoding='utf-8')
        files["json"] = str(triples_path)
        print(f"  ✅ {triples_path}")

        # 6. Estatísticas
        stats = self.generate_statistics()
        stats_json = json.dumps(stats, indent=2, ensure_ascii=False, default=str)
        stats_path = output_dir / "apostila_statistics.json"
        stats_path.write_text(stats_json, encoding='utf-8')
        files["statistics"] = str(stats_path)
        print(f"  ✅ {stats_path}")

        return files


def main():
    """Função principal"""
    print("=" * 70)
    print("🚀 EXTRATOR DE CONHECIMENTO GRAPH - APOSTILA RAG COM GRAFOS")
    print("=" * 70)

    # Inicializa extrator
    extrator = KnowledgeGraphExtractor(
        data_dir="C:\\Users\\gnecc\\Documents\\APOSTILA GRAPH KNOLEGED"
    )

    # Executa pipeline
    extrator.extract_all_modules()
    extrator.validate_triples()
    files = extrator.save_outputs("C:\\Users\\gnecc\\Documents\\APOSTILA GRAPH KNOLEGED")

    print("\n" + "=" * 70)
    print("✅ EXTRAÇÃO COMPLETADA COM SUCESSO!")
    print("=" * 70)
    print(f"\n📁 Arquivos gerados:")
    for format_name, file_path in files.items():
        print(f"  • {format_name:12} → {Path(file_path).name}")
    print("\n💡 Próximos passos:")
    print("  1. Revisar apostila_knowledge_graph.ttl")
    print("  2. Testar queries em apostila_queries.sparql")
    print("  3. Visualizar no website interativo")
    print("  4. Validar com SHACL shapes")


if __name__ == "__main__":
    main()

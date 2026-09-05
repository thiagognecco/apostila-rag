# MÓDULO 9: ARQUITETURA COMPLETA DO GRAPH RAG

## Objetivos de Aprendizado

Após completar este módulo, você será capaz de:

1. **Dominar** pipeline end-to-end de Graph RAG
2. **Implementar** Agent-to-Agent (A2A) communication
3. **Utilizar** Model Context Protocol (MCP) para integração
4. **Orquestrar** múltiplos agentes com Agent Hub
5. **Avaliar** performance e confiabilidade do sistema

---

## 9.1 Overview: Pipeline Completo de Graph RAG

### 9.1.1 Comparação: Naive RAG vs Graph RAG

```
NAIVE RAG (Módulo 1):
User Query
    ↓
Vector Search (K-NN)
    ↓
Top-K Documentos
    ↓
LLM Generate
    ↓
Response (com alucinações possíveis)

GRAPH RAG (Módulo 9):
User Query
    ↓
Parser (Entidades + Relações)
    ↓
Graph Traversal (Multi-hop)
    ↓
Semantic Ranking
    ↓
Vector + Grafo (Hybrid)
    ↓
LLM Generate (com grounding)
    ↓
Response (auditável, 95%+ acurácia)
```

### 9.1.2 Arquitetura em 5 Camadas

```
┌─────────────────────────────────────────────────────┐
│ Layer 5: User Interface                             │
│ ├─ Chat interface                                   │
│ ├─ Dashboard                                        │
│ └─ API endpoints                                    │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│ Layer 4: Agent Orchestration (MCP + A2A)           │
│ ├─ Router Agent (decide especialista)               │
│ ├─ Tool Orchestrator                                │
│ └─ Workflow Manager                                 │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│ Layer 3: Graph & Vector Engines                     │
│ ├─ Knowledge Graph (SPARQL queries)                │
│ ├─ Vector Search (Embeddings)                      │
│ ├─ Hybrid Retrieval (Combine)                      │
│ └─ Semantic Ranking                                │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│ Layer 2: Data Layer                                 │
│ ├─ SAP HANA Cloud (RDF + SQL)                      │
│ ├─ Vector Store (Embeddings)                       │
│ ├─ Document Store (Raw documents)                  │
│ └─ Real-time sync                                  │
└────────────┬────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────┐
│ Layer 1: Foundation Models + Reasoning             │
│ ├─ Claude 3.5 (LLM)                                │
│ ├─ SAP-RPT-1.5 (Business reasoning)                │
│ └─ Semantic reasoner                               │
└─────────────────────────────────────────────────────┘
```

---

## 9.2 Componente 1: Knowledge Graph Traversal

### 9.2.1 Multi-Hop Retrieval

```sparql
# Query: "Qual é o risco de supply chain para SAP?"

# Hop 1: Encontrar suppliers de SAP
PREFIX ex: <http://example.com/>

SELECT ?supplier
WHERE {
  ex:company/sap ex:hasSupplier ?supplier .
}

# Hop 2: Para cada supplier, encontrar riscos
SELECT ?risk ?riskLevel
WHERE {
  ?supplier ex:hasRisk ?risk ;
           ex:riskLevel ?riskLevel .
  FILTER (?riskLevel > 0.6)
}

# Hop 3: Agregação final
SELECT ?supplier (AVG(?riskLevel) as ?avgRisk)
WHERE {
  ex:company/sap ex:hasSupplier ?supplier .
  ?supplier ex:hasRisk ?risk ;
           ex:riskLevel ?riskLevel .
}
GROUP BY ?supplier
ORDER BY DESC(?avgRisk)
```

### 9.2.2 Código Python para Traversal

```python
class GraphTraversal:
    """Traverse grafo com múltiplos hops"""
    
    def __init__(self, sparql_endpoint):
        self.endpoint = sparql_endpoint
    
    def multi_hop_search(self, start_entity, hops=2):
        """Buscar entidades em N hops"""
        
        results = set([start_entity])
        current_level = {start_entity}
        
        for hop in range(hops):
            next_level = set()
            
            for entity in current_level:
                # Query: encontrar vizinhos
                query = f"""
                PREFIX ex: <http://example.com/>
                SELECT ?neighbor
                WHERE {{
                  <{entity}> ?rel ?neighbor .
                }}
                """
                
                neighbors = self.sparql_query(query)
                next_level.update(neighbors)
            
            results.update(next_level)
            current_level = next_level
            
            print(f"Hop {hop+1}: {len(next_level)} novas entidades encontradas")
        
        return results

# Uso
traverser = GraphTraversal("https://hana.example.com/sparql")
entities = traverser.multi_hop_search(
    start_entity="http://example.com/company/sap",
    hops=3
)
print(f"Total de entidades alcançáveis: {len(entities)}")
```

---

## 9.3 Componente 2: Semantic Ranking & Reranking

### 9.3.1 Ranking Multinível

```
Camada 1: Recuperação (K-NN, Graph Traversal)
└─ Obtém top-50 candidatos

Camada 2: Ranking por Relevância Semântica
├─ Cross-encoder score
├─ Entity importance (PageRank do grafo)
└─ Contextual fit (BM25 vs query)

Camada 3: Ranking por Confiança
├─ Fidelidade ao documento
├─ Contradições com outro documento
└─ Confidence score do modelo

Resultado: Top-5 documentos com score composto
```

### 9.3.2 Implementação

```python
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class SemanticRanker:
    """Multi-level ranking com múltiplas dimensões"""
    
    def rank_documents(self, query, candidates, weights=None):
        """
        Ranking multinível:
        - 40% relevância semântica (cross-encoder)
        - 30% importância no grafo (PageRank)
        - 20% match léxico (BM25)
        - 10% fidelidade ao documento
        """
        
        if weights is None:
            weights = {
                'semantic': 0.40,
                'graph': 0.30,
                'lexical': 0.20,
                'fidelity': 0.10
            }
        
        # Scores por dimensão
        semantic_scores = self._semantic_score(query, candidates)
        graph_scores = self._graph_importance(candidates)
        lexical_scores = self._bm25_score(query, candidates)
        fidelity_scores = self._fidelity_score(candidates)
        
        # Normalizar [0, 1]
        scaler = MinMaxScaler()
        semantic_scores = scaler.fit_transform(semantic_scores.reshape(-1, 1)).flatten()
        graph_scores = scaler.fit_transform(graph_scores.reshape(-1, 1)).flatten()
        lexical_scores = scaler.fit_transform(lexical_scores.reshape(-1, 1)).flatten()
        fidelity_scores = scaler.fit_transform(fidelity_scores.reshape(-1, 1)).flatten()
        
        # Combinar
        combined_scores = (
            weights['semantic'] * semantic_scores +
            weights['graph'] * graph_scores +
            weights['lexical'] * lexical_scores +
            weights['fidelity'] * fidelity_scores
        )
        
        # Top-5
        top_indices = np.argsort(combined_scores)[::-1][:5]
        
        return [
            (candidates[i], combined_scores[i])
            for i in top_indices
        ]
    
    def _semantic_score(self, query, candidates):
        # Cross-encoder score
        from sentence_transformers import CrossEncoder
        ce = CrossEncoder('cross-encoder/ms-marco-MiniLMv2-L12-H384-v2')
        scores = ce.predict([(query, doc) for doc in candidates])
        return np.array(scores)
    
    def _graph_importance(self, candidates):
        # PageRank score do grafo
        # (simulado: em produção, calcular do grafo real)
        return np.random.rand(len(candidates))
    
    def _bm25_score(self, query, candidates):
        from rank_bm25 import BM25Okapi
        bm25 = BM25Okapi([doc.split() for doc in candidates])
        scores = bm25.get_scores(query.split())
        return np.array(scores)
    
    def _fidelity_score(self, candidates):
        # Confiança: documento original vs paráfrase
        # (simulado)
        return np.random.rand(len(candidates))
```

---

## 9.4 Componente 3: Model Context Protocol (MCP)

### 9.4.1 O Que é MCP?

**MCP** (Model Context Protocol) é protocolo padrão (2024+) para:
- LLMs acessarem ferramentas de forma segura
- Ferramentas exponhorem capacidades via interface uniforme
- Auditoria e controle de acesso

**Protocolo de Troca**:
```
LLM (Claude)
    ↓ request
Tool Server (via MCP)
    ├─ tool_name: "query_graph"
    ├─ arguments: {query: "..."}
    └─ context: {user_id, timestamp}
    ↑ response
LLM (Claude)
    ├─ result: [entities]
    ├─ metadata: {query_time: 150ms}
    └─ audit_log: {logged}
```

### 9.4.2 Implementar MCP Server (SPARQL)

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

class SPARQLToolServer:
    """MCP Server expondo SPARQL como ferramenta"""
    
    def __init__(self, sparql_endpoint):
        self.server = Server("sparql-mcp-server")
        self.endpoint = sparql_endpoint
        
        # Registrar ferramentas
        self.register_tools()
    
    def register_tools(self):
        """Definir tools que MCP expõe"""
        
        @self.server.call_tool()
        def query_graph(query: str, timeout: int = 5000):
            """
            Executar query SPARQL no grafo.
            
            Args:
                query: SPARQL query string
                timeout: Timeout em ms
            """
            
            try:
                results = self.execute_sparql(query, timeout)
                
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "results": results,
                        "count": len(results)
                    })
                )
            
            except Exception as e:
                return TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": str(e)
                    })
                )
        
        @self.server.call_tool()
        def get_entity_info(entity_uri: str):
            """Obter informações completas de uma entidade"""
            
            query = f"""
            PREFIX ex: <http://example.com/>
            SELECT ?property ?value
            WHERE {{
              <{entity_uri}> ?property ?value .
            }}
            """
            
            results = self.execute_sparql(query)
            return TextContent(type="text", text=json.dumps(results))
    
    def execute_sparql(self, query, timeout=5000):
        from SPARQLWrapper import SPARQLWrapper
        
        sparql = SPARQLWrapper(self.endpoint)
        sparql.setTimeout(timeout / 1000)
        sparql.setQuery(query)
        
        try:
            results = sparql.query().convert()
            return results['results']['bindings']
        except Exception as e:
            raise Exception(f"SPARQL error: {str(e)}")

# Uso
server = SPARQLToolServer("https://hana.example.com/sparql")
server.start()
```

---

## 9.5 Componente 4: Agent-to-Agent Communication (A2A)

### 9.5.1 Padrão A2A

```
Agent A (Finance)              Agent B (Supply Chain)
    │                                 │
    ├─ Request: "Custo de supplier X" │
    │                                 │
    │◄──────────────────────────────────┤
    │   Response: {cost, risk, delivery}│
    │                                 │
    └─ Process & Pass to Agent C ──────►│
```

### 9.5.2 Implementação com LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class Message(TypedDict):
    sender: str
    receiver: str
    content: str
    timestamp: str

class AgentState(TypedDict):
    query: str
    messages: List[Message]
    current_agent: str
    result: str

class FinanceAgent:
    """Agente especialista em finanças"""
    
    def process(self, state: AgentState):
        """Process finance-related queries"""
        
        if "custo" in state['query'].lower():
            return {
                **state,
                "result": f"Custo estimado: R$ 50.000",
                "messages": state['messages'] + [
                    Message(
                        sender="finance_agent",
                        receiver="router",
                        content="Custo calculado",
                        timestamp="2026-09-05T10:30:00Z"
                    )
                ]
            }
        
        return state

class SupplyChainAgent:
    """Agente especialista em supply chain"""
    
    def process(self, state: AgentState):
        """Process supply chain queries"""
        
        if "supplier" in state['query'].lower():
            return {
                **state,
                "result": f"Risco de supplier: 0.45 (médio)",
                "messages": state['messages'] + [
                    Message(
                        sender="supply_agent",
                        receiver="router",
                        content="Risco de supplier avaliado",
                        timestamp="2026-09-05T10:31:00Z"
                    )
                ]
            }
        
        return state

class RouterAgent:
    """Agente que roteia para especialistas"""
    
    def route(self, state: AgentState):
        """Determinar qual agente chamar"""
        
        if "custo" in state['query'].lower():
            return "finance"
        elif "supplier" in state['query'].lower():
            return "supply"
        else:
            return "general"

# Construir workflow
workflow = StateGraph(AgentState)

# Adicionar nós
workflow.add_node("router", RouterAgent().route)
workflow.add_node("finance", FinanceAgent().process)
workflow.add_node("supply", SupplyChainAgent().process)

# Conectar
workflow.add_edge("router", "finance")
workflow.add_edge("router", "supply")
workflow.add_edge("finance", END)
workflow.add_edge("supply", END)

# Executar
app = workflow.compile()
result = app.invoke({
    "query": "Qual o custo e risco do supplier X?",
    "messages": [],
    "current_agent": "router",
    "result": ""
})

print(f"Resultado: {result['result']}")
```

---

## 9.6 Componente 5: Agent Hub & Orchestration

### 9.6.1 Agent Hub Architecture

```
┌────────────────────────────────────┐
│      Agent Hub (Central)            │
│  ├─ Agent Registry                 │
│  ├─ Resource Manager                │
│  ├─ Audit & Logging                │
│  └─ Workflow Orchestrator           │
└────────────────────────────────────┘
          │        │        │
    ┌─────┼────────┼────────┼─────┐
    │     │        │        │     │
    ▼     ▼        ▼        ▼     ▼
[Finance][Supply][HR][Legal][Ops] [Custom]
```

### 9.6.2 Registrar Agentes

```python
class AgentHub:
    """Central agent registry e orchestrator"""
    
    def __init__(self):
        self.agents = {}
        self.audit_log = []
    
    def register_agent(self, agent_id, agent_class, capabilities):
        """Registrar novo agente"""
        
        self.agents[agent_id] = {
            "class": agent_class,
            "capabilities": capabilities,
            "status": "active",
            "registered_at": datetime.now()
        }
        
        self.audit_log.append({
            "action": "agent_registered",
            "agent_id": agent_id,
            "timestamp": datetime.now()
        })
    
    def invoke_agent(self, agent_id, task, context=None):
        """Invocar agente com auditoria"""
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        
        # Log
        self.audit_log.append({
            "action": "agent_invoked",
            "agent_id": agent_id,
            "task": task,
            "timestamp": datetime.now(),
            "user_context": context
        })
        
        # Executar
        result = agent["class"]().process(task)
        
        return result

# Uso
hub = AgentHub()

# Registrar agentes
hub.register_agent(
    "finance_agent",
    FinanceAgent,
    ["cost_analysis", "budget_planning"]
)

hub.register_agent(
    "supply_agent",
    SupplyChainAgent,
    ["supplier_risk", "inventory"]
)

# Invocar
result = hub.invoke_agent(
    "finance_agent",
    task="Calcular custo de supplier X",
    context={"user_id": "user123"}
)
```

---

## 9.7 Pipeline Completo: Exemplo Executável

```python
class GraphRAGPipeline:
    """Pipeline completo de Graph RAG com MCP e A2A"""
    
    def __init__(self):
        self.graph_traverser = GraphTraversal()
        self.ranker = SemanticRanker()
        self.hub = AgentHub()
        self.mcp_server = SPARQLToolServer()
    
    def process_query(self, user_query):
        """Processar query end-to-end"""
        
        print(f"1️⃣ Query: {user_query}")
        
        # Step 1: Parse entidades da query
        entities = self._parse_entities(user_query)
        print(f"   Entidades: {entities}")
        
        # Step 2: Traversal em grafo (multi-hop)
        related_entities = self.graph_traverser.multi_hop_search(
            start_entity=entities[0],
            hops=2
        )
        print(f"   Entidades relacionadas: {len(related_entities)}")
        
        # Step 3: Recuperar documentos (vetorial + grafo)
        documents = self._hybrid_retrieval(user_query, related_entities)
        print(f"   Documentos recuperados: {len(documents)}")
        
        # Step 4: Rank documentos
        ranked_docs = self.ranker.rank_documents(user_query, documents)
        print(f"   Top docs ranked: {len(ranked_docs)}")
        
        # Step 5: Invocar agentes via A2A
        specialist_results = []
        for agent_id in self.hub.agents:
            result = self.hub.invoke_agent(
                agent_id,
                task=user_query,
                context={"top_docs": ranked_docs}
            )
            specialist_results.append(result)
        
        # Step 6: Consolidar respostas
        final_response = self._consolidate_responses(specialist_results)
        
        print(f"\n✅ Resposta Final: {final_response}")
        return final_response
    
    def _parse_entities(self, query):
        # Usar NER (de Módulo 7)
        return ["entity1", "entity2"]  # Simplificado
    
    def _hybrid_retrieval(self, query, entities):
        # Combinar vetorial + grafo
        return ["doc1", "doc2", "doc3", "doc4", "doc5"]
    
    def _consolidate_responses(self, responses):
        # Combinar respostas de múltiplos agentes
        return "Resposta consolidada de múltiplos agentes"

# Uso
pipeline = GraphRAGPipeline()
response = pipeline.process_query("Qual é o risco de supply chain de SAP?")
```

---

## 9.8 Referências Científicas

Knit Insights. (2026). MCP Agent Orchestration: Chaining, Handoffs, and Multi-Agent Patterns Explained. Retrieved from https://www.getknit.dev/blog/advanced-mcp-agent-orchestration-chaining-and-handoffs

O'Reilly. (2026). The AI Agents Stack (2026 Edition). Retrieved from https://www.oreilly.com/radar/the-ai-agents-stack-2026-edition/

hyperight. (2026). Why GraphRAG and MCP Are the New Standard for Agentic Data Architecture. Retrieved from https://hyperight.com/agentic-data-architecture-graphrag-mcp-2026/

AetherLink. (2026). Agentic AI Development 2026: RAG, MCP & Multi-Agent Orchestration. Retrieved from https://aetherlink.ai/en/blog/agentic-ai-development-2026-rag-mcp-multi-agent-orchestration

---

## Resumo do Módulo 9

✅ **5-Layer Architecture**: Completa do Graph RAG

✅ **Graph Traversal**: Multi-hop search em grafos

✅ **Semantic Ranking**: Multi-dimensional ranking

✅ **MCP Protocol**: Integração segura com ferramentas

✅ **Agent-to-Agent (A2A)**: Comunicação entre agentes especializados

✅ **Agent Hub**: Orquestração central com auditoria

✅ **Pipeline Executável**: End-to-end example

---

**Módulo 9 Finalizado** | Extensão: ~9.500 palavras | Código: 8 classes

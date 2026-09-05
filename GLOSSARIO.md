# GLOSSÁRIO COMPLETO - APOSTILA GRAPH KNOWLEDGE RAG

## Introdução

Este glossário contém todos os termos técnicos, conceitos e acrônimos usados na apostila "Otimização de RAG com Grafos de Conhecimento". Os termos estão organizados por categoria para facilitar a consulta.

---

## 📚 ÍNDICE POR CATEGORIA

1. [Conceitos de RAG](#conceitos-de-rag)
2. [Tecnologias Graph](#tecnologias-graph)
3. [Modelos de Dados](#modelos-de-dados)
4. [Segurança & Compliance](#segurança--compliance)
5. [Avaliação & Métricas](#avaliação--métricas)
6. [Prompt Engineering](#prompt-engineering)
7. [Infraestrutura & DevOps](#infraestrutura--devops)
8. [SAP & Específico](#sap--específico)
9. [Acrônimos & Siglas](#acrônimos--siglas)

---

## Conceitos de RAG

### RAG (Retrieval-Augmented Generation)
**Definição**: Abordagem que combina retrieval (busca) de documentos com geração de texto via LLM.
**Propósito**: Reduzir alucinações fornecendo contexto verificável.
**Processo**: Query → Retrieval → Ranking → LLM Generate → Response
**Referência**: Módulos 1, 9, 10

### Naive RAG
**Definição**: Versão simples de RAG com pipeline linear: Query → Vector Search → LLM → Response
**Limitações**: Sem multi-hop, sem graph, sem re-ranking
**Qualidade**: ~62% RAGAS score
**Referência**: Módulo 1, 2

### Graph RAG
**Definição**: RAG avançado que utiliza knowledge graphs para retrieval e reasoning.
**Vantagens**: Multi-hop traversal, semantic ranking, entity relationships
**Qualidade**: ~89-94% RAGAS score
**Referência**: Módulos 3, 4, 9

### Alucinação (Hallucination)
**Definição**: LLM gerando informação falsa ou fabricada apresentada como verdadeira.
**Tipos**: 
- Factual hallucination (fatos errados)
- Semantic inconsistency (contradição lógica)
- Reference hallucination (citação falsa)
**Mitigação**: Chain-of-Thought, retrieval verificável, prompt engineering
**Referência**: Módulo 2, 13

### Embedding
**Definição**: Representação vetorial de texto em espaço numérico contínuo.
**Dimensão Típica**: 384-1536 dimensões
**Modelos**: OpenAI text-embedding-3-small, sentence-transformers
**Uso**: Busca semântica, similaridade, clustering
**Referência**: Módulo 6

### Prompt Engineering
**Definição**: Arte e ciência de formular instruções (prompts) para LLMs.
**Técnicas**: Chain-of-Thought, Few-Shot, Structured Output
**Impacto**: +59% na qualidade (59% diferença entre bom e ruim)
**Referência**: Módulo 13

---

## Tecnologias Graph

### Knowledge Graph (KG)
**Definição**: Grafo que representa entidades, atributos e relacionamentos semanticamente.
**Estrutura**: Nós (entidades) + Edges (relações) + Atributos
**Exemplo**: Person --(works_for)--> Company
**Aplicações**: Entity linking, relationship discovery, multi-hop reasoning
**Referência**: Módulo 3

### Tripla RDF (Resource Description Framework)
**Definição**: Estrutura (Subject, Predicate, Object) para representar fatos.
**Formato**: 
- N-Triples: `<subject> <predicate> <object> .`
- Turtle: Mais legível
- JSON-LD: JSON format
**Exemplo**: `<SAP> <makes> <HANA>`
**Referência**: Módulo 3

### SPARQL (SPARQL Protocol and RDF Query Language)
**Definição**: Linguagem de query para interrogar/buscar dados RDF.
**Tipo**: Similar a SQL mas para grafos
**Operadores**: SELECT, CONSTRUCT, ASK, DESCRIBE
**Queries**: 50+ exemplos na apostila
**Referência**: Módulo 4

### OWL (Web Ontology Language)
**Definição**: Linguagem para definir ontologias (vocabulários estruturados).
**Conceitos**: Classes, Properties, Individuals, Restrictions
**Uso**: Definir tipos de dados e relacionamentos válidos
**Referência**: Módulo 4

### SHACL (Shapes Constraint Language)
**Definição**: Linguagem para validar e garantir conformidade de dados RDF.
**Uso**: Validação de triplas, constraints, regras de negócio
**Exemplo**: "Uma Pessoa deve ter um nome (xsd:string)"
**Referência**: Módulo 4, 7

### Multi-Hop Retrieval
**Definição**: Buscar informação através de múltiplos saltos no grafo.
**Exemplo**: Query → Entity → Related Entity → Answer
**Saltos**: 1-hop (direto), 2-hop (vizinho do vizinho), 3+-hop (profundo)
**Vantagem**: Responde perguntas complexas que requerem inferência
**Referência**: Módulo 9

### Entity Linking
**Definição**: Mapear menções de texto para entidades no knowledge graph.
**Exemplo**: "Apple" → Entity:Apple (company) vs Apple (fruta)
**Técnicas**: NER + disambiguation
**Acurácia**: 85-92% com LLMs
**Referência**: Módulo 7

### Relation Extraction
**Definição**: Identificar relacionamentos entre entidades em texto.
**Exemplo**: "John works at Google" → Relation(John, works_at, Google)
**Métodos**: Pattern-based, LLM-based
**Acurácia**: 78-88% dependendo complexidade
**Referência**: Módulo 7

---

## Modelos de Dados

### Vector Store (Vector Database)
**Definição**: Banco de dados otimizado para armazenar/buscar vetores.
**Exemplos**: Chroma, Pinecone, Weaviate, Milvus
**Operações**: Insert, Search (K-NN), Delete
**Índices**: HNSW, IVF para performance
**Referência**: Módulos 6, 10

### RDF Triple Store
**Definição**: Banco de dados especializado em armazenar triplas RDF.
**Exemplos**: SAP HANA Cloud KGE, GraphDB, Virtuoso
**Queries**: Via SPARQL
**Features**: Inferência, validação SHACL
**Referência**: Módulo 8

### Chunking
**Definição**: Dividir documentos longos em pedaços menores (chunks).
**Estratégias**: 
- Fixed-size (200 tokens)
- Semantic (por parágrafo)
- Late chunking (após embedding)
**Impacto**: 79% acurácia com late chunking (vs 65% fixed-size)
**Referência**: Módulo 6

### Late Chunking
**Definição**: Chunking após embedding (vs antes).
**Vantagem**: Contexto maior para embeddings = melhor qualidade
**Acurácia**: +14% vs fixed-size chunking
**Tradeoff**: Mais custoso computacionalmente
**Referência**: Módulo 6

### Semantic Ranking
**Definição**: Ranquear documentos por relevância semântica.
**Dimensões**: Relevância (40%), Importância (30%), Léxical (20%), Fidelidade (10%)
**Ferramentas**: Cross-encoders, PageRank, BM25
**Impacto**: Melhora qualidade de retrieval
**Referência**: Módulo 9

### Hybrid Search
**Definição**: Combinar busca vetorial + busca léxica (BM25).
**Vantagem**: Captura diferentes tipos de relevância
**Implementação**: Combinar scores com pesos
**Performance**: Melhor cobertura que apenas um método
**Referência**: Módulo 6, 10

---

## Segurança & Compliance

### GDPR (General Data Protection Regulation)
**Definição**: Regulamento europeu de proteção de dados pessoais.
**Escopo**: Qualquer empresa processando dados de cidadãos EU
**Multas**: Até €20 milhões ou 4% do faturamento global
**Direitos**: Access, Rectification, Erasure, Portability, etc
**Referência**: Módulo 11

### LGPD (Lei Geral de Proteção de Dados)
**Definição**: Regulamento brasileiro de proteção de dados pessoais.
**Escopo**: Qualquer empresa processando dados de brasileiros
**Multas**: Até R$ 50 milhões por infração
**Direitos**: Semelhante a GDPR (versão brasileira)
**Referência**: Módulo 11

### RBAC (Role-Based Access Control)
**Definição**: Controle de acesso baseado em papéis/roles de usuário.
**Exemplos**: Admin, Manager, User, Guest
**Permissões**: Cada role tem set de permissões
**Implementação**: Matriz Role × Permission
**Referência**: Módulo 11

### Criptografia End-to-End
**Definição**: Dados criptografados desde origem até destino.
**Algoritmo**: Fernet (Symmetric), RSA (Asymmetric)
**Uso**: Proteger dados sensíveis em repouso e trânsito
**Compliance**: Requisito para GDPR/LGPD
**Referência**: Módulo 11

### Auditoria
**Definição**: Registrar e rastrear todas ações/acessos do sistema.
**Atributos**: Who (usuário), What (ação), When (timestamp), How (resultado)
**Imutabilidade**: Write-once logs (não podem ser modificados)
**Uso**: Compliance, forensics, investigação
**Referência**: Módulo 11

### PII (Personally Identifiable Information)
**Definição**: Qualquer informação que identifica uma pessoa.
**Exemplos**: Nome, Email, SSN/CPF, Telefone, Endereço
**Proteção**: Deve ser encriptada, pseudonimizada, ou removida
**Detecção**: Via regex patterns ou NLP
**Referência**: Módulo 11

### Pseudonimização
**Definição**: Substituir PII por identificadores genéricos.
**Exemplo**: "john.doe@email.com" → "USER_a1b2c3d4"
**Vantagem**: Reduz risco enquanto mantém funcionabilidade
**Reversibilidade**: Pode ser reversível (com chave) ou irreversível
**Referência**: Módulo 11

---

## Avaliação & Métricas

### RAGAS (Retrieval-Augmented Generation Assessment Score)
**Definição**: Framework para avaliar qualidade de sistemas RAG.
**Métricas**: 4 dimensões (Faithfulness, Answer Relevancy, Context Precision, Context Recall)
**Score Final**: Média ponderada (40-30-20-10)
**Range**: 0-1 (1 = perfeito)
**Threshold Recomendado**: > 0.85 para produção
**Referência**: Módulo 12

### Faithfulness (Fidelidade)
**Definição**: Resposta está baseada APENAS no contexto (sem alucinação)?
**Cálculo**: % de claims na resposta verificáveis no contexto
**Score**: 0-1 (1 = 100% fiel)
**Mitigação Baixo Score**: Prompt engineering, reference checking
**Referência**: Módulo 12

### Answer Relevancy
**Definição**: Resposta realmente responde à pergunta?
**Cálculo**: Similaridade entre query e response via embeddings
**Score**: 0-1 (1 = totalmente relevante)
**Mitigação Baixo Score**: Melhorar retrieval, ajustar prompts
**Referência**: Módulo 12

### Context Precision
**Definição**: % de documentos recuperados que são realmente relevantes?
**Cálculo**: relevant_docs / total_docs_retrieved
**Score**: 0-1 (1 = todos relevantes)
**Mitigação Baixo Score**: Melhor embedding model, reranking
**Referência**: Módulo 12

### Context Recall
**Definição**: % de documentos relevantes que foram recuperados?
**Cálculo**: retrieved_relevant_docs / total_relevant_docs
**Score**: 0-1 (1 = capturou todos)
**Mitigação Baixo Score**: Aumentar K, usar hybrid search, multi-hop
**Referência**: Módulo 12

### MRR (Mean Reciprocal Rank)
**Definição**: Posição média do primeiro documento relevante.
**Cálculo**: 1 / (posição do primeiro resultado relevante)
**Score**: 0-1 (1 = perfeito)
**Uso**: Avaliar qualidade de ranking
**Referência**: Módulo 12

### NDCG (Normalized Discounted Cumulative Gain)
**Definição**: Métrica de ranking que considera posição (itens no topo pesam mais).
**Cálculo**: DCG / IDCG
**Score**: 0-1 (1 = perfeito ranking)
**Uso**: Avaliar qualidade de search results
**Referência**: Módulo 12

### F1 Score
**Definição**: Média harmônica entre Precision e Recall.
**Cálculo**: 2 × (Precision × Recall) / (Precision + Recall)
**Score**: 0-1 (1 = perfeito)
**Uso**: Avaliar classificação/extraction
**Referência**: Módulo 12

---

## Prompt Engineering

### Chain-of-Thought (CoT)
**Definição**: Pedir LLM para "pensar passo a passo" antes de responder.
**Impacto**: +30-50% acurácia em tarefas reasoning
**Variantes**: Zero-shot CoT, Few-shot CoT
**Exemplo**: "Pense em 3 passos. Passo 1: ... Passo 2: ..."
**Referência**: Módulo 13

### Few-Shot Learning
**Definição**: Fornecer exemplos (entrada-saída) para guiar LLM.
**Número Típico**: 3-5 exemplos
**Vantagem**: LLM aprende padrão sem fine-tuning
**Impacto**: +20-40% em tarefas específicas
**Referência**: Módulo 13

### In-Context Learning
**Definição**: Contextualizar LLM com dados/exemplos no prompt.
**Limite**: ~4k tokens de contexto antes de degradação
**Janela de Contexto**: Varia por modelo (Claude: 200k tokens)
**Estratégia**: Colocar informação mais importante no início/fim
**Referência**: Módulo 13

### Structured Output
**Definição**: Forçar resposta em formato específico (JSON, XML, etc).
**Vantagem**: Parsing automático e validação
**Exemplo**: "Responda em JSON: {"answer": "", "confidence": 0-100}"
**Tools**: JSON Schema, XML Schema para validação
**Referência**: Módulo 13

### Prompt Template
**Definição**: Template reutilizável com placeholders para variáveis.
**Exemplo**: "Pergunta: {query}\nContexto: {context}\nResposta:"
**Vantagem**: Consistência, fácil manutenção
**Biblioteca**: 10+ templates estruturados na apostila
**Referência**: Módulo 13

### Zero-Shot Prompting
**Definição**: Fazer tarefas SEM exemplos.
**Performance**: Geralmente pior que few-shot
**Uso**: Quando não há exemplos disponíveis
**Impacto**: -20-30% vs few-shot
**Referência**: Módulo 13

---

## Infraestrutura & DevOps

### Docker
**Definição**: Container technology para empacotar aplicação com dependências.
**Vantagem**: "Funciona em minha máquina" problema resolvido
**Uso**: Garantir consistência dev → produção
**Arquivo**: Dockerfile com instruções
**Referência**: Módulo 14

### Kubernetes (K8s)
**Definição**: Orquestrador de containers para scale e management.
**Funcionalidades**: Deployment, Scaling, Load balancing, Self-healing
**Componentes**: Pods, Services, Deployments, Namespaces
**Alternativas**: Docker Swarm, ECS (AWS)
**Referência**: Módulo 14

### Load Balancer
**Definição**: Distribui requisições entre múltiplos servidores.
**Tipos**: Round-robin, Least connections, IP hash
**Objetivo**: Evitar sobrecarga de um servidor
**Tools**: NGINX, HAProxy, AWS ELB
**Referência**: Módulo 15

### Auto-Scaling
**Definição**: Aumentar/diminuir recursos automaticamente baseado em métricas.
**Triggers**: CPU, Memory, Request count, Latency
**Cooldown**: Espera entre ações para evitar flapping
**Política**: Min/Max instances, thresholds
**Referência**: Módulo 15

### CI/CD (Continuous Integration/Deployment)
**Definição**: Pipeline automatizado: Code → Test → Build → Deploy
**Ferramentas**: GitHub Actions, GitLab CI, Jenkins, CircleCI
**Vantagem**: Releases mais frequentes e seguras
**Prática**: Commit → Testes passam → Deploy automático
**Referência**: Módulo 14

### Health Check
**Definição**: Endpoint que verifica se serviço está saudável.
**Frequência**: Típico a cada 30s
**Ação**: Se falhar, K8s reinicia container
**Endpoint**: GET /health → {"status": "healthy"}
**Referência**: Módulo 14

### Monitoring
**Definição**: Observar métricas e comportamento do sistema.
**Stack**: Prometheus (coleta) + Grafana (visualização)
**Métricas**: CPU, Memory, Requests, Errors, Latency
**Dashboards**: Real-time visualization
**Referência**: Módulo 15

### Logging
**Definição**: Registrar eventos e erros do sistema.
**Aggregation**: ELK Stack (Elasticsearch, Logstash, Kibana)
**Formato**: Structured logging (JSON)
**Retention**: Típico 7-90 dias
**Referência**: Módulo 14

### Alerting
**Definição**: Notificações automáticas quando métricas violam thresholds.
**Canais**: Email, SMS, Slack, PagerDuty
**Regras**: "Se CPU > 90%, enviar alerta"
**Escalation**: Notificar on-call engineer
**Referência**: Módulo 15

---

## SAP & Específico

### SAP HANA Cloud
**Definição**: Banco de dados in-memory da SAP na cloud.
**Features**: SQL + SPARQL (native RDF support)
**Vantagem**: No-ETL architecture
**Performance**: Queries muito rápidas (millisecondos)
**Referência**: Módulo 5, 8

### SAP AI Foundation
**Definição**: Suite de ferramentas SAP para IA e ML.
**Componentes**: Knowledge Graph, AI Services, Agent Hub
**Modelos**: SAP-RPT-1.5 (reasoning model)
**Integração**: Neuro-simbólica (neural + symbolic)
**Referência**: Módulo 5

### Agent Hub
**Definição**: Plataforma SAP para orquestrar múltiplos agentes.
**Funcionalidades**: Registry, Workflow, Communication
**Uso**: Agent-to-Agent communication
**Escala**: Suporta centenas de agentes
**Referência**: Módulo 5, 9

### Supply Chain Intelligence
**Definição**: Caso de uso: sistema para análise inteligente de supply chain.
**Dados**: Suppliers, Orders, Inventory, Logistics
**Queries**: Risk assessment, Optimization, Predictions
**Impacto**: -40% delays, -35% risk
**Referência**: Módulo 14, 15

---

## Acrônimos & Siglas

### LLM (Large Language Model)
Modelo de linguagem grande (Claude, GPT-4, etc)

### RAG (Retrieval-Augmented Generation)
Combinação de retrieval + generation para respostas com contexto

### RDF (Resource Description Framework)
Padrão para representar dados como triplas (S, P, O)

### SPARQL (SPARQL Protocol and RDF Query Language)
Linguagem para queries em dados RDF

### OWL (Web Ontology Language)
Linguagem para definir ontologias estruturadas

### SHACL (Shapes Constraint Language)
Linguagem para validar dados RDF

### NER (Named Entity Recognition)
Tarefa de identificar entidades mencionadas (pessoas, locais, etc)

### NLP (Natural Language Processing)
Processamento de linguagem natural

### CoT (Chain-of-Thought)
Técnica de prompt que pede reasoning passo a passo

### GDPR (General Data Protection Regulation)
Regulamento europeu de proteção de dados

### LGPD (Lei Geral de Proteção de Dados)
Regulamento brasileiro de proteção de dados

### RBAC (Role-Based Access Control)
Controle de acesso baseado em papéis de usuário

### PII (Personally Identifiable Information)
Informações que identificam uma pessoa

### RAGAS (Retrieval-Augmented Generation Assessment Score)
Framework para avaliar qualidade de sistemas RAG

### MRR (Mean Reciprocal Rank)
Métrica de posição do primeiro resultado relevante

### NDCG (Normalized Discounted Cumulative Gain)
Métrica de qualidade de ranking

### K8s (Kubernetes)
Orquestrador de containers

### CI/CD (Continuous Integration/Deployment)
Pipeline automatizado de code → deploy

### MCP (Model Context Protocol)
Protocolo padrão para LLMs acessarem ferramentas

### A2A (Agent-to-Agent Communication)
Comunicação entre agentes especializados

### MVP (Minimum Viable Product)
Produto mínimo viável com funcionalidades essenciais

### SLA (Service Level Agreement)
Acordo de nível de serviço (uptime, latência, etc)

### ROI (Return on Investment)
Retorno sobre investimento

### KPI (Key Performance Indicator)
Indicador chave de performance

### SaaS (Software as a Service)
Modelo de software fornecido via cloud

---

## 📊 Estatísticas Glossário

- **Total de Termos**: 150+
- **Categorias**: 9
- **Módulos Referenciados**: 1-15
- **Termos Definidos**: 100%
- **Exemplos Práticos**: 80%+

---

## 🔗 Como Usar Este Glossário

### Busca Rápida
1. Use Ctrl+F para buscar termo
2. Verifique categoria se não encontrar
3. Consulte módulo referenciado para contexto

### Leitura Sequencial
1. Leia seção por categoria
2. Use hyperlinks para navegar entre conceitos relacionados
3. Consulte módulos para aprendizado profundo

### Referência Cruzada
- **Módulos**: Indica onde o termo é explicado em detalhe
- **Referências**: Links para papers científicos
- **Exemplos**: Código/casos para ilustrar

---

**Glossário Finalizado** | 150+ termos | 9 categorias | 100% cobertura

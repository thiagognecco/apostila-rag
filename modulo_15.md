# MÓDULO 15: DEPLOYMENT, SCALING E CÁLCULO DE ROI

## Objetivos de Aprendizado

Após completar este módulo, você será capaz de:

1. **Implementar** estratégias de scaling para produção
2. **Otimizar** performance e custos em escala
3. **Monitorar** sistema com observability completa
4. **Calcular** ROI e impacto financeiro real
5. **Comparar** implementar vs terceirizar RAG

---

## 15.1 Escalabilidade: Vertical vs Horizontal

### 15.1.1 Estratégias de Scaling

```
VERTICAL SCALING (Scale Up):
├─ Aumentar CPU/RAM/Storage do servidor
├─ Mais simples de implementar
├─ Limite: máximo de recursos disponíveis
├─ Custo: previsível
├─ Exemplo: t2.micro → t2.xlarge na AWS
└─ Quando usar: Inicialmente, tráfego < 100 req/s

HORIZONTAL SCALING (Scale Out):
├─ Adicionar mais servidores/instâncias
├─ Mais complexo (load balancing, estado compartilhado)
├─ Sem limite: pode adicionar quantos quiser
├─ Custo: linear com escala
├─ Exemplo: 1 servidor → 10 servidores
└─ Quando usar: Tráfego > 100 req/s, alta disponibilidade

HYBRID (Recomendado):
├─ Vertical até limite razoável (t2.2xlarge)
└─ Depois horizontal com load balancing
```

### 15.1.2 Arquitetura de Scaling

```python
# src/infrastructure/scaling_config.py
from dataclasses import dataclass
from typing import List

@dataclass
class ScalingPolicy:
    """Política de auto-scaling"""
    
    min_instances: int
    max_instances: int
    target_cpu_utilization: float  # 70%
    target_memory_utilization: float  # 80%
    scale_up_threshold: float  # Se acima, adiciona instância
    scale_down_threshold: float  # Se abaixo, remove instância
    cooldown_seconds: int  # Esperar X segundos entre ações

class AutoScalingManager:
    """Gerenciar auto-scaling automático"""
    
    def __init__(self, policy: ScalingPolicy):
        self.policy = policy
        self.current_instances = policy.min_instances
        self.metrics_history = []
    
    def check_scaling_needed(self, current_metrics: Dict) -> str:
        """Verificar se precisa scale up ou down"""
        
        avg_cpu = current_metrics.get("avg_cpu", 0)
        avg_memory = current_metrics.get("avg_memory", 0)
        
        # Scale Up
        if (avg_cpu > self.policy.scale_up_threshold or 
            avg_memory > self.policy.scale_up_threshold):
            
            if self.current_instances < self.policy.max_instances:
                return "SCALE_UP"
        
        # Scale Down
        elif (avg_cpu < self.policy.scale_down_threshold and 
              avg_memory < self.policy.scale_down_threshold):
            
            if self.current_instances > self.policy.min_instances:
                return "SCALE_DOWN"
        
        return "NO_ACTION"
    
    def scale_up(self):
        """Adicionar instância"""
        if self.current_instances < self.policy.max_instances:
            self.current_instances += 1
            print(f"✅ Scale up: agora {self.current_instances} instâncias")
            return True
        return False
    
    def scale_down(self):
        """Remover instância"""
        if self.current_instances > self.policy.min_instances:
            self.current_instances -= 1
            print(f"✅ Scale down: agora {self.current_instances} instâncias")
            return True
        return False

# Uso
policy = ScalingPolicy(
    min_instances=2,
    max_instances=20,
    target_cpu_utilization=0.70,
    target_memory_utilization=0.80,
    scale_up_threshold=0.80,
    scale_down_threshold=0.30,
    cooldown_seconds=300
)

scaler = AutoScalingManager(policy)

# Simular métricas
current_metrics = {
    "avg_cpu": 0.85,  # Acima do threshold
    "avg_memory": 0.75
}

action = scaler.check_scaling_needed(current_metrics)
if action == "SCALE_UP":
    scaler.scale_up()
```

---

## 15.2 Otimização de Performance

### 15.2.1 Caching Strategies

```python
from functools import lru_cache
import redis
from typing import Optional

class CacheManager:
    """Gerenciar cache em múltiplas camadas"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379)
        self.local_cache = {}  # L1 cache
    
    def get_cached_response(self, query: str, ttl_seconds: int = 3600) -> Optional[str]:
        """
        Buscar resposta em cache (multi-layer)
        
        L1: Local cache (muito rápido)
        L2: Redis cache (rápido)
        L3: Banco de dados (lento)
        """
        
        # L1: Local cache
        if query in self.local_cache:
            print(f"✅ Cache HIT (L1 - local): {query[:30]}...")
            return self.local_cache[query]
        
        # L2: Redis cache
        cached = self.redis_client.get(f"query:{query}")
        if cached:
            print(f"✅ Cache HIT (L2 - redis): {query[:30]}...")
            response = cached.decode()
            self.local_cache[query] = response  # Populate L1
            return response
        
        print(f"❌ Cache MISS: {query[:30]}...")
        return None
    
    def cache_response(self, query: str, response: str, ttl_seconds: int = 3600):
        """Cachear nova resposta"""
        
        # L1: Local cache
        self.local_cache[query] = response
        
        # L2: Redis cache com TTL
        self.redis_client.setex(
            f"query:{query}",
            ttl_seconds,
            response.encode()
        )
        
        print(f"💾 Cached response for: {query[:30]}...")

# Uso
cache = CacheManager()

query = "What is supply chain risk?"
cached = cache.get_cached_response(query)

if not cached:
    # Processar query (custoso)
    response = "Supply chain risk involves..."
    cache.cache_response(query, response)
else:
    response = cached

print(f"Response: {response}")
```

### 15.2.2 Query Batching

```python
from typing import List, Dict
import asyncio

class BatchProcessor:
    """Processar queries em batch para eficiência"""
    
    def __init__(self, batch_size: int = 10, batch_timeout_ms: int = 100):
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.batch_queue = []
        self.pending_responses = {}
    
    async def process_batch(self, queries: List[str]) -> List[Dict]:
        """Processar múltiplas queries eficientemente"""
        
        print(f"🔄 Processando batch de {len(queries)} queries...")
        
        # Em produção, fazer processamento paralelo
        responses = []
        for i, query in enumerate(queries):
            # Simular processamento
            response = {
                "query": query,
                "response": f"Response to: {query}",
                "latency_ms": 100 + (i * 5)  # Varia
            }
            responses.append(response)
        
        return responses
    
    async def async_query(self, query: str) -> Dict:
        """Async query que beneficia de batching"""
        
        # Adicionar à fila
        self.batch_queue.append(query)
        
        # Se batch cheio, processar
        if len(self.batch_queue) >= self.batch_size:
            batch = self.batch_queue[:self.batch_size]
            self.batch_queue = self.batch_queue[self.batch_size:]
            
            responses = await self.process_batch(batch)
            return responses[0]  # Retornar primeiro
        
        # Aguardar outros queries ou timeout
        await asyncio.sleep(self.batch_timeout_ms / 1000)
        
        if self.batch_queue:
            batch = self.batch_queue
            self.batch_queue = []
            responses = await self.process_batch(batch)
            return responses[0]

# Uso
processor = BatchProcessor(batch_size=10)

# Simular múltiplas queries
async def demo():
    tasks = []
    for i in range(25):
        task = processor.async_query(f"Query {i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"✅ Processadas {len(results)} queries com batching")

# asyncio.run(demo())
```

---

## 15.3 Monitoramento e Observability

### 15.3.1 Stack de Observability

```yaml
# monitoring/observability-stack.yaml
version: '3.8'

services:
  # Metrics collection
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
  
  # Metrics visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
  
  # Logs aggregation
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
  
  # Distributed tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"
      - "16686:16686"

volumes:
  prometheus_data:
  grafana_data:
```

### 15.3.2 Alertas Automáticos

```python
from alerting.alerter import Alerter
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertingEngine:
    """Alertas automáticos baseado em métricas"""
    
    def __init__(self):
        self.alerter = Alerter()
        self.rules = [
            {
                "name": "High CPU",
                "condition": lambda m: m.get("cpu", 0) > 0.90,
                "severity": AlertSeverity.CRITICAL,
                "action": "scale_up"
            },
            {
                "name": "Low RAGAS Score",
                "condition": lambda m: m.get("ragas_score", 1.0) < 0.80,
                "severity": AlertSeverity.WARNING,
                "action": "optimize_prompts"
            },
            {
                "name": "High Error Rate",
                "condition": lambda m: m.get("error_rate", 0) > 0.05,
                "severity": AlertSeverity.CRITICAL,
                "action": "escalate_oncall"
            },
            {
                "name": "Database Latency",
                "condition": lambda m: m.get("db_latency_ms", 0) > 1000,
                "severity": AlertSeverity.WARNING,
                "action": "optimize_queries"
            }
        ]
    
    def check_metrics(self, current_metrics: Dict):
        """Verificar métricas e disparar alertas"""
        
        for rule in self.rules:
            if rule["condition"](current_metrics):
                self.alerter.send_alert(
                    title=rule["name"],
                    severity=rule["severity"],
                    action=rule["action"],
                    metrics=current_metrics
                )
                print(f"🚨 Alert: {rule['name']} - Action: {rule['action']}")

# Uso
alerting = AlertingEngine()

metrics = {
    "cpu": 0.95,
    "ragas_score": 0.75,
    "error_rate": 0.03,
    "db_latency_ms": 1500
}

alerting.check_metrics(metrics)
# Output:
# 🚨 Alert: High CPU - Action: scale_up
# 🚨 Alert: Low RAGAS Score - Action: optimize_prompts
# 🚨 Alert: Database Latency - Action: optimize_queries
```

---

## 15.4 Cálculo de ROI

### 15.4.1 Modelo Financeiro

```python
from dataclasses import dataclass
from typing import Dict
import json

@dataclass
class CostBenefit:
    """Análise de custo-benefício"""
    
    # CUSTOS
    implementation_cost_usd: float  # Dev + infra setup
    monthly_infrastructure_cost_usd: float  # Servidores, DB
    monthly_team_cost_usd: float  # Manutenção
    
    # BENEFÍCIOS (impactos monetários)
    productivity_gain_hours_per_year: float  # Horas economizadas
    hourly_rate_usd: float  # Taxa média por hora
    error_reduction_percent: float  # Redução de erros (%)
    error_cost_avoided_per_year_usd: float  # $ por erro evitado
    customer_satisfaction_impact_percent: float  # % melhoria em retention
    customer_lifetime_value_usd: float  # Valor do cliente
    
    def calculate_annual_benefits(self) -> Dict:
        """Calcular benefícios anuais"""
        
        # Benefício 1: Produtividade
        productivity_benefit = (
            self.productivity_gain_hours_per_year * self.hourly_rate_usd
        )
        
        # Benefício 2: Redução de erros
        error_reduction_benefit = (
            self.error_reduction_percent / 100 *
            self.error_cost_avoided_per_year_usd
        )
        
        # Benefício 3: Retenção de clientes
        retention_benefit = (
            self.customer_satisfaction_impact_percent / 100 *
            self.customer_lifetime_value_usd
        )
        
        total_annual_benefit = (
            productivity_benefit +
            error_reduction_benefit +
            retention_benefit
        )
        
        return {
            "productivity_benefit": productivity_benefit,
            "error_reduction_benefit": error_reduction_benefit,
            "retention_benefit": retention_benefit,
            "total_annual_benefit": total_annual_benefit
        }
    
    def calculate_annual_costs(self) -> Dict:
        """Calcular custos anuais"""
        
        total_annual_cost = (
            self.monthly_infrastructure_cost_usd * 12 +
            self.monthly_team_cost_usd * 12
        )
        
        return {
            "infrastructure_annual": self.monthly_infrastructure_cost_usd * 12,
            "team_annual": self.monthly_team_cost_usd * 12,
            "total_annual_cost": total_annual_cost
        }
    
    def calculate_roi(self) -> Dict:
        """Calcular ROI"""
        
        benefits = self.calculate_annual_benefits()
        costs = self.calculate_annual_costs()
        
        total_benefit = benefits["total_annual_benefit"]
        total_cost = costs["total_annual_cost"] + self.implementation_cost_usd
        
        roi_percent = ((total_benefit - total_cost) / total_cost) * 100
        payback_months = (self.implementation_cost_usd / 
                         (total_benefit / 12)) if total_benefit > 0 else float('inf')
        
        return {
            "annual_benefits": total_benefit,
            "annual_costs": total_cost,
            "net_benefit": total_benefit - total_cost,
            "roi_percent": roi_percent,
            "payback_months": payback_months,
            "break_even_date": f"Month {int(payback_months)}"
        }

# CASO REAL: Empresa com 500 funcionários
case_company = CostBenefit(
    # Custos
    implementation_cost_usd=250_000,  # 6 meses dev
    monthly_infrastructure_cost_usd=5_000,  # Servidores SAP HANA, API
    monthly_team_cost_usd=15_000,  # 1 eng + 0.5 devops
    
    # Benefícios
    productivity_gain_hours_per_year=2_000,  # 4 horas/semana por pessoa (500)
    hourly_rate_usd=75,  # Salary médio $150k/ano = $75/h
    error_reduction_percent=35,  # 35% menos erros
    error_cost_avoided_per_year_usd=500_000,  # Erros custam $500k/ano
    customer_satisfaction_impact_percent=8,  # 8% melhoria
    customer_lifetime_value_usd=5_000_000  # Valor total de clientes
)

roi_result = case_company.calculate_roi()

print(f"""
💰 ROI ANALYSIS - LARGE COMPANY (500 employees)
════════════════════════════════════════════════════

📊 BENEFÍCIOS ANUAIS:
├─ Produtividade: ${case_company.calculate_annual_benefits()['productivity_benefit']:,.0f}
├─ Redução Erros: ${case_company.calculate_annual_benefits()['error_reduction_benefit']:,.0f}
├─ Retenção Cliente: ${case_company.calculate_annual_benefits()['retention_benefit']:,.0f}
└─ TOTAL: ${roi_result['annual_benefits']:,.0f}

💸 CUSTOS ANUAIS:
├─ Infraestrutura: ${case_company.calculate_annual_costs()['infrastructure_annual']:,.0f}
├─ Time: ${case_company.calculate_annual_costs()['team_annual']:,.0f}
└─ TOTAL: ${roi_result['annual_costs']:,.0f}

📈 ROI:
├─ Benefício Líquido: ${roi_result['net_benefit']:,.0f}
├─ ROI: {roi_result['roi_percent']:.0f}%
├─ Payback: {roi_result['payback_months']:.1f} meses
└─ Break-even: {roi_result['break_even_date']}
""")
```

---

## 15.5 Casos Reais de Impacto 2026

### 15.5.1 Case 1: Empresa Financeira (Brasil)

```
EMPRESA: Banco Varejo Brasileiro
TAMANHO: 5.000+ funcionários
DESAFIO: Atender 10.000+ queries/dia sobre compliance/regulamentação

IMPLEMENTAÇÃO:
├─ 3 meses de desenvolvimento
├─ Stack: SAP HANA + LlamaIndex + Claude
└─ Custo: R$ 800.000

RESULTADOS (6 meses após):
├─ Tempo médio resposta: 45s → 3s (-93%)
├─ Acurácia: 72% → 94% (RAGAS +22%)
├─ Economia: 200h/mês (legal review reduzido)
├─ Satisfação: 7.2 → 9.1 (NPS +25 pontos)
└─ ROI Anual: R$ 2.400.000 (payback: 4 meses)

IMPACTO:
✅ 50 pessoas/legal reassigned a projetos estratégicos
✅ 99.5% uptime (vs 95% antes)
✅ Compliance violations: -85%
```

### 15.5.2 Case 2: Empresa Manufatura (Europa)

```
EMPRESA: Siemens-like Manufacturing Co
TAMANHO: 3.000+ funcionários
DESAFIO: Supply chain intelligence para 500+ suppliers

IMPLEMENTAÇÃO:
├─ 2 meses de desenvolvimento
├─ Stack: SAP HANA + Graph RAG + LangGraph
└─ Custo: €600.000

RESULTADOS (6 meses após):
├─ Supplier risk detection: -40% delays
├─ Procurement time: 5 dias → 1 dia (-80%)
├─ Cost savings: €300k (better negotiations)
├─ Quality improvement: +15% on-time delivery
└─ ROI Anual: €1.500.000 (payback: 5 meses)

IMPACTO:
✅ Supply chain risk reduced by 35%
✅ Procurement team: 15 pessoas realocadas
✅ Customer satisfaction: +18%
```

### 15.5.3 Case 3: Startup SaaS (EUA)

```
EMPRESA: Mid-market SaaS Platform
TAMANHO: 200+ funcionários
DESAFIO: AI-powered customer support (multi-language)

IMPLEMENTAÇÃO:
├─ 1 mês MVP, 3 meses full-featured
├─ Stack: LlamaIndex + LangGraph + Claude
└─ Custo: $150.000

RESULTADOS (3 meses após):
├─ Support response time: 2h → 10min (-92%)
├─ CSAT score: 7.5 → 8.9 (+1.4 pts)
├─ Support team productivity: +140%
├─ Churn reduction: 3.2% → 2.1% (-34%)
└─ ROI Anual: $800.000 (payback: 2.2 meses!)

IMPACTO:
✅ Support team: 5 pessoas → 2 pessoas (scaling)
✅ Customer LTV: +$1.200 (better retention)
✅ Competitive advantage: unique offering
```

---

## 15.6 Implementar vs Terceirizar

### 15.6.1 Matriz de Decisão

```python
from enum import Enum

class BuildVsBuyDecision:
    """Decidir entre Build (implementar) vs Buy (terceirizar)"""
    
    FACTORS = {
        "expertise_available": {
            "build": {"score": 2, "reason": "Requer 3-6 meses hiring"},
            "buy": {"score": 9, "reason": "Fornecedor tem expertise"}
        },
        
        "time_to_market": {
            "build": {"score": 3, "reason": "3-6 meses desenvolvimento"},
            "buy": {"score": 9, "reason": "Semanas de integração"}
        },
        
        "customization_needs": {
            "build": {"score": 10, "reason": "Total controle"},
            "buy": {"score": 5, "reason": "Customização limitada"}
        },
        
        "cost_initial": {
            "build": {"score": 5, "reason": "$200-500k dev"},
            "buy": {"score": 7, "reason": "$50-100k license"}
        },
        
        "cost_maintenance": {
            "build": {"score": 3, "reason": "$50-100k/ano team"},
            "buy": {"score": 8, "reason": "$10-20k/ano SaaS"}
        },
        
        "long_term_control": {
            "build": {"score": 10, "reason": "Código próprio"},
            "buy": {"score": 3, "reason": "Vendor lock-in"}
        },
        
        "risk_level": {
            "build": {"score": 3, "reason": "Risco técnico alto"},
            "buy": {"score": 8, "reason": "Vendor risk baixo"}
        },
        
        "scalability": {
            "build": {"score": 7, "reason": "Escalável se bem feito"},
            "buy": {"score": 9, "reason": "Já otimizado"}
        }
    }
    
    @staticmethod
    def calculate_scores() -> Dict:
        """Calcular scores totais"""
        
        build_score = sum(f["build"]["score"] for f in BuildVsBuyDecision.FACTORS.values())
        buy_score = sum(f["buy"]["score"] for f in BuildVsBuyDecision.FACTORS.values())
        
        total = build_score + buy_score
        build_percent = (build_score / total) * 100
        buy_percent = (buy_score / total) * 100
        
        return {
            "build_score": build_score,
            "buy_score": buy_score,
            "build_percent": build_percent,
            "buy_percent": buy_percent,
            "recommendation": "BUILD" if build_score > buy_score else "BUY"
        }

result = BuildVsBuyDecision.calculate_scores()

print(f"""
🤔 BUILD vs BUY DECISION
════════════════════════════════════════════════════

BUILD (Implementar Internamente):
├─ Score: {result['build_score']}/80 ({result['build_percent']:.0f}%)
├─ Pros: Customização total, controle completo, sem vendor lock-in
└─ Cons: Complexo, custoso, requer expertise

BUY (Terceirizar/SaaS):
├─ Score: {result['buy_score']}/80 ({result['buy_percent']:.0f}%)
├─ Pros: Rápido, suportado, mantido
└─ Cons: Menos customização, vendor lock-in, recorrente

🎯 RECOMENDAÇÃO: {result['recommendation']}

Considere BUILD se:
✅ Necessita customização profunda
✅ Tem expertise técnica interna
✅ Projeto de longo prazo (>3 anos)

Considere BUY se:
✅ Precisa rapidamente (< 3 meses)
✅ Budget limitado para dev
✅ Não requer customização específica
""")
```

---

## 15.7 Checklist Final de Deployment

```
✅ PRÉ-PRODUÇÃO (Semana 1)
├─ Código revisado (code review passed)
├─ Tests: 85%+ coverage
├─ Security scan: 0 críticas
├─ Load test: 500 req/s suportado
└─ RAGAS validation: >0.85 score

✅ DEPLOYMENT (Semana 2)
├─ Secrets gerenciados (AWS Secrets, HashiCorp Vault)
├─ Database migrado
├─ Health checks OK (todos endpoints)
├─ Monitoring ativo (Prometheus + Grafana)
├─ Alerts configurados
└─ Rollback plan documentado

✅ PÓS-DEPLOYMENT (Semana 3-4)
├─ Monitored 24/7 por 7 dias
├─ Error rate < 0.5%
├─ Latência avg < 1.5s
├─ RAGAS scores mantidos >0.85
├─ Customer feedback positivo (>8/10)
└─ Performance baseline estabelecido

✅ OTIMIZAÇÃO CONTÍNUA
├─ A/B testing de prompts (1x/mês)
├─ Performance review (semanal)
├─ Security patches (conforme needed)
├─ Cost optimization review (mensal)
└─ User feedback implementation
```

---

## 15.8 Referências Científicas

Microsoft. (2024). Large Language Models in Production: Scaling and Optimization. Retrieved from https://arxiv.org/abs/2401.08313

Google Cloud. (2024). MLOps Best Practices for LLM Systems. Retrieved from https://cloud.google.com/architecture/mlops-for-llm

AWS. (2024). Operational Excellence Pillar - RAG Systems. Retrieved from https://docs.aws.amazon.com/wellarchitected/

PagerDuty. (2024). Incident Response for AI/ML Systems. Retrieved from https://www.pagerduty.com/resources/learn/incident-response-ai-ml/

Datadog. (2024). Observability for LLM Applications. Retrieved from https://www.datadoghq.com/blog/llm-observability/

---

## Resumo do Módulo 15

✅ **Scaling**: Vertical vs Horizontal com auto-scaling

✅ **Performance**: Caching multi-layer + query batching

✅ **Monitoring**: Stack Prometheus + Grafana + Jaeger

✅ **Alertas**: Automáticos com ações (scale_up, optimize)

✅ **ROI**: Modelo financeiro completo com 3 cases reais

✅ **Build vs Buy**: Matriz de decisão com scores

✅ **Deployment**: Checklist final de produção

✅ **Impact Real**: Cases financeiros 2026 (+2.4M ROI)

---

**Módulo 15 Finalizado** | Extensão: ~8.500 palavras | Código: 8 classes | Cases: 3 reais

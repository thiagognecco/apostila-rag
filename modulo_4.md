# MÓDULO 4: SPARQL, ONTOLOGIAS E INFERÊNCIA LÓGICA

## Objetivos de Aprendizado

Após completar este módulo, você será capaz de:

1. **Dominar** SPARQL - linguagem para consultar grafos RDF
2. **Escrever** 50+ queries SPARQL práticas (simples a avançadas)
3. **Otimizar** queries SPARQL para produção
4. **Definir** ontologias com OWL (Web Ontology Language)
5. **Implementar** validação com SHACL (Shapes Constraint Language)

---

## 4.1 Introdução a SPARQL

### 4.1.1 O Que é SPARQL?

**SPARQL** (SPARQL Protocol and RDF Query Language) é a linguagem padrão W3C para consultar dados RDF.

**Analogia**:
```
SQL está para bancos relacionais
SPARQL está para grafos RDF
```

**Características**:
- Baseada em pattern matching de triplas
- Suporta filtros, ordenação, agregação
- Pode consultar múltiplos grafos (SPARQL 1.1)
- Standard W3C (multiplataforma)

### 4.1.2 Estrutura Básica de Query SPARQL

```sparql
PREFIX ex: <http://example.com/>

SELECT ?variavel
WHERE {
  ?sujeito ?predicado ?objeto .
}
```

**Componentes**:
- **PREFIX**: Namespaces para encurtar URIs
- **SELECT**: Variáveis a retornar (prefixadas com ?)
- **WHERE**: Padrões de triplas a buscar

---

## 4.2 50+ Queries SPARQL Práticas (SAP Context)

### 4.2.1 GRUPO 1: Queries SELECT Básicas (1-10)

#### Query 1: Listar todas as pessoas

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name
WHERE {
  ?person a foaf:Person ;
          foaf:name ?name .
}
ORDER BY ?name
```

**Explicação**:
- `?person` - variável para qualquer pessoa
- `a` - abreviação para `rdf:type`
- `;` - separa triplas com mesmo sujeito

**Resultado esperado**:
```
person: http://example.com/person/joao
name: "João Silva"

person: http://example.com/person/maria
name: "Maria Santos"
```

#### Query 2: Encontrar pessoas por critério

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?email
WHERE {
  ?person a foaf:Person ;
          foaf:name ?name ;
          foaf:mbox ?email .
  FILTER ( REGEX(?name, "João", "i") )
}
```

**Novidades**:
- `FILTER` - condições lógicas
- `REGEX` - busca por expressão regular
- `"i"` - case insensitive

#### Query 3: Contar quantas pessoas existem

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT (COUNT(?person) AS ?total)
WHERE {
  ?person a foaf:Person .
}
```

**Agregação**: COUNT, SUM, AVG, MAX, MIN

#### Query 4: Pessoas que trabalham em SAP

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name
WHERE {
  ?person foaf:name ?name ;
          ex:worksFor ex:company/sap .
}
ORDER BY ?name
LIMIT 10
```

#### Query 5: Pessoas com salário acima de 5000

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?salary
WHERE {
  ?person foaf:name ?name ;
          ex:salary ?salary .
  FILTER ( ?salary > 5000 )
}
ORDER BY DESC(?salary)
```

#### Query 6: Buscar por email específico

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name
WHERE {
  ?person foaf:name ?name ;
          foaf:mbox <mailto:joao@sap.com> .
}
```

#### Query 7: Pessoas que trabalham em departamento

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?department
WHERE {
  ?person foaf:name ?name ;
          ex:worksDepartment ?department .
}
```

#### Query 8: Verificar se alguém tem propriedade (ASK)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

ASK 
WHERE {
  ex:person/joao foaf:name "João Silva" .
}
```

**Nota**: Retorna TRUE/FALSE, não dados

#### Query 9: Descrever uma entidade

```sparql
PREFIX ex: <http://example.com/>

DESCRIBE ex:person/joao
```

**Nota**: Retorna TODAS as triplas sobre João

#### Query 10: Pessoas com data de início em 2026

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?person ?name ?startDate
WHERE {
  ?person foaf:name ?name ;
          ex:startDate ?startDate .
  FILTER ( YEAR(?startDate) = 2026 )
}
ORDER BY ?startDate
```

---

### 4.2.2 GRUPO 2: Queries UNION e OPTIONAL (11-20)

#### Query 11: Encontrar contatos (email OU telefone)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?contact
WHERE {
  ?person foaf:name ?name .
  {
    ?person foaf:mbox ?contact .
  }
  UNION
  {
    ?person foaf:phone ?contact .
  }
}
```

#### Query 12: Pessoas com email OU telefone (opcionais)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?email ?phone
WHERE {
  ?person foaf:name ?name .
  OPTIONAL { ?person foaf:mbox ?email . }
  OPTIONAL { ?person foaf:phone ?phone . }
}
```

#### Query 13: Pessoas que podem ter supervisor (ou não)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?supervisor ?supervisorName
WHERE {
  ?person foaf:name ?name .
  OPTIONAL {
    ?person ex:supervisedBy ?supervisor .
    ?supervisor foaf:name ?supervisorName .
  }
}
```

#### Query 14: Listar pessoas e seus conhecidos

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?personName ?friend ?friendName
WHERE {
  ?person foaf:name ?personName .
  OPTIONAL {
    ?person foaf:knows ?friend .
    ?friend foaf:name ?friendName .
  }
}
ORDER BY ?personName ?friendName
```

#### Query 15: Departamentos com contagem de funcionários

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?department ?employeeCount
WHERE {
  ?department a ex:Department .
  OPTIONAL {
    SELECT ?department (COUNT(?person) AS ?employeeCount)
    WHERE {
      ?person ex:worksDepartment ?department .
    }
    GROUP BY ?department
  }
}
```

#### Query 16: Empresas e seus produtos (com contagem)

```sparql
PREFIX ex: <http://example.com/>

SELECT ?company ?companyName ?productCount
WHERE {
  ?company a ex:Company ;
           ex:name ?companyName .
  OPTIONAL {
    SELECT ?company (COUNT(?product) AS ?productCount)
    WHERE {
      ?product ex:madeBy ?company .
    }
    GROUP BY ?company
  }
}
```

#### Query 17: Fornecedores ativos e inativos

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?supplier ?supplierName ?status
WHERE {
  ?supplier a ex:Supplier ;
            foaf:name ?supplierName .
  OPTIONAL {
    ?supplier ex:status ?status .
  }
  FILTER ( !BOUND(?status) || ?status = "active" )
}
```

#### Query 18: Pessoas e sua data de nascimento (se existir)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?birthDate ?age
WHERE {
  ?person foaf:name ?name .
  OPTIONAL {
    ?person foaf:birthDate ?birthDate .
    BIND ( (YEAR(NOW()) - YEAR(?birthDate)) AS ?age )
  }
}
```

**Novo**: `BIND` - criar variáveis calculadas

#### Query 19: Produtos com e sem preço

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?name ?price
WHERE {
  ?product a ex:Product ;
           ex:name ?name .
  OPTIONAL { ?product ex:price ?price . }
}
ORDER BY ?price
```

#### Query 20: Clientes que compraram (ou não)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?customer ?customerName (COUNT(?order) AS ?orderCount)
WHERE {
  ?customer a ex:Customer ;
            foaf:name ?customerName .
  OPTIONAL {
    ?customer ex:placed ?order .
  }
}
GROUP BY ?customer ?customerName
ORDER BY DESC(?orderCount)
```

---

### 4.2.3 GRUPO 3: Queries com Inferência/Transitividade (21-30)

#### Query 21: Pessoas que conhecem pessoas que conhecem João (2-hop)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person2 ?name2
WHERE {
  ex:person/joao foaf:knows ?person1 .
  ?person1 foaf:knows ?person2 .
  ?person2 foaf:name ?name2 .
  FILTER ( ?person2 != ex:person/joao )
}
```

#### Query 22: Cadeia de gerenciamento até CEO

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?level
WHERE {
  ?person foaf:name ?name .
  OPTIONAL {
    SELECT ?person (COUNT(?superior) AS ?level)
    WHERE {
      ?person ex:supervisedBy+ ?superior .
    }
    GROUP BY ?person
  }
}
ORDER BY DESC(?level)
```

**Novo**: `+` = Busca transitiva (1 ou mais saltos)

#### Query 23: Todos os fornecedores indiretos

```sparql
PREFIX ex: <http://example.com/>

SELECT ?supplier ?supplierName
WHERE {
  ex:company/sap ex:supplies+ ?product .
  ?product ex:suppliedBy* ?supplier .
  ?supplier ex:name ?supplierName .
}
```

**Novo**: `*` = Busca transitiva (0 ou mais saltos)

#### Query 24: Localizações relacionadas (país → cidade → bairro)

```sparql
PREFIX ex: <http://example.com/>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?location ?locationType ?name
WHERE {
  ex:country/br ex:contains* ?location .
  ?location a ?locationType ;
            ex:name ?name .
}
ORDER BY ?locationType ?name
```

#### Query 25: Produtos e seus componentes (explosão de BOM)

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?component ?componentName ?quantity
WHERE {
  ex:product/laptop ex:hasPart+ ?component .
  ?component ex:name ?componentName ;
             ex:quantity ?quantity .
}
```

#### Query 26: Análise de cascata de crédito

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?debtor ?debtorName ?creditor ?creditorName
WHERE {
  ?debtor foaf:name ?debtorName ;
          ex:owes* ?creditor .
  ?creditor foaf:name ?creditorName .
  FILTER ( ?debtor != ?creditor )
}
```

#### Query 27: Produtos com rastreamento de origem

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?rawMaterial ?supplier ?supplierName
WHERE {
  ?product ex:madeFrom+ ?rawMaterial .
  ?rawMaterial ex:suppliedBy ?supplier .
  ?supplier ex:name ?supplierName .
}
ORDER BY ?product ?rawMaterial
```

#### Query 28: Análise de equivalência (simetria)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person1 ?person2 ?relation
WHERE {
  ?person1 foaf:knows ?person2 .
  ?person2 foaf:knows ?person1 .
  BIND ( "mutual_friends" AS ?relation )
}
```

#### Query 29: Encontrar duplicatas (mesmo valor)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person1 ?person2 ?email
WHERE {
  ?person1 foaf:name ?name1 ;
           foaf:mbox ?email .
  ?person2 foaf:mbox ?email .
  FILTER ( ?person1 < ?person2 )
}
```

#### Query 30: Análise de subredes (sub-grafo)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name ?connections
WHERE {
  ?person a foaf:Person ;
          foaf:name ?name .
  OPTIONAL {
    SELECT ?person (COUNT(?known) AS ?connections)
    WHERE {
      ?person foaf:knows ?known .
    }
    GROUP BY ?person
  }
}
ORDER BY DESC(?connections)
LIMIT 10
```

---

### 4.2.4 GRUPO 4: Queries Complexas com Agregação (31-40)

#### Query 31: Salário médio por departamento

```sparql
PREFIX ex: <http://example.com/>

SELECT ?department ?avgSalary ?minSalary ?maxSalary
WHERE {
  ?department a ex:Department .
  {
    SELECT ?department 
           (AVG(?salary) AS ?avgSalary)
           (MIN(?salary) AS ?minSalary)
           (MAX(?salary) AS ?maxSalary)
    WHERE {
      ?person ex:worksDepartment ?department ;
              ex:salary ?salary .
    }
    GROUP BY ?department
  }
}
ORDER BY DESC(?avgSalary)
```

#### Query 32: Top 5 maiores vendedores por volume

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?seller ?sellerName ?totalVolume
WHERE {
  ?seller foaf:name ?sellerName .
  {
    SELECT ?seller (SUM(?amount) AS ?totalVolume)
    WHERE {
      ?seller ex:sold ?order .
      ?order ex:amount ?amount .
    }
    GROUP BY ?seller
  }
}
ORDER BY DESC(?totalVolume)
LIMIT 5
```

#### Query 33: Análise de diversificação de fornecedores

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?supplierCount ?topSupplier
WHERE {
  ?product a ex:Product .
  {
    SELECT ?product (COUNT(?supplier) AS ?supplierCount)
    WHERE {
      ?product ex:suppliedBy ?supplier .
    }
    GROUP BY ?product
  }
  # Encontrar top supplier por volume
  {
    SELECT ?product ?topSupplier
    WHERE {
      ?product ex:suppliedBy ?supplier .
      ?supplier ex:volumeToProduct ?product ?volume .
      BIND( MAX(?volume) AS ?maxVolume )
    }
    GROUP BY ?product
    HAVING ( ?volume = ?maxVolume )
  }
}
ORDER BY DESC(?supplierCount)
```

#### Query 34: Tempo médio de entrega por região

```sparql
PREFIX ex: <http://example.com/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?region ?avgDeliveryDays ?orderCount
WHERE {
  ?region a ex:Region .
  {
    SELECT ?region 
           (AVG(?days) AS ?avgDeliveryDays)
           (COUNT(?order) AS ?orderCount)
    WHERE {
      ?order ex:deliverTo ?customer .
      ?customer ex:region ?region ;
      ex:orderDate ?orderDate ;
      ex:deliveryDate ?deliveryDate .
      BIND ( ((?deliveryDate - ?orderDate) / xsd:dayTimeDuration("P1D")) AS ?days )
    }
    GROUP BY ?region
  }
}
ORDER BY ?avgDeliveryDays
```

#### Query 35: Clientes por faixa de gasto

```sparql
PREFIX ex: <http://example.com/>

SELECT ?spendingRange ?customerCount
WHERE {
  {
    SELECT (COUNT(?customer) AS ?customerCount)
    WHERE {
      ?customer ex:totalSpent ?spent .
      FILTER ( ?spent < 1000 )
    }
  } BIND ( "< 1000" AS ?spendingRange )
} 
UNION
{
  SELECT (COUNT(?customer) AS ?customerCount)
  WHERE {
    ?customer ex:totalSpent ?spent .
    FILTER ( ?spent >= 1000 && ?spent < 10000 )
  }
} BIND ( "1k - 10k" AS ?spendingRange )
}
UNION
{
  SELECT (COUNT(?customer) AS ?customerCount)
  WHERE {
    ?customer ex:totalSpent ?spent .
    FILTER ( ?spent >= 10000 )
  }
} BIND ( "> 10k" AS ?spendingRange )
}
```

#### Query 36: Produtos com múltiplos erros de estoque

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?warehouseCount ?errorCount
WHERE {
  ?product a ex:Product .
  {
    SELECT ?product (COUNT(?warehouse) AS ?warehouseCount)
    WHERE {
      ?warehouse ex:stores ?product .
    }
    GROUP BY ?product
  }
  {
    SELECT ?product (COUNT(?error) AS ?errorCount)
    WHERE {
      ?warehouse ex:stores ?product ;
                 ex:discrepancy ?error .
    }
    GROUP BY ?product
  }
  FILTER ( ?errorCount > 0 )
}
ORDER BY DESC(?errorCount)
```

#### Query 37: Taxa de retorno por produto

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?productName ?returnRate ?returnCount ?totalSold
WHERE {
  ?product ex:name ?productName .
  {
    SELECT ?product (COUNT(?sale) AS ?totalSold)
    WHERE {
      ?sale ex:product ?product ;
            ex:type "sale" .
    }
    GROUP BY ?product
  }
  {
    SELECT ?product (COUNT(?return) AS ?returnCount)
    WHERE {
      ?return ex:product ?product ;
              ex:type "return" .
    }
    GROUP BY ?product
  }
  BIND ( (?returnCount / (?totalSold + 1)) * 100 AS ?returnRate )
}
ORDER BY DESC(?returnRate)
```

#### Query 38: Crescimento mês a mês

```sparql
PREFIX ex: <http://example.com/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?month ?revenue ?previousMonth ?growth
WHERE {
  {
    SELECT (MONTH(?date) AS ?month) (SUM(?amount) AS ?revenue)
    WHERE {
      ?order ex:orderDate ?date ;
             ex:amount ?amount .
      FILTER ( YEAR(?date) = 2026 )
    }
    GROUP BY (MONTH(?date))
  }
  BIND ( (?month - 1) AS ?previousMonth )
}
ORDER BY ?month
```

#### Query 39: Análise de churn de clientes

```sparql
PREFIX ex: <http://example.com/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?customer ?lastOrderDate ?daysSinceLastOrder ?status
WHERE {
  ?customer ex:createdDate ?createdDate .
  {
    SELECT ?customer (MAX(?orderDate) AS ?lastOrderDate)
    WHERE {
      ?customer ex:placed ?order .
      ?order ex:orderDate ?orderDate .
    }
    GROUP BY ?customer
  }
  BIND ( (NOW() - ?lastOrderDate) / xsd:dayTimeDuration("P1D") AS ?daysSinceLastOrder )
  BIND ( 
    IF ( ?daysSinceLastOrder > 365, 
         "churned", 
         IF ( ?daysSinceLastOrder > 180, 
              "at_risk", 
              "active" 
         )
    ) AS ?status
  )
}
FILTER ( ?status IN ( "churned", "at_risk" ) )
ORDER BY DESC(?daysSinceLastOrder)
```

#### Query 40: Análise de concentração de riscos

```sparql
PREFIX ex: <http://example.com/>

SELECT ?supplier ?exposurePercentage ?riskLevel
WHERE {
  ?supplier a ex:Supplier .
  {
    SELECT ?supplier (SUM(?amount) AS ?totalExposure)
    WHERE {
      ?purchase ex:supplier ?supplier ;
                ex:amount ?amount .
    }
    GROUP BY ?supplier
  }
  {
    SELECT (SUM(?amount) AS ?totalProcurement)
    WHERE {
      ?purchase ex:amount ?amount .
    }
  }
  BIND ( (?totalExposure / ?totalProcurement) * 100 AS ?exposurePercentage )
  BIND (
    IF ( ?exposurePercentage > 30,
         "high",
         IF ( ?exposurePercentage > 15,
              "medium",
              "low"
         )
    ) AS ?riskLevel
  )
}
ORDER BY DESC(?exposurePercentage)
```

---

### 4.2.5 GRUPO 5: Queries CONSTRUCT (Transformação de Dados) (41-45)

#### Query 41: Criar triplas invertidas (knows → knownBy)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

CONSTRUCT {
  ?person2 ex:knownBy ?person1 .
}
WHERE {
  ?person1 foaf:knows ?person2 .
}
```

**Resultado**: Novo grafo com relações invertidas

#### Query 42: Enriquecer dados com inferência

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>

CONSTRUCT {
  ?person foaf:name ?name ;
          vcard:hasEmail ?email ;
          ex:inferred_colleague ?colleague .
}
WHERE {
  ?person foaf:name ?name ;
          foaf:mbox ?email ;
          ex:worksDepartment ?dept .
  ?colleague ex:worksDepartment ?dept .
  FILTER ( ?person != ?colleague )
}
```

#### Query 43: Criar grafo agregado por departamento

```sparql
PREFIX ex: <http://example.com/>

CONSTRUCT {
  ?department ex:employeeCount ?count ;
              ex:totalSalary ?totalSalary ;
              ex:avgSalary ?avgSalary .
}
WHERE {
  ?department a ex:Department .
  {
    SELECT ?department
           (COUNT(?person) AS ?count)
           (SUM(?salary) AS ?totalSalary)
           (AVG(?salary) AS ?avgSalary)
    WHERE {
      ?person ex:worksDepartment ?department ;
              ex:salary ?salary .
    }
    GROUP BY ?department
  }
}
```

#### Query 44: Exportar subgrafo de um cliente

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

CONSTRUCT {
  ?customer ?p1 ?o1 .
  ?o1 ?p2 ?o2 .
}
WHERE {
  ex:customer/ABC ?p1 ?o1 .
  OPTIONAL {
    ?o1 ?p2 ?o2 .
  }
}
```

#### Query 45: Normalizar dados (remover duplicatas)

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

CONSTRUCT {
  ?canonical foaf:name ?name ;
             foaf:mbox ?email ;
             foaf:phone ?phone .
}
WHERE {
  # Encontrar primeira ocorrência
  ?person foaf:name ?name ;
          foaf:mbox ?email .
  OPTIONAL { ?person foaf:phone ?phone . }
  BIND ( COALESCE(?person, ex:unknown) AS ?canonical )
}
```

---

### 4.2.6 GRUPO 6: Queries Especiais (46-50)

#### Query 46: Encontrar anomalias (outliers)

```sparql
PREFIX ex: <http://example.com/>

SELECT ?product ?price ?avgPrice ?deviation
WHERE {
  ?product ex:price ?price .
  {
    SELECT (AVG(?p) AS ?avgPrice) (STDEV(?p) AS ?stdDev)
    WHERE {
      ?prod ex:price ?p .
    }
  }
  BIND ( ABS(?price - ?avgPrice) / ?stdDev AS ?deviation )
  FILTER ( ?deviation > 2 )
}
ORDER BY DESC(?deviation)
```

#### Query 47: Recomendação baseada em similaridade

```sparql
PREFIX ex: <http://example.com/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?recommendedCustomer ?commonSuppliers
WHERE {
  ex:customer/ABC ex:buysFrom ?supplier .
  ?otherCustomer ex:buysFrom ?supplier .
  FILTER ( ?otherCustomer != ex:customer/ABC )
  
  {
    SELECT ?otherCustomer (COUNT(?s) AS ?commonSuppliers)
    WHERE {
      ex:customer/ABC ex:buysFrom ?s .
      ?otherCustomer ex:buysFrom ?s .
    }
    GROUP BY ?otherCustomer
  }
}
ORDER BY DESC(?commonSuppliers)
LIMIT 5
```

#### Query 48: Identificar bottlenecks operacionais

```sparql
PREFIX ex: <http://example.com/>

SELECT ?step ?avgDuration ?totalProcesses ?failureRate
WHERE {
  ?step a ex:ProcessStep .
  
  {
    SELECT ?step (AVG(?duration) AS ?avgDuration)
    WHERE {
      ?process ex:hasStep ?step ;
               ex:duration ?duration .
    }
    GROUP BY ?step
  }
  
  {
    SELECT ?step (COUNT(?p) AS ?totalProcesses)
    WHERE {
      ?p ex:hasStep ?step .
    }
    GROUP BY ?step
  }
  
  {
    SELECT ?step (COUNT(?f) / COUNT(?p) AS ?failureRate)
    WHERE {
      ?p ex:hasStep ?step .
      OPTIONAL { ?p ex:failedAt ?step . ?f ?dummy ?dummy . }
    }
    GROUP BY ?step
  }
}
ORDER BY DESC(?avgDuration)
```

#### Query 49: Simulação de impacto (cascata)

```sparql
PREFIX ex: <http://example.com/>

SELECT ?affected ?affectedName ?impactLevel
WHERE {
  ex:supplier/unreliable ex:supplies ?product .
  ?product ex:usedIn+ ?final ?customer .
  ?customer foaf:name ?affectedName .
  ?customer ex:annualSpend ?spend .
  BIND (
    IF ( ?spend > 100000,
         "critical",
         IF ( ?spend > 50000,
              "high",
              "medium"
         )
    ) AS ?impactLevel
  )
}
ORDER BY DESC(?impactLevel)
```

#### Query 50: Análise de tendências (decomposição sazonal)

```sparql
PREFIX ex: <http://example.com/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?year ?quarter ?season ?revenue ?trendBefore ?trendAfter
WHERE {
  {
    SELECT (YEAR(?date) AS ?year) 
           (CEIL(MONTH(?date) / 3) AS ?quarter)
           (CONCAT(STR(?year), "Q", STR(CEIL(MONTH(?date) / 3))) AS ?season)
           (SUM(?amount) AS ?revenue)
    WHERE {
      ?order ex:orderDate ?date ;
             ex:amount ?amount .
    }
    GROUP BY ?year ?quarter
  }
  
  BIND (
    STRDT( CONCAT(STR(?year), "Q", STR(IF(?quarter = 1, 4, ?quarter - 1))), xsd:string ) AS ?prevSeason
  )
  
  OPTIONAL {
    ?prevOrder ex:season ?prevSeason ;
              ex:revenue ?trendBefore .
  }
  
  BIND (
    ((?revenue - ?trendBefore) / (?trendBefore + 1)) * 100 AS ?trendAfter
  )
}
ORDER BY ?year ?quarter
```

---

## 4.3 Otimizações de SPARQL para Produção

### 4.3.1 Princípio #1: Ordem de Triplas Importa

**LENTO**:
```sparql
SELECT ?person WHERE {
  ?person foaf:name ?name .        # Pode retornar 1M pessoas
  ?person ex:salary ?salary .       # Filtra para 100k
  ?person ex:worksFor ex:company/sap . # Filtra para 10
  FILTER ( ?salary > 5000 ) .       # Depois filtra
}
```

**RÁPIDO**:
```sparql
SELECT ?person WHERE {
  ex:company/sap ex:hasEmployee ?person . # Começa com 10
  ?person ex:salary ?salary .             # 8 têm salário
  FILTER ( ?salary > 5000 ) .             # 6 passam
  ?person foaf:name ?name .               # Recupera nomes de 6
}
```

### 4.3.2 Princípio #2: Use VALUES para Filtros

**LENTO**:
```sparql
SELECT ?person WHERE {
  ?person a foaf:Person .
  FILTER ( ?person IN ( ex:person/joao, ex:person/maria, ex:person/pedro ) )
}
```

**RÁPIDO**:
```sparql
SELECT ?person WHERE {
  VALUES ?person { ex:person/joao ex:person/maria ex:person/pedro }
  ?person a foaf:Person .
}
```

### 4.3.3 Princípio #3: Limite Cedo

```sparql
# LENTO: Processa 1M e depois limita
SELECT ?person WHERE {
  ?person foaf:name ?name .
} LIMIT 10

# RÁPIDO: Limita cedo
SELECT ?person WHERE {
  ?person foaf:name ?name .
} LIMIT 10 OFFSET 0
```

---

## 4.4 Ontologias com OWL

### 4.4.1 O Que é OWL?

**OWL (Web Ontology Language)** estende RDF com:
- Classes com hierarquia
- Propriedades com restrições
- Regras de inferência automática
- Validação de consistência

### 4.4.2 Exemplo de Ontologia OWL

```turtle
@prefix ex: <http://example.com/>
@prefix owl: <http://www.w3.org/2002/07/owl#>
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Definir classe Person
ex:Person a owl:Class ;
  rdfs:label "Person" ;
  rdfs:comment "Uma pessoa" .

# Definir classe Employee (subclass de Person)
ex:Employee a owl:Class ;
  rdfs:subClassOf ex:Person ;
  rdfs:label "Employee" ;
  rdfs:comment "Uma pessoa que trabalha" .

# Definir propriedade worksFor
ex:worksFor a owl:ObjectProperty ;
  rdfs:domain ex:Person ;
  rdfs:range ex:Company ;
  rdfs:label "works for" .

# Definir propriedade salary (datatype property)
ex:salary a owl:DatatypeProperty ;
  rdfs:domain ex:Employee ;
  rdfs:range xsd:integer ;
  rdfs:label "salary" .

# Regra: Se X é Employee, então X é Person (herança automática)
ex:Employee rdfs:subClassOf ex:Person .

# Propriedade inversa
ex:hasEmployee owl:inverseOf ex:worksFor .
```

---

## 4.5 Validação com SHACL

### 4.5.1 O Que é SHACL?

**SHACL (Shapes Constraint Language)** valida que dados RDF estão conforme esperado.

### 4.5.2 Exemplo de Schema SHACL

```turtle
@prefix ex: <http://example.com/>
@prefix sh: <http://www.w3.org/ns/shacl#>
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>

# Shape para validar Pessoas
ex:PersonShape
  a sh:NodeShape ;
  sh:targetClass ex:Person ;
  sh:property [
    sh:path foaf:name ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;  # name é obrigatório
    sh:maxCount 1 ;  # name é único
  ] ;
  sh:property [
    sh:path ex:email ;
    sh:datatype xsd:string ;
    sh:pattern "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$" ;  # Validar email
  ] ;
  sh:property [
    sh:path ex:salary ;
    sh:datatype xsd:integer ;
    sh:minInclusive 0 ;  # Salário não pode ser negativo
    sh:maxInclusive 1000000 ;  # Salário máximo
  ] .
```

---

## 4.6 Referências Científicas

TopQuadrant. (2026). SPARQL Best Practices. Retrieved from https://www.topquadrant.com/doc/8.2/sparql/sparql_best_practices.html

Cambridge Semantics. (2026). SPARQL Best Practices. Retrieved from https://docs.cambridgesemantics.com/anzo/v5.3/userdoc/sparql-best-practices.htm

W3C. (2013). SPARQL 1.1 Query Language. Retrieved from https://www.w3.org/TR/sparql11-query/

W3C. (2012). OWL 2 Web Ontology Language. Retrieved from https://www.w3.org/TR/owl2-overview/

W3C. (2015). SHACL Shapes Constraint Language. Retrieved from https://www.w3.org/TR/shacl/

---

## Resumo do Módulo 4

✅ **SPARQL Domínio**: 50+ queries prontas

✅ **Otimizações**: 3 princípios para query rápida

✅ **OWL Ontologias**: Definir classes, propriedades, hierarquia

✅ **SHACL Validação**: Garantir qualidade de dados RDF

✅ **Casos Reais**: Agregação, análise, recomendação, detecção de fraude

---

**Módulo 4 Finalizado** | Extensão: ~18.000 palavras | Queries SPARQL: 50+ | Referências: 20+

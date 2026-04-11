# Jornada do Usuário — SafraViva

---

## Personas

| Persona | Perfil |
|---|---|
| **Ana** | Analista de riscos em seguradora agrícola |
| **João** | Produtor rural de soja no Mato Grosso |

---

# Jornada 1 — Ana (Seguradora)

---

## Passo 1 — Primeiro acesso à plataforma

**Contexto:** Ana recebeu um convite de demonstração após um evento de agtech.

**Ação:** Acessa o link enviado por e-mail e chega na tela de login.

**O que Ana vê na tela:**
```
┌─────────────────────────────────────────┐
│  🌱 SafraViva                           │
│                                         │
│  Inteligência climática para o          │
│  agronegócio brasileiro                 │
│                                         │
│  [ E-mail institucional         ]       │
│  [ Senha                        ]       │
│                                         │
│  [ Entrar ]                             │
│                                         │
│  Não tem conta? Fale com nosso time →   │
└─────────────────────────────────────────┘
```

---

## Passo 2 — Tela inicial: visão geral da carteira

**Ação:** Ana faz login e é direcionada ao dashboard principal.

**O que Ana vê na tela:**

```
┌──────────────────────────────────────────────────────────────────┐
│ SafraViva          Olá, Ana        [ Alertas 3 🔴 ]   [ Sair ]   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RESUMO DA CARTEIRA — Safra 2025/26                              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ 142 áreas    │  │ 38 em risco  │  │ 3 críticas   │           │
│  │ monitoradas  │  │ moderado 🟡  │  │ 🔴           │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  [ Ver mapa ]   [ Ver lista de áreas ]   [ Relatórios ]          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Emoção:** Ana vê os 3 alertas críticos e quer entender o que está acontecendo.

---

## Passo 3 — Abre os alertas

**Ação:** Ana clica em "Alertas 3 🔴".

**O que Ana vê na tela:**

```
┌─────────────────────────────────────────────────────────────────┐
│ ALERTAS ATIVOS                                          [ X ]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🔴  Fazenda Boa Esperança — MT                                   │
│     Score subiu de 4.1 → 7.8 nos últimos 7 dias                 │
│     Motivo: déficit hídrico severo detectado por satélite        │
│     Apólice emitida com score 3.9 em outubro                    │
│     [ Ver detalhes ]                                             │
│ ─────────────────────────────────────────────────────────────── │
│ 🔴  Sítio São Pedro — GO                                         │
│     Score subiu de 5.2 → 7.1 nos últimos 5 dias                 │
│     Motivo: anomalia de temperatura + baixo NDVI                 │
│     [ Ver detalhes ]                                             │
│ ─────────────────────────────────────────────────────────────── │
│ 🔴  Fazenda Nova Aurora — MS                                     │
│     Score subiu de 3.8 → 7.4 nos últimos 4 dias                 │
│     Motivo: chuva 60% abaixo da média histórica                  │
│     [ Ver detalhes ]                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Passo 4 — Analisa uma área específica

**Ação:** Ana clica em "Ver detalhes" da Fazenda Boa Esperança.

**O que Ana vê na tela:**

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Voltar    FAZENDA BOA ESPERANÇA — Sorriso, MT                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SCORE DE RISCO ATUAL                                            │
│  ┌───────────────────────────────────────────────┐              │
│  │                                               │              │
│  │   7.8 / 10   ALTO 🔴                          │              │
│  │                                               │              │
│  │   Na emissão da apólice (out/25): 3.9 🟢      │              │
│  │   ZARC municipal:  Risco Moderado             │              │
│  │                                               │              │
│  └───────────────────────────────────────────────┘              │
│                                                                  │
│  INDICADORES                                                     │
│  ┌────────────────┬───────────────┬──────────────┐              │
│  │ Chuva (30d)    │ NDVI          │ Temperatura  │              │
│  │ -52% vs média  │ 0.31 (baixo)  │ +3.2°C acima │              │
│  │ 🔴             │ 🔴            │ 🟡           │              │
│  └────────────────┴───────────────┴──────────────┘              │
│                                                                  │
│  IMAGEM DE SATÉLITE — Comparativo                               │
│  [ Janeiro/25 🟩🟩🟩 ]  →  [ Janeiro/26 🟨🟫🟫 ]              │
│                                                                  │
│  INTERPRETAÇÃO DA IA                                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ "A área apresentou déficit hídrico de 52% nas últimas    │  │
│  │  4 semanas. Combinado ao baixo NDVI (0.31), indica que   │  │
│  │  a lavoura está em estresse hídrico severo, coincidindo  │  │
│  │  com o período de enchimento de grãos da soja. Risco     │  │
│  │  de perda parcial estimado: 40–60%."                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [ Perguntar à IA ]   [ Exportar relatório ]                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Emoção:** Ana entende a gravidade. Quer saber exatamente o que fazer.

---

## Passo 5 — Pergunta ao assistente de IA

**Ação:** Ana clica em "Perguntar à IA" e digita sua dúvida.

**O que Ana vê na tela:**

```
┌─────────────────────────────────────────────────────────────────┐
│ ASSISTENTE SAFRAVIVA               Contexto: Fazenda Boa Esp.  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                                                                  │
│  🧑 Ana:                                                         │
│  "Qual a probabilidade de perda acima de 30% nessa área?        │
│   Preciso saber se devo ajustar a reserva de sinistro."         │
│                                                                  │
│  🤖 SafraViva:                                                   │
│  "Com base nos dados atuais desta gleba, o modelo estima        │
│   72% de probabilidade de perda superior a 30% na safra.        │
│                                                                  │
│   Histórico: em 3 safras com perfil climático similar a este,   │
│   a perda média foi de 41%.                                      │
│                                                                  │
│   Recomendação: considere provisionar reserva adicional para    │
│   esta apólice. O próximo ponto de reavaliação climática        │
│   ocorre em 12 dias."                                            │
│                                                                  │
│                                                                  │
│  ┌───────────────────────────────────────────┐ [ Enviar ]       │
│  │ Digite sua pergunta...                    │                  │
│  └───────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Passo 6 — Exporta relatório para a equipe

**Ação:** Ana clica em "Exportar relatório".

**O que Ana vê na tela:**

```
┌──────────────────────────────────────────────────┐
│ EXPORTAR RELATÓRIO                       [ X ]   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Área: Fazenda Boa Esperança — MT                │
│  Período: Jan/26                                 │
│                                                  │
│  Incluir no relatório:                           │
│  ☑ Score atual e histórico                      │
│  ☑ Indicadores climáticos (chuva, NDVI, temp.)  │
│  ☑ Imagens de satélite comparativas             │
│  ☑ Interpretação da IA                          │
│  ☐ Histórico completo de alertas                │
│                                                  │
│  Formato:  ● PDF   ○ Excel                       │
│                                                  │
│  [ Gerar relatório ]                             │
│                                                  │
└──────────────────────────────────────────────────┘
```

Ana gera o PDF e encaminha para o time de subscrição provisionar reserva.

---

---

# Jornada 2 — João (Produtor Rural)

---

## Passo 1 — Primeiro acesso pelo celular

**Contexto:** João recebeu um link da cooperativa com acesso à plataforma.

**Ação:** Abre o link no celular e faz cadastro.

**O que João vê na tela (mobile):**

```
┌───────────────────────────┐
│  🌱 SafraViva             │
│                           │
│  Bem-vindo, João!         │
│  Acesso via Cooperativa   │
│  Central do Cerrado       │
│                           │
│  [ Criar minha senha ]    │
│                           │
│  Já tem conta?            │
│  [ Entrar ]               │
└───────────────────────────┘
```

---

## Passo 2 — Cadastra a propriedade no mapa

**Ação:** Após login, o sistema pede para João marcar sua área.

**O que João vê na tela:**

```
┌───────────────────────────┐
│ ← Início  MINHA ÁREA      │
│                           │
│  Marque sua propriedade   │
│  no mapa abaixo:          │
│                           │
│  ┌─────────────────────┐  │
│  │   [mapa do Brasil]  │  │
│  │         🔍          │  │
│  │    [área marcada    │  │
│  │     com contorno    │  │
│  │     em laranja]     │  │
│  └─────────────────────┘  │
│                           │
│  Área selecionada:        │
│  ~480 hectares — MT       │
│                           │
│  Cultura: [ Soja     ▾ ]  │
│                           │
│  [ Confirmar área ]       │
└───────────────────────────┘
```

---

## Passo 3 — Vê o score da sua área pela primeira vez

**Ação:** Após confirmar a área, o sistema processa e exibe o resultado.

**O que João vê na tela:**

```
┌───────────────────────────┐
│ RISCO DA SUA ÁREA   🔄    │
├───────────────────────────┤
│                           │
│  Score SafraViva          │
│  ┌─────────────────────┐  │
│  │   7.2 / 10   ALTO   │  │
│  │        🔴           │  │
│  └─────────────────────┘  │
│                           │
│  Score ZARC do município  │
│  ┌─────────────────────┐  │
│  │  Risco Moderado     │  │
│  │        🟡           │  │
│  └─────────────────────┘  │
│                           │
│  ⚠️ Sua área apresenta    │
│  risco maior do que o     │
│  indicado pelo ZARC.      │
│                           │
│  [ Entender por quê ]     │
│  [ Perguntar à IA ]       │
└───────────────────────────┘
```

**Emoção:** João fica surpreso — o ZARC dizia risco moderado, mas sua gleba específica está em risco alto.

---

## Passo 4 — Entende os motivos

**Ação:** João toca em "Entender por quê".

**O que João vê na tela:**

```
┌───────────────────────────┐
│ ← Voltar  POR QUÊ ALTO?  │
├───────────────────────────┤
│                           │
│  Os dados da sua área     │
│  mostram:                 │
│                           │
│  💧 Chuva                 │
│  47% abaixo da média      │
│  nas últimas 3 semanas    │
│                           │
│  🌿 Saúde da vegetação    │
│  NDVI 0.29 — abaixo do   │
│  esperado para a época    │
│                           │
│  🌡️ Temperatura           │
│  +2.8°C acima da média    │
│  histórica do mês         │
│                           │
│  📅 Período crítico       │
│  Você está na janela de   │
│  plantio. Esse é o        │
│  momento de maior risco.  │
│                           │
│  [ Perguntar à IA ]       │
└───────────────────────────┘
```

---

## Passo 5 — Pergunta se deve plantar agora

**Ação:** João toca em "Perguntar à IA".

**O que João vê na tela:**

```
┌───────────────────────────┐
│ ASSISTENTE SAFRAVIVA      │
│ Contexto: sua área - MT   │
├───────────────────────────┤
│                           │
│ 🧑 João:                  │
│ "Vale plantar agora ou    │
│  espero mais tempo?"      │
│                           │
│ 🤖 SafraViva:             │
│ "O momento atual tem      │
│  risco elevado. A         │
│  previsão indica déficit  │
│  hídrico por mais 2-3     │
│  semanas.                 │
│                           │
│  Plantios nessa condição  │
│  têm 35% mais chance de   │
│  perda parcial.           │
│                           │
│  Aguardar 2 semanas       │
│  pode reduzir o risco     │
│  para nível moderado.     │
│  Vou te avisar quando     │
│  a janela melhorar. ✅"   │
│                           │
│ ┌───────────────────────┐ │
│ │ Sua pergunta...       │ │
│ └───────────────────────┘ │
│           [ Enviar ]      │
└───────────────────────────┘
```

João decide esperar. O sistema fica monitorando.

---

## Passo 6 — Recebe notificação 2 semanas depois

**Ação:** João recebe uma notificação push no celular.

**O que João vê na tela:**

```
┌───────────────────────────┐
│ 🔔 SafraViva              │
│                           │
│ "As condições da sua      │
│  área melhoraram.         │
│                           │
│  Score atual: 4.1 🟡      │
│  Risco: Moderado          │
│                           │
│  Janela favorável para    │
│  plantio identificada."   │
│                           │
│  [ Ver detalhes ]         │
└───────────────────────────┘
```

João vai ao campo e inicia o plantio com mais segurança.

---

## Passo 7 — Acompanha a safra em andamento

**Ação:** Semanas depois, João abre o app para ver como a lavoura está.

**O que João vê na tela:**

```
┌───────────────────────────┐
│ MINHA ÁREA — Semana 8     │
├───────────────────────────┤
│                           │
│  Score atual: 3.8 🟢      │
│                           │
│  🌿 NDVI esta semana      │
│  ████████░░  0.71         │
│  ↑ +0.12 vs semana ant.   │
│  Vegetação em             │
│  desenvolvimento normal   │
│                           │
│  📈 Evolução da safra     │
│  Sem. 1  ▬▬              │
│  Sem. 4  ▬▬▬▬▬           │
│  Sem. 8  ▬▬▬▬▬▬▬▬ 🟢    │
│                           │
│  Próxima atualização      │
│  em 3 dias                │
│                           │
└───────────────────────────┘
```

---

## Passo 8 — Alerta de anomalia durante a safra

**Ação:** Em março, João recebe um alerta inesperado.

**O que João vê na tela:**

```
┌───────────────────────────┐
│ ⚠️ ALERTA — SafraViva     │
│                           │
│ "Anomalia detectada no    │
│  setor norte da sua       │
│  propriedade.             │
│                           │
│  NDVI caiu 20% em 5 dias  │
│  nessa região.            │
│                           │
│  Possíveis causas:        │
│  • Estresse hídrico local │
│  • Pragas ou doenças      │
│  • Dano mecânico          │
│                           │
│  Recomendação: vistoriar  │
│  o setor norte nos        │
│  próximos 2-3 dias."      │
│                           │
│  [ Ver no mapa ]          │
└───────────────────────────┘
```

João vai ao campo, confirma ataque de pragas e trata antes de perda maior.

---

## Passo 9 — Exporta histórico para o banco

**Ação:** No fim da safra, João quer solicitar crédito rural com melhores condições.

**O que João vê na tela:**

```
┌───────────────────────────┐
│ RELATÓRIO DA SAFRA        │
│ 2025/26                   │
├───────────────────────────┤
│                           │
│ ☑ Score de risco inicial │
│ ☑ Decisão de janela de   │
│   plantio                 │
│ ☑ Evolução do NDVI       │
│ ☑ Alertas recebidos e    │
│   ações tomadas           │
│ ☑ Score final da safra   │
│                           │
│ Resultado da safra:       │
│ Sem sinistros registrados │
│ Score médio: 4.2 🟢       │
│                           │
│ [ Baixar PDF ]            │
│ [ Compartilhar com banco ]│
└───────────────────────────┘
```

João apresenta o relatório ao banco como evidência de gestão responsável do risco e consegue melhores condições de crédito.

---

## Resumo da Jornada

| Passo | Ana (Seguradora) | João (Produtor) |
|---|---|---|
| 1 | Login institucional | Cadastro via link da cooperativa |
| 2 | Dashboard com resumo da carteira | Marcação da área no mapa |
| 3 | Abertura dos alertas críticos | Visualização do score pela primeira vez |
| 4 | Análise detalhada de uma área | Entendimento dos motivos do risco |
| 5 | Pergunta à IA sobre reserva de sinistro | Pergunta à IA sobre momento de plantio |
| 6 | Exporta relatório para subscrição | Recebe notificação de janela favorável |
| 7 | — | Acompanha evolução semanal do NDVI |
| 8 | — | Recebe alerta de anomalia e age |
| 9 | — | Exporta histórico para obter crédito |

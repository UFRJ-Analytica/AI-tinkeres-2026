# SafraViva  
Inteligência climática para decisões mais seguras no agro

## Resumo Executivo

O agronegócio brasileiro depende diretamente do clima. Para lidar com esse risco, o setor utiliza instrumentos como o seguro rural, o Proagro e o Programa de Subvenção ao Prêmio do Seguro Rural (PSR).  
Fonte: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/seguro-rural

Mesmo com esses mecanismos, a forma como o risco ainda é calculado tem limitações importantes, principalmente por depender de modelos mais estáticos como o ZARC.  
Fonte: https://www.embrapa.br/busca-de-publicacoes/-/publicacao/1090923/zoneamento-agricola-de-risco-climatico

A SafraViva nasce para complementar esse modelo. A proposta é simples: combinar o que já existe com dados atualizados para gerar uma leitura mais fiel do risco em cada área agrícola.

## O Problema

O Zoneamento Agrícola de Risco Climático (ZARC) é hoje a principal referência de risco no Brasil. Ele é coordenado pelo Ministério da Agricultura com base técnica da Embrapa.  
Fonte: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/zoneamento-agricola-de-risco-climatico

Além disso, ele é obrigatório para acesso ao crédito rural, ao Proagro e ao seguro rural.  
Fonte: https://www.gov.br/agricultura/pt-br/assuntos/noticias/zoneamento-de-risco-climatico

O problema é que o ZARC não foi pensado para acompanhar o que acontece durante a safra.

Ele se baseia em séries históricas longas, normalmente entre 20 e 30 anos.  
Fonte: https://www.embrapa.br/agencia-de-informacao-tecnologica/cultivos/feijao/pre-producao/zoneamento-agroclimatico

As recomendações são feitas em nível de município, o que não capta diferenças dentro da própria propriedade.  
Fonte: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/zoneamento-agricola-de-risco-climatico

Também não considera dados atuais como umidade do solo, desenvolvimento da cultura ou eventos recentes de clima.  
Fonte: https://fgviisr.fgv.br/sites/default/files/2024-06/Relatorio%20Seguro%20rural%20no%20Brasil%20v6.pdf

Na prática, isso significa que mesmo seguindo o ZARC, o produtor ainda pode sofrer perdas relevantes. Do lado das seguradoras, isso se traduz em dificuldade de precificação e aumento de risco.

## Nossa Solução

A SafraViva conecta o modelo existente com dados mais atuais.

A plataforma integra o ZARC com informações vindas de satélite e modelos climáticos. A partir disso, gera um score de risco dinâmico para cada área agrícola, atualizado continuamente.

O uso de dados satelitais para monitoramento agrícola já é consolidado em diferentes países e aplicações.  
Fonte: https://developers.google.com/earth-engine/applications/agriculture

## Como Funciona

O uso é simples.

O usuário acessa a plataforma e seleciona uma área no mapa. A partir disso, o sistema cruza automaticamente os dados do ZARC com informações climáticas recentes e imagens de satélite.

Como resultado, o usuário recebe uma leitura clara daquela área, com score de risco, alertas e recomendações.

Dados de satélite como Sentinel e MODIS permitem acompanhar vegetação, umidade e condições climáticas em larga escala.  
Fonte: https://sentinel.esa.int/web/sentinel/missions  
Fonte: https://modis.gsfc.nasa.gov/data/

## Para quem isso importa

Para seguradoras, isso significa conseguir enxergar melhor o risco antes e durante a safra. Isso ajuda na precificação e reduz surpresas com sinistros.

Esse tipo de limitação na análise de risco é reconhecido como um dos principais desafios do seguro rural no Brasil.  
Fonte: https://fgviisr.fgv.br/sites/default/files/2024-06/Relatorio%20Seguro%20rural%20no%20Brasil%20v6.pdf

Para produtores, a plataforma traz mais segurança na tomada de decisão. Ajuda a escolher melhor quando plantar, reduz perdas e melhora o acesso a crédito.

O uso do ZARC continua sendo obrigatório para essas operações.  
Fonte: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/zoneamento-agricola-de-risco-climatico

## Mercado

O seguro rural no Brasil vem crescendo nos últimos anos, impulsionado por políticas públicas e pela necessidade de proteção contra riscos climáticos.

Relatórios do próprio governo mostram a relevância do PSR no apoio ao setor.  
Fonte: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/seguro-rural/dados/relatorios

Hoje, o mercado movimenta bilhões por ano. As estimativas indicam algo entre 70 e 100 bilhões de reais em valor segurado e cerca de 10 a 12 bilhões em prêmios anuais. Esses números são baseados em consolidações de dados públicos do setor e devem ser tratados como aproximações.

## Modelo de Negócio

A SafraViva opera como um software B2B.

A receita vem de assinaturas com seguradoras, cobrança por área monitorada e integração via API. Também existe espaço para licenciamento com cooperativas e instituições financeiras.

## Diferenciais

A principal diferença está em como conectamos o modelo regulatório com dados em tempo real.

A plataforma não substitui o ZARC, mas melhora significativamente sua aplicação prática. Além disso, trabalha com mais granularidade e escala nacional, graças ao uso de satélites.

## Tecnologia

A base tecnológica envolve dados satelitais, processamento geoespacial e infraestrutura em nuvem.

Ferramentas como o Google Earth Engine são amplamente utilizadas nesse tipo de aplicação.  
Fonte: https://earthengine.google.com/

## Impacto

A solução contribui diretamente para agricultura mais sustentável e para adaptação às mudanças climáticas.

ODS 2 — Agricultura sustentável  
Fonte: https://sdgs.un.org/goals/goal2  

ODS 13 — Ação climática  
Fonte: https://sdgs.un.org/goals/goal13  

ODS 17 — Parcerias  
Fonte: https://sdgs.un.org/goals/goal17  

## Visão

Ser uma das principais referências em inteligência de risco climático para o agro na América Latina.

## Missão

Ajudar o agro a tomar decisões mais seguras usando dados.

## Próximos passos

O foco agora está em validar a solução em campo.

Isso passa por parcerias com seguradoras, testes com cooperativas e integração com instituições financeiras que atuam no agro.
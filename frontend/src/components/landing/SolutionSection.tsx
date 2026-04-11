import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"
import { Database, Globe2, Zap, BarChart3, Shield, Radio } from "lucide-react"

const features = [
  {
    icon: Database,
    title: "ZARC como Base",
    description:
      "Mantemos o ZARC como fundação regulatória, garantindo conformidade com as exigências legais do crédito rural, Proagro e seguro rural.",
    detail:
      "Obrigatório para acesso ao crédito rural, Proagro e seguro rural — não abrimos mão da conformidade.",
  },
  {
    icon: Radio,
    title: "Satélites em Tempo Real",
    description:
      "Integramos dados do Sentinel-2 (ESA) e MODIS (NASA) para monitorar vegetação, umidade do solo e condições climáticas em escala nacional.",
    detail:
      "Atualização a cada passagem orbital — aproximadamente a cada 5 dias com Sentinel-2 e diariamente com MODIS.",
  },
  {
    icon: Zap,
    title: "Score Dinâmico",
    description:
      "Geramos um score de risco entre 0 e 100 atualizado continuamente para cada área, combinando dados históricos e em tempo real.",
    detail:
      "O score captura eventos climáticos em curso, tendências de desenvolvimento da cultura e anomalias recentes.",
  },
  {
    icon: BarChart3,
    title: "Alertas e Recomendações",
    description:
      "Além do score, a plataforma emite alertas automáticos e recomendações acionáveis para seguradoras e produtores.",
    detail:
      "Alertas configuráveis por threshold de risco, tipo de cultura e região geográfica.",
  },
  {
    icon: Globe2,
    title: "Escala Nacional",
    description:
      "A plataforma cobre todo o território brasileiro com granularidade em nível de talhão graças ao uso de satélites.",
    detail:
      "Resolução espacial de até 10 metros por pixel com Sentinel-2 — muito abaixo da escala municipal do ZARC.",
  },
  {
    icon: Shield,
    title: "Complementar ao ZARC",
    description:
      "Não substituímos o modelo regulatório — o aprimoramos. A SafraViva é totalmente compatível com os fluxos existentes.",
    detail:
      "APIs para integração direta com sistemas de seguradoras, cooperativas e instituições financeiras.",
  },
]

export default function SolutionSection() {
  return (
    <section id="solucao" className="py-24 bg-background">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="text-center space-y-4 mb-14">
          {/* bg-primary/10 text-primary — reactivo ao tema */}
          <Badge className="bg-primary/10 text-primary border border-primary/20 text-xs">
            Nossa Solução
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight">
            SafraViva preenche as lacunas
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto leading-relaxed">
            Conectamos o que já existe com o que está faltando: dados em tempo
            real, granularidade por talhão e inteligência aplicada ao agro.
          </p>
        </div>

        {/* Equação visual */}
        <div className="flex items-center justify-center gap-3 mb-14 flex-wrap">
          {[
            { label: "ZARC", cls: "bg-secondary text-secondary-foreground border-border" },
            { label: "+", plain: true },
            { label: "Satélite", cls: "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-700" },
            { label: "+", plain: true },
            { label: "IA", cls: "bg-purple-100 text-purple-700 border-purple-300 dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-700" },
            { label: "=", plain: true },
            {
              label: "Score Dinâmico de Risco",
              /* bg-primary text-primary-foreground — reactivo ao tema */
              cls: "bg-primary text-primary-foreground border-primary text-sm px-5 py-1.5 shadow-md shadow-primary/25",
              highlight: true,
            },
          ].map((item, i) =>
            item.plain ? (
              <span key={i} className="text-xl text-muted-foreground font-light">
                {item.label}
              </span>
            ) : (
              <Badge key={i} className={`border text-xs px-3 py-1 ${item.cls}`}>
                {item.label}
              </Badge>
            )
          )}
        </div>

        <Separator className="mb-14" />

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature) => (
            <HoverCard key={feature.title} openDelay={200} closeDelay={100}>
              <HoverCardTrigger asChild>
                <Card className="cursor-default hover:shadow-md hover:border-primary/25 transition-all">
                  <CardHeader className="pb-3">
                    {/* bg-primary/10 text-primary — reactivo ao tema */}
                    <div className="w-10 h-10 bg-primary/10 border border-primary/15 rounded-xl flex items-center justify-center mb-3">
                      <feature.icon className="w-5 h-5 text-primary" />
                    </div>
                    <CardTitle className="text-base">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </HoverCardTrigger>
              <HoverCardContent className="w-72" side="top">
                <div className="space-y-1.5">
                  <p className="text-xs font-semibold text-primary">Saiba mais</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {feature.detail}
                  </p>
                </div>
              </HoverCardContent>
            </HoverCard>
          ))}
        </div>
      </div>
    </section>
  )
}

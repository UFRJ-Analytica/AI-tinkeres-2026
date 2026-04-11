import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { CheckCircle2 } from "lucide-react"

const audiences = {
  seguradoras: {
    badge: "Seguradoras rurais",
    /* Azul mantido intencionalmente para diferenciar da cor primária */
    badgeCls: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-700",
    title: "Para Seguradoras",
    description:
      "Precificação mais precisa, menos surpresas com sinistros e monitoramento contínuo da carteira.",
    benefits: [
      "Visualize o risco antes e durante toda a safra",
      "Melhore a precificação com dados mais granulares",
      "Reduza surpresas com sinistros inesperados",
      "Integre via API aos seus sistemas existentes",
      "Monitore toda a carteira em tempo real",
      "Relatórios automáticos por área e por período",
    ],
    checkCls: "text-blue-600 dark:text-blue-400",
    testimonial: {
      quote:
        "Com dados mais precisos por área, conseguimos precificar melhor e reduzir nossa exposição em regiões de risco climático elevado.",
      name: "Analista de Risco Sênior",
      company: "Seguradora Rural · São Paulo",
      avatar: "AR",
      avatarCls: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    },
  },
  produtores: {
    badge: "Produtores & Cooperativas",
    /* text-primary bg-primary/10 — reactivo ao tema */
    badgeCls: "bg-primary/10 text-primary border-primary/20",
    title: "Para Produtores",
    description:
      "Mais segurança na tomada de decisão, redução de perdas e melhor acesso a crédito rural.",
    benefits: [
      "Tome decisões de plantio com dados reais",
      "Antecipe eventos climáticos adversos",
      "Reduza perdas por erros de timing no plantio",
      "Melhore o acesso a crédito e seguro rural",
      "Acompanhe sua área com score atualizado",
      "Receba alertas personalizados por cultura",
    ],
    /* text-primary — reactivo ao tema */
    checkCls: "text-primary",
    testimonial: {
      quote:
        "Evitei plantar em um período de risco elevado que os alertas apontaram. A safra desse ciclo foi significativamente melhor.",
      name: "Produtor Rural",
      company: "Soja e Milho · Mato Grosso",
      avatar: "PR",
      /* bg-primary/10 text-primary — reactivo ao tema */
      avatarCls: "bg-primary/10 text-primary",
    },
  },
}

export default function AudienceSection() {
  return (
    <section id="para-quem" className="py-24 bg-background">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="text-center space-y-4 mb-14">
          <Badge variant="outline" className="text-xs">
            Para Quem
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight">
            Para quem é a SafraViva
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto leading-relaxed">
            A plataforma serve dois perfis complementares que dependem de
            informação climática precisa para tomar boas decisões.
          </p>
        </div>

        <Tabs defaultValue="seguradoras" className="w-full">
          <TabsList className="grid w-full max-w-xs mx-auto grid-cols-2 mb-12 h-9">
            <TabsTrigger value="seguradoras" className="text-xs">
              Seguradoras
            </TabsTrigger>
            <TabsTrigger value="produtores" className="text-xs">
              Produtores
            </TabsTrigger>
          </TabsList>

          {Object.entries(audiences).map(([key, data]) => (
            <TabsContent key={key} value={key} className="mt-0">
              <div className="grid lg:grid-cols-2 gap-8 items-start">
                <Card className="shadow-sm">
                  <CardHeader className="pb-4">
                    <Badge className={`w-fit text-xs border mb-2 ${data.badgeCls}`}>
                      {data.badge}
                    </Badge>
                    <CardTitle className="text-2xl">{data.title}</CardTitle>
                    <CardDescription className="text-base leading-relaxed">
                      {data.description}
                    </CardDescription>
                  </CardHeader>
                  <Separator className="mx-6 mb-4 w-auto" />
                  <CardContent>
                    <ul className="space-y-3">
                      {data.benefits.map((benefit) => (
                        <li key={benefit} className="flex items-start gap-3">
                          <CheckCircle2
                            className={`w-4 h-4 shrink-0 mt-0.5 ${data.checkCls}`}
                          />
                          <span className="text-sm leading-relaxed">
                            {benefit}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <div className="space-y-4">
                  <Card className="bg-muted/40 border-0 shadow-none">
                    <CardContent className="p-8">
                      <p className="text-lg leading-relaxed text-foreground/70 italic mb-6">
                        "{data.testimonial.quote}"
                      </p>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback
                            className={`text-sm font-semibold ${data.testimonial.avatarCls}`}
                          >
                            {data.testimonial.avatar}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-semibold text-sm">
                            {data.testimonial.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {data.testimonial.company}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-dashed">
                    <CardContent className="p-6 text-center space-y-2">
                      <p className="text-sm font-medium">
                        Quer entender melhor como funciona para o seu caso?
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Agende uma demonstração personalizada sem compromisso.
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </section>
  )
}

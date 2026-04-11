import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Check, Building2, Layers, Network } from "lucide-react"

const plans = [
  {
    icon: Building2,
    name: "Assinatura",
    description:
      "Para seguradoras que precisam de monitoramento contínuo de toda a carteira.",
    badge: "Mais Popular",
    highlight: false,
    features: [
      "Monitoramento ilimitado de apólices",
      "Alertas automáticos em tempo real",
      "Dashboard analítico completo",
      "Relatórios personalizáveis por período",
      "API de integração inclusa",
      "Suporte técnico dedicado",
    ],
  },
  {
    icon: Layers,
    name: "Por Área Monitorada",
    description:
      "Cobrança proporcional ao volume de hectares monitorados — ideal para escalar.",
    badge: "Recomendado",
    highlight: true,
    features: [
      "Preço por hectare monitorado",
      "Score de risco por talhão",
      "Alertas georreferenciados",
      "Integração com cooperativas",
      "Acesso via API ou plataforma web",
      "Histórico completo de scores",
    ],
  },
  {
    icon: Network,
    name: "API & Licenciamento",
    description:
      "Para cooperativas, instituições financeiras e parceiros estratégicos.",
    badge: "Enterprise",
    highlight: false,
    features: [
      "Acesso completo à API REST",
      "White-label disponível",
      "SLA garantido por contrato",
      "Suporte técnico premium",
      "Modelo de compartilhamento de dados",
      "Onboarding personalizado",
    ],
  },
]

export default function PricingSection() {
  return (
    <section id="modelo" className="py-24 bg-background">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="text-center space-y-4 mb-14">
          <Badge variant="outline" className="text-xs">
            Modelo de Negócio
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight">
            Flexível para cada perfil
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto leading-relaxed">
            A SafraViva opera como um software B2B com modelos de receita
            adaptados a cada tipo de cliente e escala de operação.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 items-stretch">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative flex flex-col ${
                plan.highlight
                  ? /* border-primary shadow-primary/15 — reactivo ao tema */
                    "border-2 border-primary shadow-xl shadow-primary/10"
                  : ""
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  {/* bg-primary text-primary-foreground — reactivo ao tema */}
                  <Badge className="bg-primary text-primary-foreground border-0 shadow-sm">
                    {plan.badge}
                  </Badge>
                </div>
              )}

              <CardHeader className="pb-4">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${
                    plan.highlight
                      ? "bg-primary/10"   /* reactivo ao tema */
                      : "bg-muted"
                  }`}
                >
                  <plan.icon
                    className={`w-5 h-5 ${
                      plan.highlight
                        ? "text-primary"  /* reactivo ao tema */
                        : "text-muted-foreground"
                    }`}
                  />
                </div>
                {!plan.highlight && (
                  <Badge variant="outline" className="w-fit text-xs mb-3">
                    {plan.badge}
                  </Badge>
                )}
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <CardDescription className="leading-relaxed text-sm">
                  {plan.description}
                </CardDescription>
              </CardHeader>

              <Separator className="mx-6" />

              <CardContent className="pt-5 flex-1">
                <ul className="space-y-2.5">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2.5 text-sm">
                      {/* text-primary para o card destacado — reactivo ao tema */}
                      <Check
                        className={`w-4 h-4 shrink-0 mt-0.5 ${
                          plan.highlight ? "text-primary" : "text-muted-foreground"
                        }`}
                      />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter className="pt-4">
                {/* variant="default" usa bg-primary automaticamente */}
                <Button
                  className="w-full"
                  variant={plan.highlight ? "default" : "outline"}
                  size="sm"
                >
                  Solicitar Proposta
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

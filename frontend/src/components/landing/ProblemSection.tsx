import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Calendar, MapPin, CloudOff, AlertTriangle } from "lucide-react"

const problems = [
  {
    icon: Calendar,
    title: "Dados Históricos Desatualizados",
    description:
      "O ZARC utiliza séries históricas de 20 a 30 anos para calcular o risco climático. Sem considerar as condições atuais, o modelo não captura eventos climáticos recentes nem tendências emergentes.",
    impact: "Alta probabilidade de subnotificação de risco",
    iconColor: "text-orange-600",
    bg: "bg-orange-50",
    border: "border-orange-200",
    impactColor: "text-orange-700",
  },
  {
    icon: MapPin,
    title: "Granularidade Limitada",
    description:
      "As recomendações do ZARC são feitas em nível de município, o que não consegue captar variações significativas de microclima e condições de solo dentro de uma mesma propriedade.",
    impact: "Estimativas de risco imprecisas por área",
    iconColor: "text-red-600",
    bg: "bg-red-50",
    border: "border-red-200",
    impactColor: "text-red-700",
  },
  {
    icon: CloudOff,
    title: "Sem Dados em Tempo Real",
    description:
      "O modelo não considera dados atuais como umidade do solo, índice de vegetação (NDVI), desenvolvimento da cultura ou eventos climáticos recentes — fatores críticos durante a safra.",
    impact: "Risco subestimado em períodos críticos",
    iconColor: "text-purple-600",
    bg: "bg-purple-50",
    border: "border-purple-200",
    impactColor: "text-purple-700",
  },
]

export default function ProblemSection() {
  return (
    <section id="problema" className="py-24 bg-slate-50">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="text-center space-y-4 mb-14">
          <Badge
            variant="outline"
            className="border-slate-300 text-slate-600 text-xs"
          >
            O Desafio
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight">
            O modelo atual tem limites
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto leading-relaxed">
            O ZARC é uma referência técnica e regulatória importante, mas foi
            construído para um contexto diferente. A realidade do campo exige
            mais precisão e atualização contínua.
          </p>
        </div>

        <Alert className="mb-10 border-amber-200 bg-amber-50 text-amber-900">
          <AlertTriangle className="h-4 w-4 text-amber-600" />
          <AlertTitle className="text-amber-800 font-semibold">
            Impacto real no setor
          </AlertTitle>
          <AlertDescription className="text-amber-700">
            Mesmo seguindo o ZARC, produtores ainda podem sofrer perdas
            relevantes. Para seguradoras, isso se traduz em dificuldade de
            precificação e aumento inesperado de sinistros na carteira.
          </AlertDescription>
        </Alert>

        <div className="grid md:grid-cols-3 gap-6">
          {problems.map((problem) => (
            <Card
              key={problem.title}
              className={`border-2 ${problem.border} overflow-hidden`}
            >
              <CardHeader className={`${problem.bg} pb-4`}>
                <div
                  className={`w-10 h-10 rounded-lg ${problem.bg} border ${problem.border} flex items-center justify-center mb-3`}
                >
                  <problem.icon className={`w-5 h-5 ${problem.iconColor}`} />
                </div>
                <CardTitle className="text-base leading-snug">
                  {problem.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-5 space-y-4">
                <CardDescription className="text-sm leading-relaxed text-foreground/70">
                  {problem.description}
                </CardDescription>
                <Separator />
                <div
                  className={`text-xs font-semibold ${problem.impactColor} flex items-center gap-1.5`}
                >
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  {problem.impact}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

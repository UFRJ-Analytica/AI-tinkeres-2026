import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { TrendingUp } from "lucide-react"

const marketStats = [
  {
    label: "Valor Segurado",
    value: "R$ 70–100bi",
    description: "Em apólices de seguro rural por ano no Brasil",
    progress: 85,
  },
  {
    label: "Prêmios Anuais",
    value: "R$ 10–12bi",
    description: "Em prêmios pagos ao mercado segurador",
    progress: 60,
  },
  {
    label: "Crescimento",
    value: "Acelerado",
    description: "Impulsionado pelo PSR e políticas públicas federais",
    progress: 75,
  },
]

const segments = [
  { label: "Seguradoras rurais", tag: "Foco primário" },
  { label: "Cooperativas agrícolas", tag: "Foco secundário" },
  { label: "Instituições financeiras", tag: "Parceiro estratégico" },
]

export default function MarketSection() {
  return (
    <section id="mercado" className="py-24 bg-slate-900 text-white">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="text-center space-y-4 mb-14">
          {/*
            Seção com fundo escuro fixo (slate-900) — os tokens do tema
            resolveriam para light-mode. Mantemos bg/text explícitos
            para garantir legibilidade neste contexto de design escuro.
            A --primary em dark mode (emerald-400) seria usada se a
            seção fosse marcada com class="dark".
          */}
          <Badge className="bg-white/10 text-white/80 border border-white/20 text-xs">
            Mercado
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight">
            Um mercado bilionário em crescimento
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
            O seguro rural no Brasil cresce impulsionado por políticas públicas
            como o PSR, criando uma janela de oportunidade significativa para
            soluções de inteligência climática.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-5 mb-14">
          {marketStats.map((stat) => (
            <Card
              key={stat.label}
              className="bg-slate-800 border-slate-700 text-white"
            >
              <CardHeader className="pb-2">
                <p className="text-slate-400 text-xs uppercase tracking-wider">
                  {stat.label}
                </p>
                <CardTitle className="text-3xl font-bold text-white tracking-tight">
                  {stat.value}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-400 leading-relaxed">
                  {stat.description}
                </p>
                {/* Progress bar usa primary — que em light mode é emerald-600 */}
                <Progress
                  value={stat.progress}
                  className="h-1.5 bg-slate-700 [&>div]:bg-primary"
                />
              </CardContent>
            </Card>
          ))}
        </div>

        <Separator className="bg-slate-700 mb-14" />

        <div className="grid md:grid-cols-2 gap-10 items-center">
          <div className="space-y-5">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-4 h-4 text-white" />
              </div>
              <h3 className="text-xl font-semibold">
                Crescimento sustentado por políticas públicas
              </h3>
            </div>
            <p className="text-slate-400 leading-relaxed text-sm">
              O seguro rural no Brasil vem crescendo de forma consistente,
              impulsionado pelo Programa de Subvenção ao Prêmio (PSR) e pela
              necessidade crescente de proteção contra riscos climáticos.
              Relatórios do Ministério da Agricultura confirmam a relevância
              desses instrumentos.
            </p>
            <p className="text-slate-400 leading-relaxed text-sm">
              À medida que as mudanças climáticas tornam eventos extremos mais
              frequentes e severos, a demanda por ferramentas de gestão de risco
              mais sofisticadas só tende a crescer — e a SafraViva está
              posicionada para atender esse mercado.
            </p>
          </div>

          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-7 space-y-1">
              <p className="text-slate-400 text-xs uppercase tracking-wider mb-4">
                Segmentos prioritários
              </p>
              {segments.map((item, i) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-sm text-white font-medium">
                      {item.label}
                    </span>
                    <Badge
                      variant="outline"
                      className="border-slate-600 text-slate-400 text-xs"
                    >
                      {item.tag}
                    </Badge>
                  </div>
                  {i < segments.length - 1 && (
                    <Separator className="bg-slate-700" />
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}

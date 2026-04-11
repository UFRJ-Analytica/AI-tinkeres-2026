import { Card, CardContent } from "@/components/ui/card"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Info } from "lucide-react"

const stats = [
  {
    value: "R$ 70–100bi",
    label: "Mercado de seguro rural",
    sublabel: "Em valor segurado por ano no Brasil",
    tooltip: "Estimativa baseada em consolidações de dados públicos do Ministério da Agricultura",
  },
  {
    value: "20–30 anos",
    label: "Séries históricas do ZARC",
    sublabel: "Sem atualização com dados em tempo real",
    tooltip: "O ZARC baseia suas recomendações em séries históricas longas, sem considerar o contexto atual",
  },
  {
    value: "2 satélites",
    label: "Sentinel-2 + MODIS",
    sublabel: "Integrados para cobertura nacional",
    tooltip: "Sentinel-2 (ESA) oferece resolução de 10m/pixel; MODIS (NASA) cobre todo o Brasil frequentemente",
  },
  {
    value: "Contínuo",
    label: "Score atualizado",
    sublabel: "Risco recalculado com novos dados",
    tooltip: "O score de risco é recalculado automaticamente a cada nova passagem orbital e atualização climática",
  },
]

export default function StatsSection() {
  return (
    <section className="py-14 bg-white border-b">
      <div className="container mx-auto max-w-7xl px-4">
        <TooltipProvider>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-1">
            {stats.map((stat, i) => (
              <Card
                key={stat.label}
                className={`border-0 shadow-none rounded-none ${i < 3 ? "lg:border-r lg:border-border" : ""}`}
              >
                <CardContent className="py-6 px-8 text-center space-y-1.5">
                  <p className="text-3xl font-bold text-primary tracking-tight">
                    {stat.value}
                  </p>
                  <div className="flex items-center justify-center gap-1">
                    <p className="text-sm font-semibold text-foreground">
                      {stat.label}
                    </p>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button className="text-muted-foreground hover:text-foreground transition-colors">
                          <Info className="w-3 h-3" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent className="max-w-52 text-center">
                        <p className="text-xs">{stat.tooltip}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <p className="text-xs text-muted-foreground">{stat.sublabel}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TooltipProvider>
      </div>
    </section>
  )
}

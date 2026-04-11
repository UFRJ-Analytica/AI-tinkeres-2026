import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { MapPin, Cpu, BarChart3 } from "lucide-react"

const steps = [
  {
    number: "01",
    icon: MapPin,
    title: "Selecione uma área no mapa",
    short: "Escolha qualquer área agrícola no mapa interativo da plataforma.",
    detail:
      "O usuário acessa a plataforma e seleciona a área de interesse diretamente no mapa. É possível selecionar polígonos personalizados, talhões ou regiões inteiras. A plataforma também aceita importação via shapefile ou coordenadas geográficas para maior agilidade.",
  },
  {
    number: "02",
    icon: Cpu,
    title: "Cruzamento automático de dados",
    short:
      "O sistema processa automaticamente ZARC, satélite e dados climáticos.",
    detail:
      "Em segundos, o sistema cruza os dados do ZARC para a área selecionada com imagens recentes do Sentinel-2 e MODIS, além de dados climáticos do INMET e modelos de previsão. O processamento inclui cálculo de NDVI, umidade estimada do solo, temperatura e histórico de precipitação recente.",
  },
  {
    number: "03",
    icon: BarChart3,
    title: "Score + alertas + recomendações",
    short:
      "Receba o score de risco, alertas automáticos e recomendações acionáveis.",
    detail:
      "O resultado é um score de risco entre 0 e 100, acompanhado de alertas prioritários e recomendações específicas. Para seguradoras, inclui subsídio para precificação e análise de sinistros. Para produtores, orienta decisões de manejo, janela de plantio e aplicação de insumos.",
  },
]

export default function HowItWorksSection() {
  return (
    <section id="como-funciona" className="py-24 bg-muted/40">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="text-center space-y-4 mb-14">
          {/* border-primary/30 text-primary — reactivo ao tema */}
          <Badge
            variant="outline"
            className="border-primary/30 text-primary text-xs"
          >
            Como Funciona
          </Badge>
          <h2 className="text-4xl font-bold tracking-tight">
            Simples de usar, poderoso nos resultados
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto leading-relaxed">
            Em três passos, qualquer análise de risco agrícola se torna mais
            precisa e atualizada com dados reais.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          <div className="space-y-3">
            {steps.map((step, i) => (
              <Card key={step.number} className="border-0 shadow-sm bg-card">
                <CardContent className="p-5 flex gap-5">
                  <div className="flex flex-col items-center shrink-0">
                    {/* bg-primary text-primary-foreground — reactivo ao tema */}
                    <div className="w-11 h-11 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">
                      {step.number}
                    </div>
                    {i < steps.length - 1 && (
                      <Separator
                        orientation="vertical"
                        className="flex-1 bg-primary/20 mt-2 min-h-6"
                      />
                    )}
                  </div>
                  <div className="space-y-1 pt-2.5 pb-1">
                    <div className="flex items-center gap-2">
                      {/* text-primary — reactivo ao tema */}
                      <step.icon className="w-4 h-4 text-primary shrink-0" />
                      <h3 className="font-semibold text-sm">{step.title}</h3>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {step.short}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div>
            <Accordion
              type="single"
              collapsible
              defaultValue="step-0"
              className="space-y-2"
            >
              {steps.map((step, i) => (
                <AccordionItem
                  key={step.number}
                  value={`step-${i}`}
                  className="bg-card rounded-xl border px-4 data-[state=open]:border-primary/25 data-[state=open]:shadow-sm transition-all"
                >
                  <AccordionTrigger className="hover:no-underline py-4 gap-3">
                    <div className="flex items-center gap-3 text-left">
                      {/* bg-primary text-primary-foreground — reactivo ao tema */}
                      <Badge className="bg-primary text-primary-foreground border-0 min-w-8 justify-center font-bold shrink-0">
                        {step.number}
                      </Badge>
                      <span className="font-medium text-sm leading-snug">
                        {step.title}
                      </span>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="pb-4">
                    <div className="pl-11 text-sm text-muted-foreground leading-relaxed">
                      {step.detail}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        </div>
      </div>
    </section>
  )
}

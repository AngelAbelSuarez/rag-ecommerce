import { CreditCard, Shield, Truck } from "lucide-react";
import { Link } from "react-router";

import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/Navbar";

const features = [
  {
    icon: Truck,
    title: "Envíos",
    description: "Información sobre tiempos de entrega, costos y zonas de cobertura.",
  },
  {
    icon: Shield,
    title: "Garantía",
    description: "Conocé la cobertura de garantía y los procedimientos de reclamo.",
  },
  {
    icon: CreditCard,
    title: "Pagos",
    description: "Consultá métodos de pago, facturación y opciones de financiación.",
  },
];

const stats = [
  { value: "5", label: "Documentos" },
  { value: "159", label: "Chunks" },
  { value: "24/7", label: "Disponible" },
];

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <Navbar />

      <main className="flex-1">
        <section className="relative overflow-hidden px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
          <div className="mx-auto max-w-4xl text-center">
            <span className="mb-4 inline-flex items-center rounded-full border border-[var(--border-hex)] bg-[var(--bg-sidebar)] px-3 py-1 text-sm font-medium text-[var(--accent-hex)]">
              Asistente IA
            </span>
            <h1 className="mb-6 text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
              BimBam Chat
            </h1>
            <p className="mb-4 text-xl font-semibold text-[var(--accent-hex)] sm:text-2xl">
              Tu asistente inteligente de BimBam Buy
            </p>
            <p className="mb-8 text-lg text-[var(--text-secondary)] sm:text-xl">
              Respondé preguntas sobre envíos, garantías, reembolsos, pagos y más
              en segundos.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button asChild size="lg" className="min-w-[10rem]">
                <Link to="/chat">Comenzar</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="min-w-[10rem]">
                <Link to="/chat">Hablar con BimBam</Link>
              </Button>
            </div>
          </div>
        </section>

        <section className="border-y border-[var(--border-hex)] bg-[var(--bg-sidebar)] px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-6xl">
            <h2 className="mb-10 text-center text-2xl font-bold sm:text-3xl">
              ¿Qué podés consultar?
            </h2>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={feature.title}
                    className="rounded-xl border border-[var(--border-hex)] bg-[var(--bg-primary)] p-6 shadow-sm transition-transform hover:-translate-y-1"
                  >
                    <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-[var(--accent-hex)]/10 text-[var(--accent-hex)]">
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="mb-2 text-lg font-semibold">{feature.title}</h3>
                    <p className="text-[var(--text-secondary)]">{feature.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-5xl">
            <div className="grid gap-8 sm:grid-cols-3">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="text-center"
                >
                  <div className="mb-2 text-4xl font-extrabold text-[var(--accent-hex)] sm:text-5xl">
                    {stat.value}
                  </div>
                  <div className="text-[var(--text-secondary)]">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl rounded-2xl bg-[var(--accent-hex)] px-6 py-12 text-center text-white sm:px-12">
            <h2 className="mb-4 text-2xl font-bold sm:text-3xl">
              ¿Listo para resolver tus dudas?
            </h2>
            <p className="mb-8 text-white/90">
              BimBam te responde en segundos.
            </p>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="min-w-[10rem] bg-white text-[var(--accent-hex)] hover:bg-white/90"
            >
              <Link to="/chat">Ir al chat</Link>
            </Button>
          </div>
        </section>
      </main>

      <footer className="border-t border-[var(--border-hex)] bg-[var(--bg-sidebar)] px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl text-center text-sm text-[var(--text-secondary)]">
          <p>© 2026 BimBam Buy. Todos los derechos reservados.</p>
        </div>
      </footer>
    </div>
  );
}

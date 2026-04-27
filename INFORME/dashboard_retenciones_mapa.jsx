import React, { useEffect, useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/  ui/button";
import { motion } from "framer-motion";
import { MapPin, Layers, Calendar } from "lucide-react";

// Dashboard de HITOS del Plan Verano
// Cada punto = evento crítico (retención por alcohol / sustancias / grave)

export default function DashboardRetencionesMapa() {
  const [datos, setDatos] = useState([]);
  const [region, setRegion] = useState("TODAS");
  const [tipo, setTipo] = useState("TODOS");

  useEffect(() => {
    fetch("/datos.json")
      .then(r => r.json())
      .then(d => setDatos(d.detalle_incidencias || []));
  }, []);

  const filtrados = datos.filter(d => {
    const okRegion = region === "TODAS" || d.region === region;
    const okTipo = tipo === "TODOS" || d.resultado === tipo;
    return okRegion && okTipo;
  });

  const regiones = ["TODAS", ...new Set(datos.map(d => d.region))];
  const tipos = ["TODOS", "ALCOHOLEMIA", "SUSTANCIA"];

  return (
    <div className="p-4 grid gap-4">

      <motion.h1
        className="text-xl font-bold"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        Mapa de Hitos – Retenciones Plan Verano
      </motion.h1>

      <Card className="rounded-2xl shadow">
        <CardContent className="p-4 flex gap-4 items-center">

          <Layers className="w-4 h-4" />

          <select
            className="border rounded p-2"
            value={region}
            onChange={e => setRegion(e.target.value)}
          >
            {regiones.map(r => (
              <option key={r}>{r}</option>
            ))}
          </select>

          <select
            className="border rounded p-2"
            value={tipo}
            onChange={e => setTipo(e.target.value)}
          >
            {tipos.map(t => (
              <option key={t}>{t}</option>
            ))}
          </select>

          <div className="ml-auto text-sm">
            Hitos: {filtrados.length}
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow">
        <CardContent className="p-2">

          <div className="h-[520px] w-full border rounded-2xl relative bg-slate-50">

            {filtrados.map((p, i) => (
              <motion.div
                key={i}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute"
                style={{ left: p.lng || 50, top: p.lat || 50 }}
                title={`${p.resultado} – ${p.region}`}
              >
                <MapPin className="w-5 h-5" />
              </motion.div>
            ))}

            <div className="absolute inset-0 flex items-center justify-center text-sm opacity-60">
              Conectar con coordenadas reales (lat/lng) o geocodificación por localidad
            </div>

          </div>

        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow">
        <CardContent className="p-4 grid gap-2">
          <h2 className="font-semibold">Definición de Hito</h2>
          <p className="text-sm opacity-80">
            Cada punto representa un evento con relevancia jurídica:
          </p>
          <ul className="text-sm list-disc pl-4 opacity-80">
            <li>Alcoholemia positiva validada por medición técnica</li>
            <li>Detección de sustancias psicoactivas</li>
            <li>Retención efectiva del vehículo o conductor</li>
          </ul>
        </CardContent>
      </Card>

    </div>
  );
}

// Archivo: src/content/config.ts
// Versión final y completa. Define la estructura de todas tus colecciones.

import { z, defineCollection } from 'astro:content';

// 1. Definimos la colección para los datos de cada EQUIPO.
const teamsCollection = defineCollection({
  type: 'data',
  schema: z.object({
    team_info: z.object({
      id: z.number(),
      time: z.string(),
      sigla: z.string(),
      display_name: z.string(),
      slug: z.string(), // Crítico: nos aseguramos de que Astro sepa que el slug está en tus datos.
      logo: z.string(),
      estadio: z.string().optional(),
      league_slug: z.string().optional(),
    }),
    proximos_jogos: z.array(z.any()),
    ultimos_resultados: z.array(z.any()),
  }),
});

// 2. Definimos la colección para las TABLAS DE CLASIFICACIÓN (Standings).
const standingsCollection = defineCollection({
    type: 'data',
    schema: z.array(z.object({
        pos: z.number(),
        time: z.string(),
        display_name: z.string(),
        slug: z.string(),
        logo: z.string(),
        pts: z.number(),
        v: z.number(),
        e: z.number(),
        d: z.number(),
        gp: z.number(),
        gc: z.number(),
        sg: z.number(),
    }))
});


// 3. Exportamos las colecciones para que Astro las reconozca.
export const collections = {
  'teams': teamsCollection,
  'standings': standingsCollection,
};
import React, { Suspense, lazy } from 'react';
import { useParams, Navigate } from 'react-router-dom';

// Глобы И АБСОЛЮТНЫЕ, и ОТНОСИТЕЛЬНЫЕ — объединяем
const absPages = import.meta.glob('/src/template_full/pages/**/page.tsx');
const relPages = import.meta.glob('./template_full/pages/**/page.tsx');
const pages = { ...absPages, ...relPages } as Record<string, () => Promise<any>>;

function makeCandidates(rest: string): string[] {
  const clean = (rest || '').replace(/^\/+|\/+$/g, '');
  const bases = [
    '/src/template_full/pages', '/src/template_full/pages/app',
    './template_full/pages',    './template_full/pages/app',
  ];
  const out: string[] = [];
  for (const b of bases) {
    if (clean) {
      out.push(`${b}/${clean}/page.tsx`);
      out.push(`${b}/${clean}/index.tsx`);
    }
  }
  if (!clean) {
    out.push('/src/template_full/pages/app/page.tsx');
    out.push('/src/template_full/pages/page.tsx');
    out.push('./template_full/pages/app/page.tsx');
    out.push('./template_full/pages/page.tsx');
  }
  return Array.from(new Set(out));
}

export default function TemplateRouter() {
  const rest = (useParams()['*'] ?? '').trim();

  if (!rest) return <Navigate to="/template/dashboards/default" replace />;

  const candidates = makeCandidates(rest);

  for (const key of candidates) {
    if (key in pages) {
      const Lazy = lazy(pages[key] as any);
      return (
        <Suspense fallback={null}>
          <Lazy />
        </Suspense>
      );
    }
  }

  // Если не нашли соответствующий файл — отправляем на общую 404
  return <Navigate to="/404" replace />;
}

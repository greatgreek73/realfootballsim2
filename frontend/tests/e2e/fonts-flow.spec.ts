import { test, expect } from '@playwright/test';
import { createHash } from 'node:crypto';
import { request as pwRequest } from '@playwright/test';


/**
 * Пайплайн шрифтов — Шаг 1
 * Цель: браузер получает страницу от Vite dev на :5173
 * Критерии:
 *  - статус 200 при заходе на /
 *  - в HTML присутствует служебный скрипт "/@vite/client" (признак Vite dev)
 */
test('step1: Vite dev is reachable at :5173 (@step1)', async ({ page }) => {
  // 1) открыть корень (baseURL задан в playwright.config.ts)
  const response = await page.goto('/', { waitUntil: 'domcontentloaded' });
  expect(response, 'no response from Vite').toBeTruthy();
  expect(response!.ok(), `non-OK status: ${response?.status()}`).toBeTruthy();

  // 2) проверить, что это именно Vite dev (в HTML подключается /@vite/client)
  const html = await page.content();
  expect(
    html.includes('/@vite/client'),
    'expected Vite dev client script (/@vite/client) to be in HTML'
  ).toBeTruthy();

  // 3) доп. sanity-check: на странице есть корневой контейнер (#root)
  const root = await page.$('#root');
  expect(root, 'missing #root element').not.toBeNull();
});

test('step2: index.html links /static/css/fonts.css (@step2)', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });

  // Ищем линк в <head>; допускаем query string после fonts.css
  const link = page.locator('head link[rel="stylesheet"][href^="/static/css/fonts.css"]');
  const count = await link.count();
  expect(count, 'link to /static/css/fonts.css not found in <head>').toBeGreaterThan(0);

  // Доп. проверка: href действительно начинается с нужного пути
  const href = await link.first().getAttribute('href');
  expect(href?.startsWith('/static/css/fonts.css')).toBeTruthy();
});

/**
 * Пайплайн шрифтов — Шаг 3
 * Цель: /static/css/fonts.css доступен через фронт (:5173) и содержит нужные правила.
 * Критерии:
 *  - статус 200
 *  - Content-Type: text/css
 *  - есть @font-face
 *  - есть наши семейства MulishLocal/UrbanistLocal
 *  - есть ссылки на /static/fonts/mulish/*.woff2 и /static/fonts/urbanist/*.woff2
 */
test('step3: /static/css/fonts.css is served and has our @font-face (@step3)', async ({ request }) => {
  // baseURL задан в playwright.config.ts, можно и относительный путь:
  const res = await request.get('/static/css/fonts.css');
  expect(res.ok(), `bad status: ${res.status()}`).toBeTruthy();

  const ct = res.headers()['content-type'] || res.headers()['Content-Type'];
  expect(ct && ct.includes('text/css')).toBeTruthy();

  const css = await res.text();

  // Базовые признаки
  expect(css.includes('@font-face')).toBeTruthy();
  expect(css.includes("font-family: 'MulishLocal'")).toBeTruthy();
  expect(css.includes("font-family: 'UrbanistLocal'")).toBeTruthy();

  // Ссылки на файлы шрифтов (woff2)
  expect(/\/static\/fonts\/mulish\/.+\.woff2/.test(css)).toBeTruthy();
  expect(/\/static\/fonts\/urbanist\/.+\.woff2/.test(css)).toBeTruthy();
});

/**
 * Пайплайн шрифтов — Шаг 4
 * Цель: убедиться, что /static/css/fonts.css через :5173 и :8000 идентичны (прокси Vite → Django работает).
 * Критерии:
 *  - оба ответа 200 и Content-Type: text/css
 *  - совпадают SHA-256 содержимого (один и тот же файл)
 *
 * ВАЖНО: перед запуском этого шага должен быть запущен backend на :8000.
 */

test('step4: :5173/static/css/fonts.css equals :8000 one (@step4)', async ({ request }) => {
  // 1) Получаем css через :5173 (Vite)
  const resDev = await request.get('/static/css/fonts.css');
  expect(resDev.ok(), `dev status: ${resDev.status()}`).toBeTruthy();

  const ctDev = resDev.headers()['content-type'] ?? resDev.headers()['Content-Type'] ?? '';
  expect(ctDev.includes('text/css')).toBeTruthy();

  const cssDev = await resDev.text(); // строка

  // 2) Получаем css напрямую с :8000 (Django)
  const beCtx = await pwRequest.newContext({ baseURL: 'http://127.0.0.1:8000' });
  const resBe = await beCtx.get('/static/css/fonts.css');
  expect(resBe.ok(), `backend status: ${resBe.status()}`).toBeTruthy();

  const ctBe = resBe.headers()['content-type'] ?? resBe.headers()['Content-Type'] ?? '';
  expect(ctBe.includes('text/css')).toBeTruthy();

  const cssBe = await resBe.text(); // строка

  // 3) Сравниваем SHA-256 содержимого
  const sha = (s: string) => createHash('sha256').update(s, 'utf8').digest('hex');
  const hashDev = sha(cssDev);
  const hashBe  = sha(cssBe);

  expect(hashDev, `hash mismatch:\n  dev: ${hashDev}\n  be : ${hashBe}`).toBe(hashBe);
});


/**
 * Пайплайн шрифтов — Шаг 5
 * Цель: все url(...*.woff2) из /static/css/fonts.css отдаются через :5173
 * Критерии:
 *  - нашли ≥1 ссылки на /static/fonts/... .woff2
 *  - для каждой: статус 200, Content-Type = font/woff2 (или application/font-woff2),
 *    есть ненулевой Content-Length
 *
 * ВАЖНО: backend :8000 должен быть запущен (Vite проксирует /static).
 */
test('step5: every font url in fonts.css is served via :5173 (@step5)', async ({ request }) => {
  const res = await request.get('/static/css/fonts.css');
  expect(res.ok(), `bad status for fonts.css: ${res.status()}`).toBeTruthy();
  const css = await res.text();

  // Собираем все ссылки на woff2 внутри fonts.css
  const rx = /url\((?:['"])?(\/static\/fonts\/[^'")]+\.woff2)(?:['"])?\)/g;
  const urls = Array.from(css.matchAll(rx)).map(m => m[1]);
  const uniqueUrls = Array.from(new Set(urls));

  expect(uniqueUrls.length, 'no *.woff2 urls found in fonts.css').toBeGreaterThan(0);
  expect(uniqueUrls.every(u => u.startsWith('/static/fonts/'))).toBeTruthy();

  for (const u of uniqueUrls) {
    const r = await request.get(u);
    expect(r.ok(), `${u} responded ${r.status()}`).toBeTruthy();

    const ct = (r.headers()['content-type'] ?? '').toLowerCase();
    // некоторые dev-сервера могут отдавать octet-stream — допустим как запасной вариант
    expect(
      ct.includes('font/woff2') || ct.includes('application/font-woff2') || ct.includes('application/octet-stream')
    ).toBeTruthy();

    const len = Number(r.headers()['content-length'] ?? 0);
    expect(len, `${u} has empty content`).toBeGreaterThan(0);
  }
});


/**
 * Пайплайн шрифтов — Шаг 6
 * Цель: все *.woff2 из fonts.css доступны напрямую на :8000 (Django staticfiles).
 * Критерии:
 *  - для каждой ссылки: статус 200, корректный content-type, ненулевой размер
 *
 * ВАЖНО: backend на :8000 должен быть запущен.
 */
test('step6: every font url from fonts.css is served via :8000 (@step6)', async ({ request }) => {
  // 1) Берём fonts.css с :5173 (чтобы получить список ссылок)
  const resDev = await request.get('/static/css/fonts.css');
  expect(resDev.ok(), `bad status for fonts.css on :5173: ${resDev.status()}`).toBeTruthy();
  const css = await resDev.text();

  // 2) Достаём все url(...*.woff2) и убираем дубли
  const rx = /url\((?:['"])?(\/static\/fonts\/[^'")]+\.woff2)(?:['"])?\)/g;
  const urls = Array.from(css.matchAll(rx)).map(m => m[1]);
  const uniqueUrls = Array.from(new Set(urls));
  expect(uniqueUrls.length, 'no *.woff2 urls found in fonts.css').toBeGreaterThan(0);

  // 3) Проверяем каждый файл напрямую через :8000
  const be = await (await import('@playwright/test')).request.newContext({ baseURL: 'http://127.0.0.1:8000' });

  for (const u of uniqueUrls) {
    const r = await be.get(u);
    expect(r.ok(), `${u} on :8000 responded ${r.status()}`).toBeTruthy();

    const ct = (r.headers()['content-type'] ?? '').toLowerCase();
    expect(
      ct.includes('font/woff2') || ct.includes('application/font-woff2') || ct.includes('application/octet-stream')
    ).toBeTruthy();

    const len = Number(r.headers()['content-length'] ?? 0);
    expect(len, `${u} on :8000 has empty content`).toBeGreaterThan(0);
  }
});

/**
 * Пайплайн шрифтов — Шаг 7 (устойчивый)
 * Проверяем, что страница реально использует наши семейства и нужные веса:
 *  - обычный текст → MulishLocal (семейство + загрузка 400)
 *  - заголовок     → UrbanistLocal (семейство + загрузка ФАКТИЧЕСКОГО веса)
 */
test('step7: page uses MulishLocal for text and UrbanistLocal for headings (@step7)', async ({ page }) => {
  await page.goto('/my-club/players', { waitUntil: 'domcontentloaded' });

  // 1) Берём видимые узлы: любой MUI-текст и любой заголовок/титул карточки
  const textNode = page.locator('.MuiTypography-root').first();
  await textNode.waitFor({ state: 'visible', timeout: 15000 });

  const headingNode = page.locator('.MuiCardHeader-title, [role="heading"], h1, h2, h3, h4, h5, h6').first();
  await headingNode.waitFor({ state: 'visible', timeout: 15000 });

  // 2) Проверяем семейства по факту
  const famText = (await textNode.evaluate(el => getComputedStyle(el as Element).fontFamily)).toLowerCase();
  expect(famText.includes('mulishlocal')).toBeTruthy();

  const famHeading = (await headingNode.evaluate(el => getComputedStyle(el as Element).fontFamily)).toLowerCase();
  expect(famHeading.includes('urbanistlocal')).toBeTruthy();

  // 3) Фактический вес заголовка из вычисленных стилей
  const weightStr = await headingNode.evaluate(el => getComputedStyle(el as Element).fontWeight);
  const map: Record<string, number> = { normal: 400, bold: 700, bolder: 700, lighter: 300 };
  const parsed = Number(weightStr);
  const weightNum = Number.isFinite(parsed) ? parsed : (map[weightStr as keyof typeof map] ?? 600);

  // 4) Font Loading API: дожидаемся, при необходимости подгружаем нужные веса и проверяем
  const checks = await page.evaluate(async ({ weightNum }) => {
    // @ts-ignore
    await document.fonts.ready;

    // Обычный текст — MulishLocal 400
    // @ts-ignore
    let bodyOk = document.fonts.check('400 16px "MulishLocal"');
    if (!bodyOk) {
      // @ts-ignore
      await document.fonts.load('400 16px "MulishLocal"');
      // @ts-ignore
      bodyOk = document.fonts.check('400 16px "MulishLocal"');
    }

    // Заголовок — UrbanistLocal фактического веса
    const query = `${weightNum} 20px "UrbanistLocal"`;
    // @ts-ignore
    let headOk = document.fonts.check(query);
    if (!headOk) {
      // @ts-ignore
      await document.fonts.load(query);
      // @ts-ignore
      headOk = document.fonts.check(query);
    }

    return { bodyOk, headOk, weightNum };
  }, { weightNum });

  expect(checks.bodyOk, 'MulishLocal 400 not loaded/checked').toBeTruthy();
  expect(checks.headOk,  `UrbanistLocal ${checks.weightNum} not loaded/checked`).toBeTruthy();
});

/**
 * Пайплайн шрифтов — Шаг 8b (функциональная проверка весов)
 * Цель: убедиться, что MulishLocal 400 и 700 действительно доступны и выбираются в DOM.
 * Критерии:
 *  - document.fonts.check для 400 и 700 → true
 *  - getComputedStyle(...).fontWeight для span[400] = 400, для span[700] = 700
 *  - font-family у обоих содержит MulishLocal
 */
test('step8b: MulishLocal 400 и 700 действительно доступны и выбираются (@step8b)', async ({ page }) => {
  await page.goto('/my-club/players', { waitUntil: 'domcontentloaded' });

  const result = await page.evaluate(async () => {
    // @ts-ignore
    await document.fonts.ready;
    // гарантируем, что нужные экземпляры запросились
    // @ts-ignore
    await Promise.all([
      document.fonts.load('400 24px "MulishLocal"'),
      document.fonts.load('700 24px "MulishLocal"'),
    ]);

    // Проверка через Font Loading API
    // @ts-ignore
    const api400 = document.fonts.check('400 24px "MulishLocal"');
    // @ts-ignore
    const api700 = document.fonts.check('700 24px "MulishLocal"');

    // Создаём два DOM-элемента и меряем вычисленные стили
    const mk = (w: number) => {
      const s = document.createElement('span');
      s.textContent = 'Weight check';
      s.style.position = 'absolute';
      s.style.left = '-99999px';
      s.style.top = '0';
      s.style.fontFamily = 'MulishLocal, ui-sans-serif';
      s.style.fontSize = '24px';
      s.style.fontWeight = String(w);
      document.body.appendChild(s);
      const cs = getComputedStyle(s);
      const fam = cs.fontFamily.toLowerCase();
      const wNum = Number(cs.fontWeight);
      s.remove();
      return { fam, wNum };
    };

    const dom400 = mk(400);
    const dom700 = mk(700);

    return { api400, api700, dom400, dom700 };
  });

  // Семейство в DOM действительно MulishLocal
  expect(result.dom400.fam.includes('mulishlocal')).toBeTruthy();
  expect(result.dom700.fam.includes('mulishlocal')).toBeTruthy();

  // Font Loading API подтвердил наличие 400 и 700
  expect(result.api400).toBeTruthy();
  expect(result.api700).toBeTruthy();

  // Вычисленные веса в DOM соответствуют запрошенным (400 и 700)
  expect(result.dom400.wNum).toBe(400);
  expect(result.dom700.wNum).toBe(700);
});



/**
 * Пайплайн шрифтов — Шаг 9
 * Цель: пары woff2 для разных весов — реально разные файлы (по SHA-256).
 */
test('step9: woff2 files for 400 vs 700 (Mulish) и 600 vs 700 (Urbanist) have different hashes (@step9)', async ({ request }) => {
  // вспомогательная функция
  const sha = (buf: string | Buffer) => createHash('sha256').update(buf).digest('hex');

  const fetchHash = async (url: string) => {
    const r = await request.get(url);
    expect(r.ok(), `${url} responded ${r.status()}`).toBeTruthy();
    const buf = await r.body();
    return sha(buf);
  };

  const m400 = await fetchHash('/static/fonts/mulish/mulish-400.woff2');
  const m700 = await fetchHash('/static/fonts/mulish/mulish-700.woff2');
  const u600 = await fetchHash('/static/fonts/urbanist/urbanist-600.woff2');
  const u700 = await fetchHash('/static/fonts/urbanist/urbanist-700.woff2');

  expect(m400 !== m700, `Mulish 400 and 700 woff2 are identical (sha256=${m400})`).toBeTruthy();
  expect(u600 !== u700, `Urbanist 600 and 700 woff2 are identical (sha256=${u600})`).toBeTruthy();
});

/**
 * Пайплайн шрифтов — Шаг 10
 * Цель: при загрузке страницы нет запросов на внешние font-CDN (googleapis/gstatic).
 * Дополнительно: все запросы *.woff2 идут только на /static/fonts/.
 */
test('step10: no external font CDN requests; only /static/fonts/* used (@step10)', async ({ page }) => {
  const externalHits: string[] = [];
  const fontHits: string[] = [];

  page.on('request', (req) => {
    const url = req.url();
    // собираем все шрифтовые запросы
    if (/\.(woff2)(\?|$)/i.test(url)) fontHits.push(url);
    // фиксируем внешние домены
    if (/fonts\.googleapis\.com/i.test(url) || /gstatic\.com/i.test(url)) {
      externalHits.push(url);
    }
  });

  await page.goto('/my-club/players', { waitUntil: 'networkidle' });

  // 1) никаких внешних запросов
  expect(externalHits, 'unexpected external font requests:\n' + externalHits.join('\n')).toHaveLength(0);

  // 2) шрифтовые запросы идут только на /static/fonts/
  const badFonts = fontHits.filter(u => !/\/static\/fonts\//i.test(u));
  expect(badFonts, 'font requests should hit /static/fonts/: \n' + badFonts.join('\n')).toHaveLength(0);
});


/**
 * Служебный дамп типографики со страницы — печатает Markdown-таблицу в консоль.
 */
test('dump: current typography snapshot (@dump)', async ({ page }) => {
  await page.goto('/my-club/players', { waitUntil: 'domcontentloaded' });

  // Помощники
  const readCS = async (locator: string) => {
    const el = page.locator(locator).first();
    if (!(await el.count())) return null;
    await el.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
    return el.evaluate((node) => {
      const cs = getComputedStyle(node as Element);
      const fam = cs.fontFamily;
      const sz  = cs.fontSize;
      const lh  = cs.lineHeight;
      const ls  = cs.letterSpacing;
      const fw  = cs.fontWeight;
      return { fam, sz, lh, ls, fw };
    }).catch(() => null);
  };

  // Где ищем
  const probe = {
    h1: '.MuiTypography-h1, h1',
    h2: '.MuiTypography-h2, h2',
    h3: '.MuiTypography-h3, h3',
    h4: '.MuiTypography-h4, h4',
    h5: '.MuiTypography-h5, h5',
    h6: '.MuiTypography-h6, h6',
    cardTitle: '.MuiCardHeader-title',
    body1: '.MuiTypography-body1',
    body2: '.MuiTypography-body2, .MuiTypography-root',
    button: '.MuiButton-root',
    caption: '.MuiTypography-caption',
    overline: '.MuiTypography-overline'
  };

  const rows: Array<{variant: string, fam: string, fw: string, sz: string, lh: string, ls: string}> = [];

  for (const [variant, sel] of Object.entries(probe)) {
    const cs = await readCS(sel);
    if (!cs) continue;
    rows.push({
      variant,
      fam: cs.fam,
      fw: cs.fw,
      sz: cs.sz,
      lh: cs.lh,
      ls: cs.ls,
    });
  }

  // Печатаем Markdown-таблицу в stdout
  const md = [
    '| Вариант | Семейство | Вес | Размер | Line-height | Letter-spacing |',
    '|---|---|---:|---:|---:|---:|',
    ...rows.map(r => `| ${r.variant} | ${r.fam} | ${r.fw} | ${r.sz} | ${r.lh} | ${r.ls} |`)
  ].join('\n');
  console.log('\n\nCURRENT TYPOGRAPHY\n' + md + '\n');
});

/** 
 * Заглушки для следующих шагов — будем заполнять позже.
 * test('step2: index.html содержит <link href="/static/css/fonts.css">', async () => {});
 * test('step3: запрос /static/css/fonts.css уходит через :5173', async () => {});
 * test('step4: /static проксируется на :8000', async () => {});
 * test('step5: fonts.css ссылается на /static/fonts/... .woff2', async () => {});
 * test('step6: браузер скачивает .woff2 файлы', async () => {});
 * test('step7: Django отдаёт .woff2 с диска C:\\realfootballsim\\static\\fonts', async () => {});
 * test('step8: Rendered Fonts: MulishLocal (400) для текста, UrbanistLocal (600/700) для заголовков', async () => {});
 */

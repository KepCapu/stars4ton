// web/api/price.js
// ВЕРСИЯ: robust — сначала ищем buildId в HTML, затем грузим JSON по Next.js-роуту.
// Возвращает: { price_ton_per_star: <number> }
// Если не удалось — пишет понятное сообщение об ошибке.

const HTML_URL = "https://fragment.com/stars/buy";

function pickPriceFromJson(obj) {
  // Рекурсивный обход объекта с первичным приоритетом по ключам
  // "price", "rate", "cost" и здравым диапазонам (0 < v < 1 TON за 1 star).
  let found = null;

  const visit = (x) => {
    if (found !== null || !x || typeof x !== "object") return;
    for (const [k, v] of Object.entries(x)) {
      if (found !== null) break;

      if (typeof v === "number" && isFinite(v)) {
        const key = k.toLowerCase();
        const looksLikePriceKey =
          key.includes("price") || key.includes("rate") || key.includes("cost");
        const inPlausibleRange = v > 0 && v < 1; // обычно ~0.006.. TON
        if (looksLikePriceKey && inPlausibleRange) {
          found = v;
          break;
        }
      } else if (typeof v === "object") {
        visit(v);
      }
    }
  };

  visit(obj);
  return found;
}

export default async function handler(req, res) {
  try {
    // 1) Загружаем HTML, маскируемся под обычный браузер
    const rsp = await fetch(HTML_URL, {
      headers: {
        "user-agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "accept-language": "en-US,en;q=0.9,ru;q=0.8",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://fragment.com/",
      },
    });

    if (!rsp.ok) {
      return res
        .status(502)
        .json({ error: `upstream ${HTML_URL} status ${rsp.status}` });
    }

    const html = await rsp.text();

    // 2) Сначала пробуем Next.js buildId, чтобы получить чистый JSON
    const mBuild = html.match(/"buildId"\s*:\s*"([a-zA-Z0-9\-_]+)"/);
    if (mBuild && mBuild[1]) {
      const buildId = mBuild[1];
      const dataUrl = `https://fragment.com/_next/data/${buildId}/stars/buy.json`;

      const jsonRsp = await fetch(dataUrl, {
        headers: {
          "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
          "accept": "application/json",
          "cache-control": "no-cache",
          "pragma": "no-cache",
          "referer": HTML_URL,
        },
      });

      if (jsonRsp.ok) {
        const data = await jsonRsp.json();
        const price = pickPriceFromJson(data);
        if (typeof price === "number") {
          res.setHeader("content-type", "application/json; charset=utf-8");
          return res.status(200).json({ price_ton_per_star: Number(price) });
        }
      }
      // если JSON не дал результата — провалимся на резервный парсер ниже
    }

    // 3) Резервный путь: попробовать вытащить inline-JSON (__NEXT_DATA__) из HTML
    const mInline =
      html.match(
        /<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/i
      ) || [];
    if (mInline[1]) {
      try {
        const nextData = JSON.parse(mInline[1]);
        const price = pickPriceFromJson(nextData);
        if (typeof price === "number") {
          res.setHeader("content-type", "application/json; charset=utf-8");
          return res.status(200).json({ price_ton_per_star: Number(price) });
        }
      } catch (e) {
        // JSON парс не удался — идём к ошибке
      }
    }

    // 4) Если обе стратегии не дали результата — сообщим, что не нашли цену
    return res.status(500).json({ error: "price field not found" });
  } catch (e) {
    return res.status(500).json({
      error:
        e && e.message ? String(e.message) : typeof e === "string" ? e : "unknown",
    });
  }
}

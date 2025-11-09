// web/api/price.js
// Vercel Node.js API Route. Возвращает { price_ton_per_star } из Fragment.

export default async function handler(req, res) {
  try {
    const rsp = await fetch("https://fragment.com/stars/buy", {
      headers: {
        "user-agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept-language": "en-US,en;q=0.9,ru;q=0.8",
      },
    });
    if (!rsp.ok) throw new Error(`Upstream status ${rsp.status}`);
    const html = await rsp.text();

    const m =
      html.match(
        /<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/i
      ) || [];
    if (!m[1]) throw new Error("NEXT_DATA not found");

    const nextData = JSON.parse(m[1]);

    let found = null;
    const visit = (obj) => {
      if (!obj || typeof obj !== "object" || found !== null) return;
      for (const [k, v] of Object.entries(obj)) {
        if (found !== null) break;
        if (typeof v === "number") {
          if (/price|rate|cost/i.test(k)) {
            found = v;
            break;
          }
        } else if (typeof v === "object") {
          visit(v);
        }
      }
    };
    visit(nextData);

    if (typeof found !== "number" || !isFinite(found)) {
      throw new Error("price field not found");
    }

    res.setHeader("content-type", "application/json; charset=utf-8");
    res.status(200).json({ price_ton_per_star: Number(found) });
  } catch (e) {
    res
      .status(500)
      .json({ error: String(e && e.message ? e.message : e || "unknown") });
  }
}

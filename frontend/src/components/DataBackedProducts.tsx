"use client";

import { useEffect, useState } from "react";
import { getProductScorecard, Product, ProductScoreResponse, searchProducts } from "@/lib/api";
import { ProductScanner } from "@/components/ProductScanner";
import { useProfile } from "@/components/ProfileProvider";

function ProductImage({ product, large = false }: { product: Product; large?: boolean }) {
  return product.image_url ? (
    <img className={large ? "product-record-image large" : "product-record-image"} src={product.image_url} alt={`${product.product_name} package`} loading="lazy" />
  ) : <div className={large ? "product-record-image fallback large" : "product-record-image fallback"}>Product image unavailable</div>;
}

function AlternativeCard({ swap }: { swap: NonNullable<ProductScoreResponse["scorecard"]>["healthy_swaps"][number] }) {
  return <article className="alternative-card">
    <ProductImage product={swap.product} />
    <div className="alternative-copy"><p className="eyebrow">{swap.product.brand || swap.product.category || "Database alternative"}</p><h4>{swap.product.product_name}</h4><p>Jivanya Health Score: <strong>{swap.score}/100 · Grade {swap.grade}</strong></p><div className="alternative-differences">{swap.highlights.map(highlight => <span key={highlight}>{highlight}</span>)}</div></div>
  </article>;
}

export function DataBackedProducts() {
  const { profile } = useProfile();
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [selected, setSelected] = useState<ProductScoreResponse | null>(null);
  const [scanner, setScanner] = useState(false);
  const [error, setError] = useState("");

  async function search() {
    setError("");
    try { setProducts((await searchProducts({ query, limit: 30, offset: 0 })).items); }
    catch (err) { setProducts([]); setError(err instanceof Error ? err.message : "Product database unavailable"); }
  }
  useEffect(() => { void search(); }, []);
  async function openScore(product: Product) {
    try { setSelected(await getProductScorecard(product.barcode, { allergies: profile?.allergies.join(","), exclusions: profile?.exclusions.join(","), diet: profile?.dietPreference !== "no preference" ? profile?.dietPreference : undefined })); }
    catch (err) { setError(err instanceof Error ? err.message : "Product record unavailable"); }
  }

  return <section className="product-workspace">
    <div className="page-title"><p className="eyebrow">Packaged food intelligence</p><h2>Look closer at <em>what’s in the pack.</em></h2><p>Browse real product records, inspect stored nutrition, and compare deterministic Jivanya alternatives.</p></div>
    <div className="toolbar"><input className="input search-input" value={query} onChange={event => setQuery(event.target.value)} onKeyDown={event => { if (event.key === "Enter") void search(); }} placeholder="Search product names"/><button className="button button-secondary" onClick={() => void search()}>Search</button><button className="button button-primary" onClick={() => setScanner(true)}>Scan barcode</button></div>
    {error && <p className="form-message">{error}</p>}
    {scanner && <ProductScanner onClose={() => setScanner(false)} />}
    {selected && <section className="card product-detail"><div className="product-detail-heading"><ProductImage product={selected.product} large /><div><p className="eyebrow">{selected.product.brand || "Product record"}</p><h3>{selected.product.product_name}</h3><p>{selected.product.category || "Category not listed"} · Barcode {selected.product.barcode}</p></div><button className="outline-link" onClick={() => setSelected(null)}>Close ×</button></div><p className="product-score-line"><strong>Jivanya Health Score {selected.scorecard.score}/100</strong> · Grade {selected.scorecard.grade}</p><p>{selected.scorecard.summary}</p><div className="stored-nutrition"><strong>Stored nutrition per 100g</strong><span>Energy {selected.product.energy_100g ?? "—"} kcal</span><span>Protein {selected.product.protein_100g ?? "—"}g</span><span>Sugar {selected.product.sugars_100g ?? "—"}g</span><span>Saturated fat {selected.product.saturated_fat_100g ?? "—"}g</span><span>Sodium {selected.product.sodium_100g != null ? `${selected.product.sodium_100g}mg` : "—"}</span></div>{selected.scorecard.rule_warnings.length > 0 && <div className="product-rules"><h4>Jivanya product rules</h4>{selected.scorecard.rule_warnings.map(warning => <p key={warning.code}>{warning.label}: {warning.description}</p>)}</div>}{selected.scorecard.healthy_swaps.length > 0 && <div className="alternatives-section"><h3>Alternatives to {selected.product.product_name}</h3><p>These are real products in the same category with a higher deterministic Jivanya score.</p><div className="alternative-grid">{selected.scorecard.healthy_swaps.map(swap => <AlternativeCard key={swap.product.barcode} swap={swap} />)}</div></div>}</section>}
    <div className="product-grid">{products.map(product => <article className="product-card" key={product.barcode}><ProductImage product={product} /><div className="product-body"><p className="eyebrow">{product.brand || product.category || "Product record"}</p><h3>{product.product_name}</h3><p>{product.category || "Category not listed"}</p><p>{product.energy_100g ?? "—"} kcal · {product.sugars_100g ?? "—"}g sugar per 100g</p><button className="outline-link" onClick={() => void openScore(product)}>View product intelligence →</button></div></article>)}</div>
  </section>;
}

import Image from "next/image";
import Link from "next/link";

export function Brand({ compact = false }: { compact?: boolean }) {
  return <Link className={`brand-link${compact ? " brand-link-compact" : ""}`} href="/" aria-label="Jivanya home"><Image className="brand-image" src="/brand/jivanya-wordmark.png" alt="Jivanya" width={720} height={378} priority /></Link>;
}

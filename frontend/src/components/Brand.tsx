import Image from "next/image";
import Link from "next/link";

export function Brand({ compact = false }: { compact?: boolean }) {
  const size = compact ? 400 : 88;
  return <Link className={`brand-link${compact ? " brand-link-compact" : ""}`} href="/" aria-label="Jivanya home"><Image className="brand-image" src="/brand/jivanya-logo.jpeg" alt="Jivanya" width={size} height={size} priority /></Link>;
}

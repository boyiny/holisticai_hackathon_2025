import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

# Allow importing from repo root (for core.valyu_tools)
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from core.valyu_tools import ValyuRetriever
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Failed to import Valyu tools. Ensure repository root is on PYTHONPATH and dependencies are installed."
    ) from e


def _load_lines_file(path: Optional[str]) -> List[str]:
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    items: List[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        items.append(s)
    return items


def _canonical_domain(s: str) -> str:
    # Accept either plain domain or URL; return netloc without www.
    # Examples: nhs.uk -> nhs.uk, https://www.nhs.uk/path -> nhs.uk
    try:
        from urllib.parse import urlparse
        if "://" in s:
            netloc = urlparse(s).netloc
        else:
            netloc = s
        netloc = netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return s.lower()


def _domain_from_url(url: str) -> Optional[str]:
    try:
        from urllib.parse import urlparse
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return None


def _extract_urls(text: str) -> List[str]:
    if not text:
        return []
    # Simple URL regex
    pattern = re.compile(r"https?://[^\s)\]]+")
    return pattern.findall(text)


@dataclass
class QueryEvalResult:
    query: str
    include_sources: List[str]
    canonical_whitelist: List[str]
    retrieved_urls: List[str]
    retrieved_domains: List[str]
    non_whitelisted_domains: List[str]
    notes: Optional[str] = None
    answer: Optional[str] = None
    cited_urls_in_answer: Optional[List[str]] = None
    non_whitelisted_in_answer: Optional[List[str]] = None


def run_whitelisted_search(
    query: str,
    include_sources: List[str],
    k: int = 10,
    country: Optional[str] = None,
    fast_mode: bool = False,
    valyu_api_key: Optional[str] = None,
    ) -> Tuple[List[str], List[str]]:
    retriever = ValyuRetriever(
        k=k,
        search_type="all",
        included_sources=include_sources,
        country_code=country,
        fast_mode=fast_mode,
        valyu_api_key=valyu_api_key,
    )
    # Modern LangChain retrievers are Runnables; use .invoke() to fetch docs.
    docs = retriever.invoke(query)
    urls = [d.metadata.get("url") for d in docs if d.metadata.get("url")]
    domains = [_domain_from_url(u) or "" for u in urls]
    return urls, domains


def judge_whitelist_compliance(
    retrieved_domains: List[str],
    whitelist: List[str],
) -> List[str]:
    wl = {_canonical_domain(d) for d in whitelist}
    out_of_whitelist = []
    for d in retrieved_domains:
        cd = _canonical_domain(d)
        if cd and cd not in wl:
            out_of_whitelist.append(cd)
    return sorted(list(dict.fromkeys(out_of_whitelist)))


def judge_answer_sources(answer: str, whitelist: List[str]) -> Tuple[List[str], List[str]]:
    cited = _extract_urls(answer)
    cited_domains = [d for d in [_domain_from_url(u) for u in cited] if d]
    non_wl = judge_whitelist_compliance(cited_domains, whitelist)
    return cited, non_wl


def main():
    p = argparse.ArgumentParser(description="Whitelisted grounding eval using Valyu search")
    g_in = p.add_argument_group("Inputs")
    g_in.add_argument("--query", help="Single query to run")
    g_in.add_argument("--queries-file", help="Path to file with one query per line")

    g_src = p.add_argument_group("Sources")
    g_src.add_argument("--include-sources", nargs="*", default=[], help="List of domains or URLs to whitelist")
    g_src.add_argument("--whitelist-file", help="File with domains/URLs, one per line")
    g_src.add_argument("--country", help="2-letter ISO country code, e.g., uk or us")

    g_cfg = p.add_argument_group("Config")
    g_cfg.add_argument("--k", type=int, default=10, help="Max documents to retrieve")
    g_cfg.add_argument("--fast", action="store_true", help="Enable Valyu fast mode")
    g_cfg.add_argument("--valyu-api-key", help="Valyu API key (overrides VALYU_API_KEY env)")

    g_ans = p.add_argument_group("Answer Judging (optional)")
    g_ans.add_argument("--answer-text", help="Answer text to judge for whitelist source compliance")

    g_out = p.add_argument_group("Output")
    g_out.add_argument("--output", help="Path to save JSON report (default under data/evals)")

    args = p.parse_args()

    queries: List[str] = []
    if args.query:
        queries.append(args.query)
    if args.queries_file:
        queries.extend(_load_lines_file(args.queries_file))
    if not queries:
        p.error("Provide --query or --queries-file")

    whitelist = []
    whitelist.extend(args.include_sources or [])
    whitelist.extend(_load_lines_file(args.whitelist_file))
    if not whitelist:
        p.error("Provide --include-sources or --whitelist-file with allowed domains/URLs")

    # Normalize whitelist for reporting
    canonical_wl = sorted(list({
        _canonical_domain(s) if "://" in s or "." in s else s for s in whitelist
    }))

    api_key = args.valyu_api_key or os.getenv("VALYU_API_KEY")
    if not api_key:
        print("⚠️  VALYU_API_KEY not set; requests may fail.", file=sys.stderr)

    results: List[QueryEvalResult] = []
    for q in queries:
        urls, domains = run_whitelisted_search(
            q,
            include_sources=whitelist,
            k=args.k,
            country=(args.country.upper() if args.country else None),
            fast_mode=bool(args.fast),
            valyu_api_key=api_key,
        )

        non_wl = judge_whitelist_compliance(domains, canonical_wl)
        rec = QueryEvalResult(
            query=q,
            include_sources=whitelist,
            canonical_whitelist=canonical_wl,
            retrieved_urls=urls,
            retrieved_domains=[d for d in domains if d],
            non_whitelisted_domains=non_wl,
        )

        if args.answer_text:
            cited, non_wl_ans = judge_answer_sources(args.answer_text, canonical_wl)
            rec.answer = args.answer_text
            rec.cited_urls_in_answer = cited
            rec.non_whitelisted_in_answer = non_wl_ans

        results.append(rec)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = (
        Path(args.output)
        if args.output
        else REPO_ROOT / "data" / "evals" / f"whitelist_grounding_{ts}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "created_at": ts,
        "tool": "valyu",
        "k": args.k,
        "country": args.country,
        "fast_mode": bool(args.fast),
        "results": [asdict(r) for r in results],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()


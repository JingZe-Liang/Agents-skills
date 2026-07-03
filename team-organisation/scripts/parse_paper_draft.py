#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


NUMBERED_RE = re.compile(r"(?m)^\s*(\d+)\.\s*(.*)$")
URL_RE = re.compile(r"https?://[^\s,}）]+")
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})(?:v\d+)?", re.I)
EPRINT_RE = re.compile(r"eprint\s*=\s*[{'\"]([^}'\"]+)[}'\"]", re.I)
TITLE_RE = re.compile(r"title\s*=\s*[{'\"](.+?)[}'\"]\s*,?", re.I | re.S)
YEAR_RE = re.compile(r"year\s*=\s*[{'\"]?([0-9]{4})[}'\"]?", re.I)
DOI_RE = re.compile(r"doi\s*=\s*[{'\"]([^}'\"]+)[}'\"]", re.I)
BIBKEY_RE = re.compile(r"@\w+\s*{\s*([^,\s]+)", re.I)


def clean_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(URL_RE, "", text).strip(" ：:")
    text = text.replace("{", "").replace("}", "")
    return text.strip()


def extract_entry_fields(raw: str) -> dict[str, object]:
    title_match = TITLE_RE.search(raw)
    year_match = YEAR_RE.search(raw)
    doi_match = DOI_RE.search(raw)
    key_match = BIBKEY_RE.search(raw)
    urls = URL_RE.findall(raw)
    arxiv_ids = []
    for url in urls:
        arxiv_ids.extend(ARXIV_RE.findall(url))
    eprint_match = EPRINT_RE.search(raw)
    if eprint_match and re.match(r"^\d{4}\.\d{4,5}$", eprint_match.group(1)):
        arxiv_ids.append(eprint_match.group(1))
    seen = set()
    arxiv_ids = [x for x in arxiv_ids if not (x in seen or seen.add(x))]
    title = clean_title(title_match.group(1)) if title_match else clean_title(raw.splitlines()[0])
    return {
        "title": title,
        "year": year_match.group(1) if year_match else "",
        "doi": doi_match.group(1) if doi_match else "",
        "bibtex_key": key_match.group(1) if key_match else "",
        "urls": urls,
        "arxiv_ids": arxiv_ids,
    }


def len_numbered_entry(text: str, body_start: int) -> int:
    body = text[body_start:]
    body_stripped = body.lstrip()
    offset = body_start + (len(body) - len(body_stripped))
    if body_stripped.startswith("@"):
        depth = 0
        end = offset
        while end < len(text):
            ch = text[end]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return end + 1
            end += 1
    newline = text.find("\n", body_start)
    return len(text) if newline < 0 else newline


def split_numbered_entries(text: str) -> list[dict[str, object]]:
    matches = list(NUMBERED_RE.finditer(text))
    entries: list[dict[str, object]] = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len_numbered_entry(text, match.start(2))
        raw = text[start:end].strip()
        body = raw.split(".", 1)[1].strip()
        fields = extract_entry_fields(body)
        entries.append({"source_id": str(int(match.group(1))), "source_kind": "numbered", "raw": raw, **fields})
    return entries


def split_unnumbered_tail(text: str, existing_end: int) -> list[dict[str, object]]:
    tail = text[existing_end:]
    entries: list[dict[str, object]] = []
    pos = 0
    item = 64
    while pos < len(tail):
        bib = re.search(r"@\w+\s*{", tail[pos:])
        url = re.search(URL_RE, tail[pos:])
        candidates = [(m.start(), "bib", m) for m in [bib] if m] + [(m.start(), "url", m) for m in [url] if m]
        if not candidates:
            break
        offset, kind, match = min(candidates, key=lambda x: x[0])
        start = pos + offset
        if kind == "bib":
            depth = 0
            end = start
            while end < len(tail):
                ch = tail[end]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end += 1
                        break
                end += 1
            raw = tail[start:end].strip()
            fields = extract_entry_fields(raw)
            entries.append({"source_id": f"extra-{item}", "source_kind": "bibtex-extra", "raw": raw, **fields})
            item += 1
            pos = end
        else:
            raw = match.group(0).strip()
            fields = extract_entry_fields(raw)
            entries.append({"source_id": f"extra-{item}", "source_kind": "url-extra", "raw": raw, **fields})
            item += 1
            pos = start + len(raw)
    return entries


def split_plain_title_entries(text: str, existing_end: int, start_item: int = 1) -> list[dict[str, object]]:
    tail = text[existing_end:]
    entries: list[dict[str, object]] = []
    item = start_item
    for line in tail.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or raw.startswith("@") or URL_RE.fullmatch(raw):
            continue
        if re.match(r"^\s*[-*]\s+", raw):
            raw = re.sub(r"^\s*[-*]\s+", "", raw).strip()
        fields = extract_entry_fields(raw)
        if fields["title"]:
            entries.append({"source_id": f"plain-{item}", "source_kind": "plain-title", "raw": raw, **fields})
            item += 1
    return entries


def parse_draft(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    matches = list(NUMBERED_RE.finditer(text))
    if not matches:
        entries = split_unnumbered_tail(text, 0)
        covered = "\n".join(str(entry["raw"]) for entry in entries)
        plain_source = text
        for entry in entries:
            plain_source = plain_source.replace(str(entry["raw"]), "")
        entries.extend(split_plain_title_entries(plain_source, 0))
    else:
        numbered = split_numbered_entries(text)
        last = numbered[-1]["raw"]
        last_start = text.rfind(str(last))
        extra_start = last_start + len(str(last)) if last_start >= 0 else matches[-1].end()
        entries = numbered + split_unnumbered_tail(text, extra_start)
        entries.extend(split_plain_title_entries(text, extra_start, start_item=len(entries) + 1))

    title_to_indices: defaultdict[str, list[int]] = defaultdict(list)
    arxiv_to_indices: defaultdict[str, list[int]] = defaultdict(list)
    for idx, entry in enumerate(entries):
        title = str(entry.get("title") or "").lower()
        if title:
            title_to_indices[title].append(idx)
        for aid in entry.get("arxiv_ids", []):
            arxiv_to_indices[str(aid)].append(idx)

    for entry in entries:
        entry["status"] = "todo"
        entry["target_category"] = ""
        entry["verified_source"] = ""
        entry["duplicate_of"] = ""

    for groups in (title_to_indices, arxiv_to_indices):
        for indices in groups.values():
            if len(indices) <= 1:
                continue
            first = entries[indices[0]]["source_id"]
            for idx in indices[1:]:
                entries[idx]["status"] = "duplicate"
                entries[idx]["duplicate_of"] = first
    return entries


def write_ledger(entries: list[dict[str, object]], output: Path, json_output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    raw_count = len(entries)
    duplicate_count = sum(1 for e in entries if e["status"] == "duplicate")
    lines = [
        "# Paper Crawl Ledger",
        "",
        "## Reconciliation",
        "",
        f"- raw_input_item_count: {raw_count}",
        f"- parsed_candidate_count: {raw_count}",
        f"- duplicate_count: {duplicate_count}",
        "- verified_category_file_count: 0",
        "- problem_list_count: 0",
        f"- total_accounted_count: {duplicate_count}",
        "",
        "## Entries",
        "",
    ]
    for entry in entries:
        lines.extend(
            [
                f"### {entry['source_id']} {entry.get('title') or '(title pending)'}",
                "",
                f"- status: {entry['status']}",
                f"- duplicate_of: {entry.get('duplicate_of') or ''}",
                f"- source_kind: {entry['source_kind']}",
                f"- year: {entry.get('year') or ''}",
                f"- arxiv_ids: {', '.join(entry.get('arxiv_ids', []))}",
                f"- doi: {entry.get('doi') or ''}",
                f"- urls: {', '.join(entry.get('urls', []))}",
                f"- target_category: {entry.get('target_category') or ''}",
                f"- verified_source: {entry.get('verified_source') or ''}",
                "",
            ]
        )
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    json_output.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()
    entries = parse_draft(args.draft)
    write_ledger(entries, args.ledger, args.json)
    print(f"parsed {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

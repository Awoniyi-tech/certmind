import json
import re
import uuid
from pathlib import Path
from typing import Optional


async def extract_questions_from_pdf(
    pdf_path: Path,
    cert_id:  str,
    bank_id:  str,
) -> list[dict]:
    text = _extract_text(pdf_path)
    if not text:
        return []

    questions = _parse_questions(text, cert_id, bank_id)
    return questions


def _extract_text(pdf_path: Path) -> str:
    try:
        import fitz
        doc   = fitz.open(str(pdf_path))
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages)
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf")


def _parse_questions(text: str, cert_id: str, bank_id: str) -> list[dict]:
    question_blocks = _split_into_blocks(text)
    questions       = []

    for block in question_blocks:
        q = _parse_block(block, cert_id, bank_id)
        if q:
            questions.append(q)

    return questions


def _split_into_blocks(text: str) -> list[str]:
    pattern = re.compile(
        r"(?=(?:^|\n)\s*(?:Q\.?\s*)?(\d{1,3})[\.)\s])",
        re.MULTILINE,
    )
    blocks = pattern.split(text)

    result = []
    i = 0
    while i < len(blocks):
        if re.match(r"^\d{1,3}$", blocks[i].strip()):
            # blocks[i] is just the captured number from the lookahead's capture
            # group. The lookahead is zero-width, so it never consumed any text —
            # meaning blocks[i+1] already starts with that same number naturally
            # (e.g. "599. When configuring..."). Appending blocks[i] on top of it
            # duplicated the number (producing "599599. When configuring...").
            if i + 1 < len(blocks):
                block_text = blocks[i + 1]
                i += 2
            else:
                block_text = ""
                i += 1
            if len(block_text.strip()) > 20:
                result.append(block_text)
        else:
            i += 1

    if not result:
        result = [text]

    return result


def _parse_block(block: str, cert_id: str, bank_id: str) -> Optional[dict]:
    lines = [l.strip() for l in block.split("\n") if l.strip()]
    if len(lines) < 3:
        return None

    options    = []
    answer_key = None
    question_lines = []
    found_options  = False

    for line in lines:
        opt_match = re.match(r"^([A-D])[\.)\s]\s*(.+)", line)
        if opt_match:
            found_options = True
            options.append(f"{opt_match.group(1)}. {opt_match.group(2)}")
            continue

        ans_match = re.match(
            r"(?:Answer|Ans|Correct)[:\s]*([A-D](?:[,\s]+[A-D])*)",
            line, re.IGNORECASE
        )
        if ans_match:
            keys = re.findall(r"[A-D]", ans_match.group(1))
            answer_key = keys if len(keys) > 1 else keys[0] if keys else None
            continue

        if not found_options:
            question_lines.append(line)

    question_text = " ".join(question_lines).strip()
    question_text = re.sub(r"^\d{1,3}[\.)\s]+", "", question_text).strip()

    if not question_text or len(options) < 2:
        return None

    q_type = _detect_type(question_text, options, answer_key)
    topic  = _detect_topic(question_text)

    return {
        "id":         str(uuid.uuid4()),
        "bank_id":    bank_id,
        "cert_id":    cert_id,
        "type":       q_type,
        "topic":      topic,
        "question":   question_text,
        "options":    options,
        "answer_key": answer_key or "A",
        "difficulty": "medium",
    }


def _detect_type(question: str, options: list[str], answer_key) -> str:
    if isinstance(answer_key, list) and len(answer_key) > 1:
        return "multiple"

    q_lower = question.lower()
    if any(kw in q_lower for kw in ["true or false", "true/false", "yes or no"]):
        return "truefalse"

    if len(options) == 2:
        opts = [o.lower() for o in options]
        if any("true" in o or "false" in o for o in opts):
            return "truefalse"

    if "select all" in q_lower or "which of the following are" in q_lower:
        return "multiple"

    return "single"


def _detect_topic(question: str) -> str:
    topics = {
        "OSPF":  ["ospf", "designated router", "dr/bdr", "lsa", "area", "hello packet", "spf"],
        "BGP":   ["bgp", "autonomous system", "as-path", "med", "local_pref", "route reflector", "ibgp", "ebgp"],
        "MPLS":  ["mpls", "label", "lsp", "ldp", "rsvp", "vpn", "vrf"],
        "VLAN":  ["vlan", "trunk", "access port", "802.1q", "trunking"],
        "STP":   ["stp", "spanning tree", "bpdu", "root bridge", "rstp", "mstp"],
        "VRRP":  ["vrrp", "virtual router", "master", "backup"],
        "ACL":   ["acl", "access control", "permit", "deny", "traffic policy"],
        "NAT":   ["nat", "network address translation", "pat", "napt"],
        "IPv6":  ["ipv6", "ndp", "slaac", "icmpv6", "prefix"],
        "QoS":   ["qos", "dscp", "cos", "traffic shaping", "priority queue"],
        "IS-IS": ["is-is", "isis", "intermediate system"],
        "DHCP":  ["dhcp", "ip address assignment", "dhcp relay"],
    }

    q_lower = question.lower()
    for topic, keywords in topics.items():
        if any(kw in q_lower for kw in keywords):
            return topic

    return "General"
# numtriad/cli/main.py

import argparse
from typing import List

from ..config import NumTriadConfig
from ..encoders.numtriad_text_v2 import NumTriadTextEncoderV2
from ..rag.triad_rag import TriadRAGEngine
from ..triad_types import Triad


def cmd_embed(args: argparse.Namespace) -> None:
    cfg = NumTriadConfig()
    encoder = NumTriadTextEncoderV2(cfg)
    texts: List[str] = args.texts
    res = encoder.encode(texts)
    for t, triad in zip(texts, res.triads):
        print("TEXT:", t)
        print("TRIAD:", triad)
        print("-" * 40)


def cmd_rag(args: argparse.Namespace) -> None:
    cfg = NumTriadConfig()
    engine = TriadRAGEngine(cfg)

    # index demo
    docs = [
        "L'intelligence artificielle est un champ de recherche théorique.",
        "Ce tutoriel montre comment déployer un modèle en production.",
        "Voici un exemple de code pour effectuer une requête API.",
        "Une vue d'ensemble des concepts de machine learning.",
    ]
    ids = [f"doc_{i}" for i in range(len(docs))]
    engine.index(ids, docs)

    query = args.query
    print("Query:", query)

    bias = None
    if args.abstract:
        bias = Triad(delta=0.1, infinity=0.8, theta=0.1)
    elif args.concrete:
        bias = Triad(delta=0.1, infinity=0.1, theta=0.8)

    results = engine.search(query, k=args.k, triad_bias=bias)
    for doc, score in results:
        print(f"[{doc.doc_id}] score={score:.3f} triad={doc.triad}")
        print(" ", doc.text)
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(prog="numtriad", description="NumTriad CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # embed
    p_embed = sub.add_parser("embed", help="Afficher triade de textes")
    p_embed.add_argument("texts", nargs="+", help="Textes à analyser")
    p_embed.set_defaults(func=cmd_embed)

    # rag
    p_rag = sub.add_parser("rag", help="Demo RAG triad-aware")
    p_rag.add_argument("query", help="Requête de recherche")
    p_rag.add_argument("-k", type=int, default=3)
    g = p_rag.add_mutually_exclusive_group()
    g.add_argument("--abstract", action="store_true", help="Biais vers explicatif/abstrait")
    g.add_argument("--concrete", action="store_true", help="Biais vers concret/exemples")
    p_rag.set_defaults(func=cmd_rag)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

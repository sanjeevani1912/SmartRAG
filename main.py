import os
import warnings
import argparse

# --- SILENCE MODE (Optimized for Demo) ---
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
warnings.filterwarnings("ignore")

from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from src.retriever import SmartRetriever
from src.router import SmartRouter
from src.generator import SmartGenerator

console = Console()

def main():
    parser = argparse.ArgumentParser(description="SmartRAG Agentic Q&A System")
    parser.add_argument("--query", type=str, help="The query to answer")
    parser.add_argument("--eval", action="store_true", help="Run the full evaluation framework")
    args = parser.parse_args()

    # --- STARTUP BANNER ---
    console.print(Panel.fit(
        "[bold cyan]SmartRAG[/bold cyan] — Agentic RAG System\n"
        "[dim]AI Regulation Document Intelligence[/dim]",
        border_style="cyan"
    ))

    BASE_DIR = os.getcwd()
    INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index")

    if args.eval:
        from src.evaluator import Evaluator
        if not os.path.exists(INDEX_PATH):
            console.print(f"[bold red]Error:[/bold red] Vector index not found at {INDEX_PATH}.")
            console.print("Please run: [bold cyan]python src/ingest.py[/bold cyan] first.")
            exit(1)
            
        retriever = SmartRetriever(INDEX_PATH)
        router = SmartRouter(threshold=0.42)
        generator = SmartGenerator()
        evaluator = Evaluator(retriever, router, generator)
        evaluator.run_evaluation()
        
    elif args.query:
        if not os.path.exists(INDEX_PATH):
            console.print(f"[bold red]Error:[/bold red] Vector index not found at {INDEX_PATH}.")
            console.print("Please run: [bold cyan]python src/ingest.py[/bold cyan] first.")
            exit(1)
            
        retriever = SmartRetriever(INDEX_PATH)
        router = SmartRouter(threshold=0.42)
        generator = SmartGenerator()
        
        console.print(f"\n[bold]QUERY:[/bold] {args.query}\n")
        
        chunks, scores = retriever.retrieve(args.query)
        q_type, reason = router.classify_query(args.query, chunks, scores)
        logs = router.get_logs()
        confidence = logs.get("confidence", "LOW")
        
        # --- ROUTER DECISION PANEL ---
        color_map = {
            "factual": "green",
            "synthesis": "yellow", 
            "out_of_scope": "red"
        }
        color = color_map.get(q_type, "white")

        console.print(Panel(
            f"[bold]Type:[/bold] [{color}]{q_type.upper()}[/{color}]\n"
            f"[bold]Confidence:[/bold] {confidence}\n"
            f"[bold]Reason:[/bold] {reason}",
            title="[bold]Router Decision[/bold]",
            border_style=color,
            expand=False
        ))
        
        answer = generator.generate(args.query, q_type, chunks, reason, confidence)
        console.print(f"\n[bold underline]ANSWER:[/bold underline]\n")
        console.print(answer)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

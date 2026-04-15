import os
import pandas as pd
import numpy as np
from rouge_score import rouge_scorer
from sklearn.metrics.pairwise import cosine_similarity
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

from src.retriever import SmartRetriever
from src.router import SmartRouter
from src.generator import SmartGenerator
from src.test_questions import TEST_QUESTIONS

console = Console()

class Evaluator:
    def __init__(self, retriever, router, generator):
        self.retriever = retriever
        self.router = router
        self.generator = generator
        self.scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

    def compute_cosine_similarity(self, text1, text2):
        if not text1 or not text2 or text1 == "Information not available." or text2 == "Information not available.":
            return 0.0
        # Reusing retriever's embeddings to avoid redundant model loading
        emb1 = np.array(self.retriever.embeddings.embed_query(text1))
        emb2 = np.array(self.retriever.embeddings.embed_query(text2))
        return cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]

    def run_evaluation(self, output_csv="data/output/evaluation_results.csv"):
        results = []
        
        # Use Progress context manager for clean interleaving of logs and progress bar
        with Progress() as progress:
            task = progress.add_task("[cyan]Running evaluation...", total=len(TEST_QUESTIONS))
            
            for i, item in enumerate(TEST_QUESTIONS):
                import time; time.sleep(2)
                query = item["query"]
                expected_type = item["expected_type"]
                ground_truth = item["ground_truth"]
                
                console.print(f"\n[bold blue][{i+1}/15][/bold blue] [white]Evaluating:[/white] [dim]{query[:60]}...[/dim]")
                
                # Step 1: Retrieve
                chunks, scores = self.retriever.retrieve(query)
                
                # GUARD: Handle empty retrieval
                if not chunks or not scores:
                    pred_type = "out_of_scope"
                    reason = "No relevant document chunks retrieved."
                    confidence = "ZERO"
                    generated_answer = "I am sorry, but no relevant information was found."
                    console.print(f"   [bold yellow]![/bold yellow] [red]No chunks found.[/red]")
                else:
                    # Step 2: Route
                    pred_type, reason = self.router.classify_query(query, chunks, scores)
                    logs = self.router.get_logs()
                    confidence = logs.get("confidence", "LOW")
                    
                    # DEBUG LOGS
                    console.print(f"   [bold cyan]>[/bold cyan] [dim]Max Score:[/dim] [bold]{logs['max_score']:.3f}[/bold] | [dim]Gap:[/dim] {logs['score_gap']:.3f} | [dim]Conf:[/dim] {confidence}")
                    console.print(f"   [bold cyan]>[/bold cyan] [dim]Decision:[/dim] [italic]{pred_type.upper()}[/italic] ({reason})")

                    # Step 3: Generate
                    generated_answer = self.generator.generate(query, pred_type, chunks, reason, confidence)
                
                # Step 4: Metrics
                routing_correct = 1 if pred_type == expected_type else 0
                rouge_l = self.scorer.score(ground_truth, generated_answer)['rougeL'].fmeasure
                cos_sim = self.compute_cosine_similarity(ground_truth, generated_answer)
                
                results.append({
                    "Query": query,
                    "Expected Type": expected_type,
                    "Predicted Type": pred_type,
                    "Routing Correct": routing_correct,
                    "ROUGE-L": round(rouge_l, 3),
                    "Cosine Sim": round(cos_sim, 3),
                    "Generated Answer": generated_answer
                })
                
                progress.advance(task)

        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False)
        
        # Calculate summary metrics
        routing_acc = df["Routing Correct"].mean() * 100
        avg_rouge = df["ROUGE-L"].mean()
        avg_sim = df["Cosine Sim"].mean()
        
        # --- RICH TABLE OUTPUT ---
        table = Table(title="[bold]SmartRAG Evaluation Results[/bold]", show_lines=True)
        table.add_column("Query", style="cyan", max_width=45, overflow="fold")
        table.add_column("Expected", style="white")
        table.add_column("Predicted", style="white")
        table.add_column("Verdict", justify="center")
        table.add_column("ROUGE-L", justify="right")

        for _, row in df.iterrows():
            correct_icon = "[green]PASS[/green]" if row["Routing Correct"] else "[red]FAIL[/red]"
            predicted_color = "green" if row["Routing Correct"] else "red"
            
            table.add_row(
                row["Query"],
                row["Expected Type"],
                f"[{predicted_color}]{row['Predicted Type']}[/{predicted_color}]",
                correct_icon,
                f"{row['ROUGE-L']:.3f}"
            )

        console.print("\n")
        console.print(table)
        
        # --- SUMMARY STATISTICS PANEL ---
        console.print(Panel(
            f"[bold green]Routing Accuracy:[/bold green] {routing_acc:.2f}%\n"
            f"[bold]Average ROUGE-L:[/bold] {avg_rouge:.3f}\n"
            f"[bold]Average Cosine Similarity:[/bold] {avg_sim:.3f}\n\n"
            f"[dim]Deep-dive logs saved to: {output_csv}[/dim]",
            title="[bold]Evaluation Summary[/bold]",
            border_style="green",
            expand=False
        ))
        
        return df

if __name__ == "__main__":
    BASE_DIR = os.getcwd()
    INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index")
    
    # Verify index exists
    if not os.path.exists(INDEX_PATH):
        print("Error: Vector index not found. Run src/ingest.py first.")
    else:
        retriever = SmartRetriever(INDEX_PATH)
        router = SmartRouter(threshold=0.42) # Defensible threshold from cluster analysis
        generator = SmartGenerator()
        
        eval_engine = Evaluator(retriever, router, generator)
        eval_engine.run_evaluation()

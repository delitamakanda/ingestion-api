import asyncio

from ingestion_api.api.v1.search import get_search_router
from ingestion_api.core.database import AsyncSessionFactory


from tests.evaluation.evaluator import RetrievalEvaluator
from tests.evaluation.dataset import load_dataset


async def main():
    async with AsyncSessionFactory() as session:
        search_router = get_search_router(session=session)
        evaluator = RetrievalEvaluator(search_router, session)

        cases = load_dataset()
        results = []

        print()
        print("="*50)
        print("Evaluating retrieval quality...")
        print("="*50)

        for case in cases:
            try:
                result = await evaluator.evaluate(case)
                results.append(result)
                print(f"Case ID: {result.case_id}")
                print(f"Query: {case.query}")
                print(f"Mode: {case.mode}")

                if case.countries:
                    print(f"Countries: {', '.join(case.countries)}")

                print(
                    f"Recall@5: {result.recall_at_5:.3f}"
                )
                print(f"Recall@10: {result.recall_at_10:.3f}")
                print(f"Precision@5: {result.precision_at_5:.3f}")
                print(f"Reciprocal Rank: {result.reciprocal_rank:.3f}")
                print(f"Term Hit Rate: {result.term_hit_rate:.3f}")

                if result.retrieved_chunks_ids:
                    print(f"Retrieved Chunk IDs:")

                    for rank, chunk_id in enumerate(result.retrieved_chunks_ids, start=1):
                        marker = ("*" if chunk_id in case.chunks_ids else "")
                        print(f"Rank {rank:>2}: {chunk_id}[{marker}]")

            except Exception as e:
                print()
                print(f"Error evaluating case {case.id}: {e}")
                print(f"query: {case.query}")

                await session.rollback()

        if not results:
            print("No results to evaluate.")
            return

        print()
        print("="*50)
        print("global evaluation metrics")
        print("="*50)

        count = len(results)

        avg_recall_5 = sum(result.recall_at_5 for result in results) / count
        avg_recall_10 = sum(result.recall_at_10 for result in results) / count
        avg_precision_5 = sum(result.precision_at_5 for result in results) / count
        avg_reciprocal_rank = sum(result.reciprocal_rank for result in results) / count

        avg_term_hit = sum(result.term_hit_rate for result in results) / count

        print(f"Average term hit rate: {avg_term_hit:.3f}")
        print(f"Average recall at 5: {avg_recall_5:.3f}")
        print(f"Average recall at 10: {avg_recall_10:.3f}")
        print(f"Average precision at 5: {avg_precision_5:.3f}")
        print(f"Average reciprocal rank: {avg_reciprocal_rank:.3f}")



if __name__ == "__main__":
    asyncio.run(main())
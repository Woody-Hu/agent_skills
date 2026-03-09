#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from memory_system import ResearchAgentMemory


def cmd_record(args):
    memory_system = ResearchAgentMemory(args.storage)
    
    tags = args.tags.split(',') if args.tags else []
    keywords = args.keywords.split(',') if args.keywords else []
    
    memory_data = {
        "type": args.type,
        "tags": tags,
        "keywords": keywords,
        "context_string": args.context or "",
        "error_snapshot": {},
        "reflection": {},
        "metadata": {}
    }
    
    if args.reflection_file:
        with open(args.reflection_file, 'r', encoding='utf-8') as f:
            reflection_data = json.load(f)
            memory_data['reflection'] = reflection_data
    
    if args.snapshot_file:
        with open(args.snapshot_file, 'r', encoding='utf-8') as f:
            snapshot_data = json.load(f)
            memory_data['error_snapshot'] = snapshot_data
    
    memory_id = memory_system.record(memory_data)
    print(f"Memory recorded: {memory_id}")
    return 0


def cmd_recall(args):
    memory_system = ResearchAgentMemory(args.storage)
    
    tags = args.tags.split(',') if args.tags else None
    keywords = args.keywords.split(',') if args.keywords else None
    
    results = memory_system.recall(
        query=args.query,
        tags=tags,
        keywords=keywords,
        top_k=args.top_k,
        threshold=args.threshold
    )
    
    if not results:
        print("No matching memories found.")
        return 0
    
    for i, mem in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"ID: {mem.get('memory_id', 'N/A')}")
        print(f"Type: {mem.get('type', 'N/A')}")
        print(f"Tags: {', '.join(mem.get('tags', []))}")
        print(f"Keywords: {', '.join(mem.get('keywords', []))}")
        
        reflection = mem.get('reflection', {})
        if reflection:
            if reflection.get('lesson_learned'):
                print(f"Lesson: {reflection['lesson_learned']}")
            if reflection.get('prevention_strategy'):
                print(f"Prevention: {reflection['prevention_strategy']}")
    
    return 0


def cmd_augment(args):
    memory_system = ResearchAgentMemory(args.storage)
    
    with open(args.prompt_file, 'r', encoding='utf-8') as f:
        current_prompt = f.read()
    
    augmented = memory_system.augment_context(
        task_description=args.task,
        current_prompt=current_prompt,
        top_k=args.top_k,
        threshold=args.threshold
    )
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(augmented)
        print(f"Augmented prompt written to: {args.output}")
    else:
        print(augmented)
    
    return 0


def cmd_stats(args):
    memory_system = ResearchAgentMemory(args.storage)
    stats = memory_system.get_stats()
    
    print(f"Total memories: {stats['total_memories']}")
    print(f"Unique tags: {stats['unique_tags']}")
    print(f"BM25 available: {stats['bm25_available']}")
    print(f"Vector available: {stats['vector_available']}")
    print("\nTag distribution:")
    for tag, count in stats['tag_distribution'].items():
        print(f"  {tag}: {count}")
    
    return 0


def cmd_list(args):
    memory_system = ResearchAgentMemory(args.storage)
    memories = memory_system.list_memories(limit=args.limit, offset=args.offset)
    
    for mem in memories:
        print(f"\n--- {mem.get('memory_id', 'N/A')} ---")
        print(f"Type: {mem.get('type', 'N/A')}")
        print(f"Timestamp: {mem.get('timestamp', 'N/A')}")
        print(f"Tags: {', '.join(mem.get('tags', []))}")
        print(f"Keywords: {', '.join(mem.get('keywords', []))}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Research Agent Memory System CLI"
    )
    parser.add_argument(
        "--storage",
        default="./memory_store",
        help="Path to memory storage directory"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    record_parser = subparsers.add_parser("record", help="Record a new memory")
    record_parser.add_argument("--type", required=True, help="Memory type")
    record_parser.add_argument("--tags", help="Comma-separated tags")
    record_parser.add_argument("--keywords", help="Comma-separated keywords")
    record_parser.add_argument("--context", help="Context string")
    record_parser.add_argument("--reflection-file", help="Path to reflection JSON file")
    record_parser.add_argument("--snapshot-file", help="Path to error snapshot JSON file")
    record_parser.set_defaults(func=cmd_record)
    
    recall_parser = subparsers.add_parser("recall", help="Recall memories")
    recall_parser.add_argument("--query", required=True, help="Query string")
    recall_parser.add_argument("--tags", help="Comma-separated tags to filter")
    recall_parser.add_argument("--keywords", help="Comma-separated keywords to filter")
    recall_parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    recall_parser.add_argument("--threshold", type=float, default=0.3, help="Similarity threshold")
    recall_parser.set_defaults(func=cmd_recall)
    
    augment_parser = subparsers.add_parser("augment", help="Augment prompt with memories")
    augment_parser.add_argument("--task", required=True, help="Task description")
    augment_parser.add_argument("--prompt-file", required=True, help="Path to prompt file")
    augment_parser.add_argument("--output", help="Output file path")
    augment_parser.add_argument("--top-k", type=int, default=3, help="Number of memories")
    augment_parser.add_argument("--threshold", type=float, default=0.5, help="Similarity threshold")
    augment_parser.set_defaults(func=cmd_augment)
    
    stats_parser = subparsers.add_parser("stats", help="Show memory statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    list_parser = subparsers.add_parser("list", help="List all memories")
    list_parser.add_argument("--limit", type=int, default=100, help="Number of memories")
    list_parser.add_argument("--offset", type=int, default=0, help="Offset")
    list_parser.set_defaults(func=cmd_list)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

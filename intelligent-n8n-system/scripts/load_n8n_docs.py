#!/usr/bin/env python3
"""
N8N Documentation Loader Script

This script loads n8n documentation from various sources into the knowledge base.
It can be run standalone or as part of the initialization process.
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge.documentation_loader import N8nDocumentationLoader
from knowledge.lightrag_service import LightRAGService


async def load_documentation_only():
    """Load documentation without indexing to LightRAG"""
    print("📚 Loading n8n documentation from various sources...")

    async with N8nDocumentationLoader() as loader:
        results = await loader.load_all_documentation()

        print(f"\n✅ Documentation loading completed!")
        print(f"📊 Summary:")
        print(f"   - Total documents: {results['total_documents']}")
        print(f"   - Total size: {results['total_size']:,} bytes")
        print(f"   - Load time: {results['load_time']:.2f} seconds")
        print(f"   - Sources processed: {len(results['sources'])}")

        print(f"\n📋 Source details:")
        for source in results["sources"]:
            status_emoji = (
                "✅"
                if source["status"] == "success"
                else "❌"
                if source["status"] == "failed"
                else "💾"
            )
            print(
                f"   {status_emoji} {source['name']}: {source.get('documents_count', 0)} documents ({source.get('total_size', 0):,} bytes)"
            )
            if source.get("error"):
                print(f"      Error: {source['error']}")

        return results


async def load_and_index_documentation():
    """Load documentation and index it into LightRAG"""
    print("📚 Loading and indexing n8n documentation into LightRAG...")

    # First load documentation
    load_results = await load_documentation_only()

    if load_results["total_documents"] == 0:
        print("❌ No documents loaded, skipping LightRAG indexing")
        return False

    print(f"\n🤖 Indexing {load_results['total_documents']} documents into LightRAG...")

    # Initialize LightRAG service
    lightrag_service = LightRAGService()

    try:
        # Initialize knowledge base (this will use the DocumentationLoader)
        success = await lightrag_service.initialize_knowledge_base()

        if success:
            print("✅ Successfully indexed documentation into LightRAG knowledge base")
            return True
        else:
            print("❌ Failed to index documentation into LightRAG")
            return False

    except Exception as e:
        print(f"❌ Error during LightRAG indexing: {e}")
        return False


async def list_sources():
    """List available documentation sources"""
    print("📋 Available n8n documentation sources:")

    async with N8nDocumentationLoader() as loader:
        for source in loader.sources:
            print(f"   🔗 {source.name}")
            print(f"      URL: {source.url}")
            print(f"      Type: {source.source_type}")
            print(f"      Priority: {source.priority}")
            print()


async def check_cache_status():
    """Check the status of cached documentation"""
    print("💾 Checking documentation cache status...")

    async with N8nDocumentationLoader() as loader:
        for source in loader.sources:
            cache_file = loader.cache_dir / f"{source.name}_cache.json"

            if cache_file.exists():
                try:
                    import json

                    with open(cache_file, "r") as f:
                        cache_data = json.load(f)

                    last_updated = cache_data.get("last_updated", "Unknown")
                    doc_count = cache_data.get("documents_count", 0)
                    total_size = cache_data.get("total_size", 0)

                    print(
                        f"   ✅ {source.name}: {doc_count} documents ({total_size:,} bytes)"
                    )
                    print(f"      Last updated: {last_updated}")

                except Exception as e:
                    print(f"   ❌ {source.name}: Cache file corrupted ({e})")
            else:
                print(f"   ⚪ {source.name}: No cache found")


async def force_update():
    """Force update all documentation sources"""
    print("🔄 Force updating all documentation sources...")

    # This would require modifying the DocumentationLoader to accept force_update parameter
    # For now, we'll just delete cache files and reload
    async with N8nDocumentationLoader() as loader:
        import shutil

        # Clear cache directory
        if loader.cache_dir.exists():
            shutil.rmtree(loader.cache_dir)
            print(f"🗑️  Cleared cache directory: {loader.cache_dir}")

        # Reload all documentation
        await load_documentation_only()


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Load n8n documentation into knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python load_n8n_docs.py --load-only          # Load docs without indexing
  python load_n8n_docs.py --load-and-index     # Load and index into LightRAG
  python load_n8n_docs.py --list-sources       # List available sources
  python load_n8n_docs.py --check-cache        # Check cache status
  python load_n8n_docs.py --force-update       # Force update all sources
        """,
    )

    parser.add_argument(
        "--load-only",
        action="store_true",
        help="Load documentation without indexing to LightRAG",
    )
    parser.add_argument(
        "--load-and-index",
        action="store_true",
        help="Load documentation and index into LightRAG",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List available documentation sources",
    )
    parser.add_argument("--check-cache", action="store_true", help="Check cache status")
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Force update all documentation sources",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Default action if no specific action is specified
    if not any(
        [
            args.load_only,
            args.load_and_index,
            args.list_sources,
            args.check_cache,
            args.force_update,
        ]
    ):
        args.load_and_index = True  # Default to load and index

    try:
        if args.list_sources:
            await list_sources()
        elif args.check_cache:
            await check_cache_status()
        elif args.force_update:
            await force_update()
        elif args.load_only:
            await load_documentation_only()
        elif args.load_and_index:
            success = await load_and_index_documentation()
            if not success:
                sys.exit(1)

        print("\n🎉 Operation completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

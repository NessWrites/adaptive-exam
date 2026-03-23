# main.py (with CLI arguments)
import sys
import json
import argparse
from pathlib import Path
from config import Config
from distractor_manager import DistractorManager
from utils import load_json, save_json
sys.path.append(str(Path(__file__).parent))



def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate distractors for multiple-choice questions")
    
    parser.add_argument(
        "--questions", 
        default="files/output.json",
        help="Path to questions JSON file (default: questions.json)"
    )
    
    parser.add_argument(
        "--output", 
        default="files/output_with_distractor1.json",
        help="Output file path (default: questions_with_distractors.json)"
    )
    
    parser.add_argument(
        "--agent",
        choices=["numeric", "llm", "hybrid"],
        default="hybrid",
        help="Agent type to use (default: hybrid)"
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM (use database/fallback only)"
    )
    
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Disable database (use LLM only)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode (process only first 5 questions)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    return parser.parse_args()

def main():
    print("=" * 70)
    print("🤖 DISTRACTOR GENERATOR v2.0")
    print("=" * 70)
    
    # Parse arguments
    args = parse_arguments()
    
    # Load and override configuration
    config = Config()
    
    # Override with command line arguments
    config.QUESTIONS_PATH = args.questions
    config.OUTPUT_PATH = args.output
    config.AGENT_TYPE = args.agent
    config.USE_LLM = not args.no_llm
    config.USE_DATABASE = not args.no_db
    
    config.validate()
    
    # Print configuration
    print(f"\n⚙️  Configuration:")
    print(f"   Questions file: {config.QUESTIONS_PATH}")
    print(f"   Output file: {config.OUTPUT_PATH}")
    print(f"   Agent type: {config.AGENT_TYPE}")
    print(f"   LLM enabled: {config.USE_LLM}")
    print(f"   Database enabled: {config.USE_DATABASE}")
    if config.USE_LLM:
        print(f"   LLM model: {config.GROQ_MODEL}")
    
    # Load questions
    print(f"\n📂 Loading questions...")
    try:
        with open(config.QUESTIONS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{config.QUESTIONS_PATH}' not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{config.QUESTIONS_PATH}': {e}")
        sys.exit(1)
    
    # Extract questions
    if isinstance(data, list):
        questions = data
    elif isinstance(data, dict):
        if "questions" in data:
            questions = data["questions"]
        elif "data" in data:
            questions = data["data"]
        else:
            # Assume it's already a list of questions
            questions = [data] if isinstance(data, dict) else []
    else:
        print(f"❌ Error: Unexpected data format")
        sys.exit(1)
    
    if not questions:
        print("❌ No questions found!")
        sys.exit(1)
    
    # Test mode: limit to 5 questions
    if args.test:
        questions = questions[:5]
        print(f"🧪 Test mode: Processing only first {len(questions)} questions")
    
    print(f"✅ Loaded {len(questions)} questions")
    
    # Initialize distractor manager
    print(f"\n🔧 Initializing...")
    try:
        manager = DistractorManager(config)
        print("✅ Initialization successful!")
        
        # Test LLM connectivity
        if config.USE_LLM and config.AGENT_TYPE != "numeric":
            print(f"\n🔗 Testing LLM connectivity...")
            if manager.llm_agent and manager.llm_agent.client:
                try:
                    test_response = manager.llm_agent.client.chat.completions.create(
                        model=config.GROQ_MODEL,
                        messages=[{"role": "user", "content": "Test"}],
                        max_tokens=5
                    )
                    print(f"✅ LLM connection successful")
                except Exception as e:
                    print(f"⚠️  LLM connection failed: {e}")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)
    
    # Process questions
    print(f"\n🚀 Processing {len(questions)} questions...")
    print("-" * 70)
    
    results = []
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "distractors": 0,
        "sources": {}
    }
    
    for i, question in enumerate(questions, 1):
        qid = question.get('core_id', question.get('id', f'Q{i}'))
        qtype = question.get('type', 'unknown')
        concept = question.get('concept_tag', 'N/A')
        
        if args.verbose:
            print(f"\n[{i}/{len(questions)}] {qid}")
            print(f"   Type: {qtype}, Concept: {concept}")
            print(f"   Question: {question['stem'][:80]}...")
        else:
            print(f"[{i}/{len(questions)}] Processing {qid}...", end=' ')
        
        try:
            # Generate distractors
            distractors = manager.generate_distractors(question)
            question["distractors"] = distractors
            
            # Update statistics
            stats["total"] += 1
            if distractors:
                stats["success"] += 1
                stats["distractors"] += len(distractors)
                
                # Track sources
                for d in distractors:
                    source = d.get('source', 'unknown')
                    stats["sources"][source] = stats["sources"].get(source, 0) + 1
                
                if args.verbose:
                    print(f"   ✅ Generated {len(distractors)} distractors")
                    for d in distractors[:2]:  # Show first 2
                        print(f"     - {d['text'][:50]}... [{d.get('source', '?')}]")
                else:
                    print(f"✅ ({len(distractors)} distractors)")
            else:
                stats["failed"] += 1
                if args.verbose:
                    print(f"   ⚠️  No distractors generated")
                else:
                    print(f"⚠️  (0 distractors)")
            
            results.append(question)
            
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Process interrupted by user")
            break
        except Exception as e:
            stats["failed"] += 1
            print(f"❌ Error: {e}")
            # Add question with empty distractors
            question["distractors"] = []
            results.append(question)
    
    # Save results
    print(f"\n💾 Saving results to {config.OUTPUT_PATH}...")
    try:
        save_json({"questions": results}, config.OUTPUT_PATH)
        print("✅ Results saved successfully!")
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        # Try direct save
        try:
            with open(config.OUTPUT_PATH, 'w', encoding='utf-8') as f:
                json.dump({"questions": results}, f, indent=2, ensure_ascii=False)
            print("✅ Saved using direct method")
        except Exception as e2:
            print(f"❌ Failed to save: {e2}")
    
    # Generate report
    print("\n" + "=" * 70)
    print("📊 FINAL REPORT")
    print("=" * 70)
    
    print(f"\n📈 Performance:")
    print(f"   Total Questions: {stats['total']}")
    print(f"   Successful: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"   Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    
    if stats['total'] > 0:
        avg_distractors = stats['distractors'] / stats['total']
        print(f"   Total Distractors: {stats['distractors']}")
        print(f"   Avg per Question: {avg_distractors:.1f}")
    
    if stats['sources']:
        print(f"\n🔍 Distractor Sources:")
        for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['distractors'] * 100) if stats['distractors'] > 0 else 0
            print(f"   - {source}: {count} ({percentage:.1f}%)")
    
    # Questions without distractors
    no_distractors = [q for q in results if not q.get("distractors")]
    if no_distractors:
        print(f"\n⚠️  Questions with NO distractors ({len(no_distractors)}):")
        for q in no_distractors[:3]:
            qid = q.get('core_id', q.get('id', 'Unknown'))
            print(f"   - {qid}: {q['stem'][:60]}...")
    
    # Sample output
    print(f"\n🎯 Sample Output:")
    for q in results[:2]:  # Show first 2
        if q.get("distractors"):
            qid = q.get('core_id', q.get('id', 'Sample'))
            print(f"\n{qid}: {q['stem'][:50]}...")
            for d in q["distractors"][:2]:
                print(f"  - {d['text'][:40]}...")
    
    print("\n" + "=" * 70)
    print("✅ Generation complete!")
    print(f"📁 Output: {config.OUTPUT_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    main()
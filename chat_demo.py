"""
GLM v3.0 - Interactive Chat Demo
=================================

Interactive chat interface to test all GLM v3.0 features

Usage:
    python3 chat_demo.py
    
    Commands:
    - transform <text> from <domain1> to <domain2>
    - similarity <text1> vs <text2> in <domain>
    - analyze <text> in <domain>
    - list domains
    - help
    - exit
"""

import sys
import os
import numpy as np
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.symbolic import SymbolicEngine
from domains.geometric import GeometricDomain
from domains.text import TextDomain
from domains.code import CodeDomain
from domains.image import ImageDomain


class GLMChatDemo:
    """Interactive chat interface for GLM v3.0"""
    
    def __init__(self):
        print("\n" + "="*70)
        print("🎉 GLM v3.0 - Interactive Chat Demo")
        print("="*70)
        
        # Initialize engine
        self.engine = SymbolicEngine(embedding_dim=128)
        
        # Register domains
        print("\n📦 Initializing domains...")
        self.engine.register_domain(GeometricDomain())
        self.engine.register_domain(TextDomain())
        self.engine.register_domain(CodeDomain())
        self.engine.register_domain(ImageDomain())
        
        print("✓ All domains initialized")
        
        # Commands
        self.commands = {
            'transform': self.cmd_transform,
            'similarity': self.cmd_similarity,
            'analyze': self.cmd_analyze,
            'list': self.cmd_list_domains,
            'domains': self.cmd_list_domains,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
        }
    
    def run(self):
        """Run the chat loop"""
        print("\n" + "="*70)
        print("💬 Type 'help' for commands or 'exit' to quit")
        print("="*70 + "\n")
        
        while True:
            try:
                user_input = input("🤖 GLM> ").strip()
                
                if not user_input:
                    continue
                
                self.process_command(user_input)
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def process_command(self, user_input: str):
        """Process user command"""
        parts = user_input.lower().split()
        
        if not parts:
            return
        
        command = parts[0]
        args = ' '.join(parts[1:])
        
        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"❌ Unknown command: {command}")
            print("   Type 'help' for available commands")
    
    # ========================================================================
    # COMMANDS
    # ========================================================================
    
    def cmd_transform(self, args: str):
        """Transform content between domains"""
        try:
            # Parse: transform <text> from <domain1> to <domain2>
            if ' from ' not in args or ' to ' not in args:
                print("Usage: transform <text> from <domain1> to <domain2>")
                print("Example: transform 'hello world' from text to code")
                return
            
            text_part, rest = args.split(' from ', 1)
            source_domain, target_domain = rest.split(' to ', 1)
            
            text_part = text_part.strip().strip("'\"")
            source_domain = source_domain.strip()
            target_domain = target_domain.strip()
            
            print(f"\n🔄 Transforming: {text_part}")
            print(f"   From: {source_domain} → To: {target_domain}")
            
            # Perform transformation
            result = self.engine.transform(text_part, source_domain, target_domain)
            
            print(f"\n✅ Result:")
            print(f"   {result}")
            
            # Show symbolic info
            sym = self.engine.abstract(text_part, source_domain)
            print(f"\n📊 Symbolic Representation:")
            print(f"   ∆ (Delta) norm: {np.linalg.norm(sym.delta):.4f}")
            print(f"   ∞ (Infinity) nodes: {sym.infinity.number_of_nodes()}, edges: {sym.infinity.number_of_edges()}")
            print(f"   Ο (Omega) norm: {np.linalg.norm(sym.omega):.4f}")
        
        except Exception as e:
            print(f"❌ Transform error: {e}")
    
    def cmd_similarity(self, args: str):
        """Calculate similarity between two contents"""
        try:
            # Parse: similarity <text1> vs <text2> in <domain>
            if ' vs ' not in args or ' in ' not in args:
                print("Usage: similarity <text1> vs <text2> in <domain>")
                print("Example: similarity 'cat on mat' vs 'feline on rug' in text")
                return
            
            content_part, domain_part = args.rsplit(' in ', 1)
            text1, text2 = content_part.split(' vs ', 1)
            
            text1 = text1.strip().strip("'\"")
            text2 = text2.strip().strip("'\"")
            domain = domain_part.strip()
            
            print(f"\n📊 Calculating similarity...")
            print(f"   Text 1: {text1}")
            print(f"   Text 2: {text2}")
            print(f"   Domain: {domain}")
            
            # Get symbolic representations
            sym1 = self.engine.abstract(text1, domain)
            sym2 = self.engine.abstract(text2, domain)
            
            # Calculate similarity
            similarity = np.dot(sym1.omega, sym2.omega)
            
            print(f"\n✅ Similarity: {similarity:.4f} ({similarity*100:.1f}%)")
            print(f"\n📈 Details:")
            print(f"   Text 1 - ∆: {np.linalg.norm(sym1.delta):.4f}, ∞: {sym1.infinity.number_of_nodes()} nodes, Ο: {np.linalg.norm(sym1.omega):.4f}")
            print(f"   Text 2 - ∆: {np.linalg.norm(sym2.delta):.4f}, ∞: {sym2.infinity.number_of_nodes()} nodes, Ο: {np.linalg.norm(sym2.omega):.4f}")
        
        except Exception as e:
            print(f"❌ Similarity error: {e}")
    
    def cmd_analyze(self, args: str):
        """Analyze content in a domain"""
        try:
            # Parse: analyze <text> in <domain>
            if ' in ' not in args:
                print("Usage: analyze <text> in <domain>")
                print("Example: analyze 'def hello(): pass' in code")
                return
            
            text, domain = args.rsplit(' in ', 1)
            text = text.strip().strip("'\"")
            domain = domain.strip()
            
            print(f"\n🔍 Analyzing: {text}")
            print(f"   Domain: {domain}")
            
            # Get symbolic representation
            sym = self.engine.abstract(text, domain)
            
            print(f"\n✅ Analysis:")
            print(f"   ∆ (Delta) - Essence:")
            print(f"      Norm: {np.linalg.norm(sym.delta):.4f}")
            print(f"      Dimension: {sym.delta.shape[0]}")
            
            print(f"\n   ∞ (Infinity) - Process Graph:")
            print(f"      Nodes: {sym.infinity.number_of_nodes()}")
            print(f"      Edges: {sym.infinity.number_of_edges()}")
            print(f"      Density: {sym.infinity.number_of_edges() / max(1, sym.infinity.number_of_nodes()):.2f}")
            
            print(f"\n   Ο (Omega) - Completeness:")
            print(f"      Norm: {np.linalg.norm(sym.omega):.4f}")
            print(f"      Dimension: {sym.omega.shape[0]}")
            
            print(f"\n   Metadata:")
            for key, value in sym.metadata.items():
                print(f"      {key}: {value}")
        
        except Exception as e:
            print(f"❌ Analysis error: {e}")
    
    def cmd_list_domains(self, args: str):
        """List available domains"""
        domains = self.engine.list_domains()
        
        print(f"\n📚 Available Domains ({len(domains)}):")
        for i, domain in enumerate(domains, 1):
            print(f"   {i}. {domain}")
        
        print(f"\n💡 Tip: Use domain names in commands (e.g., 'transform ... from text to code')")
    
    def cmd_help(self, args: str):
        """Show help"""
        print("\n" + "="*70)
        print("📖 GLM v3.0 - Chat Commands")
        print("="*70)
        
        print("\n🔄 TRANSFORMATION:")
        print("   transform <text> from <domain1> to <domain2>")
        print("   Example: transform 'hello' from text to code")
        
        print("\n📊 SIMILARITY:")
        print("   similarity <text1> vs <text2> in <domain>")
        print("   Example: similarity 'cat on mat' vs 'feline on rug' in text")
        
        print("\n🔍 ANALYSIS:")
        print("   analyze <text> in <domain>")
        print("   Example: analyze 'def hello(): pass' in code")
        
        print("\n📚 DOMAINS:")
        print("   list domains")
        print("   domains")
        
        print("\n⚙️  SYSTEM:")
        print("   help - Show this message")
        print("   exit - Exit the chat")
        
        print("\n💡 TIPS:")
        print("   - Use quotes for multi-word text: 'hello world'")
        print("   - Available domains: geometry, text, code, image")
        print("   - All transformations use symbolic ∆∞Ο representation")
        
        print("="*70 + "\n")
    
    def cmd_exit(self, args: str):
        """Exit the chat"""
        print("\n👋 Goodbye!")
        sys.exit(0)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    try:
        chat = GLMChatDemo()
        chat.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

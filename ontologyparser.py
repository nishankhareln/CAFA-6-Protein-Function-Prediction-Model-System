"""
CAFA 6 Protein Function Prediction - GO Ontology Parser
This script parses the GO ontology structure and creates helper functions
"""

import obonet
import networkx as nx
import pickle
from collections import defaultdict

class GOGraphParser:
    """Parse and navigate the Gene Ontology graph structure"""
    
    def __init__(self, obo_file):
        """
        Initialize GO graph parser
        
        Args:
            obo_file: Path to go-basic.obo file
        """
        print("Loading GO ontology graph...")
        self.graph = obonet.read_obo(obo_file)
        print(f" Loaded {len(self.graph)} GO terms")
        
        # Separate by namespace
        self.namespaces = defaultdict(set)
        for term_id, data in self.graph.nodes(data=True):
            if 'namespace' in data:
                ns = data['namespace']
                if ns == 'molecular_function':
                    self.namespaces['MFO'].add(term_id)
                elif ns == 'biological_process':
                    self.namespaces['BPO'].add(term_id)
                elif ns == 'cellular_component':
                    self.namespaces['CCO'].add(term_id)
        
        print(f"  - MFO terms: {len(self.namespaces['MFO'])}")
        print(f"  - BPO terms: {len(self.namespaces['BPO'])}")
        print(f"  - CCO terms: {len(self.namespaces['CCO'])}")
    
    def get_ancestors(self, term_id):
        """
        Get all ancestor terms (parents, grandparents, etc.)
        
        Args:
            term_id: GO term ID (e.g., 'GO:0008150')
            
        Returns:
            set: All ancestor term IDs
        """
        if term_id not in self.graph:
            return set()
        
        ancestors = set()
        try:
            # NetworkX ancestors includes the node itself, we exclude it
            all_ancestors = nx.ancestors(self.graph, term_id)
            ancestors.update(all_ancestors)
        except nx.NetworkXError:
            pass
        
        return ancestors
    
    def get_descendants(self, term_id):
        """
        Get all descendant terms (children, grandchildren, etc.)
        
        Args:
            term_id: GO term ID
            
        Returns:
            set: All descendant term IDs
        """
        if term_id not in self.graph:
            return set()
        
        descendants = set()
        try:
            all_descendants = nx.descendants(self.graph, term_id)
            descendants.update(all_descendants)
        except nx.NetworkXError:
            pass
        
        return descendants
    
    def propagate_terms(self, term_ids):
        """
        Given a set of GO terms, add all their ancestors (hierarchy propagation)
        This ensures consistency: if a protein has a term, it must have all parent terms
        
        Args:
            term_ids: Set or list of GO term IDs
            
        Returns:
            set: Original terms plus all ancestors
        """
        propagated = set(term_ids)
        
        for term_id in term_ids:
            ancestors = self.get_ancestors(term_id)
            propagated.update(ancestors)
        
        return propagated
    
    def get_term_info(self, term_id):
        """
        Get information about a GO term
        
        Args:
            term_id: GO term ID
            
        Returns:
            dict: Term information (name, namespace, etc.)
        """
        if term_id not in self.graph:
            return None
        
        data = self.graph.nodes[term_id]
        return {
            'id': term_id,
            'name': data.get('name', 'Unknown'),
            'namespace': data.get('namespace', 'Unknown'),
            'definition': data.get('def', 'No definition')
        }
    
    def filter_by_ontology(self, term_ids, ontology):
        """
        Filter GO terms by ontology type
        
        Args:
            term_ids: List/set of GO term IDs
            ontology: 'MFO', 'BPO', or 'CCO'
            
        Returns:
            set: Filtered term IDs
        """
        return set(term_ids) & self.namespaces[ontology]
    
    def save(self, filepath):
        """Save parser to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f" Saved GO parser to {filepath}")
    
    @staticmethod
    def load(filepath):
        """Load parser from file"""
        with open(filepath, 'rb') as f:
            parser = pickle.load(f)
        print(f" Loaded GO parser from {filepath}")
        return parser


if __name__ == "__main__":
    import os
    
    # Initialize parser
    GO_OBO = r"D:\CAFA project\data\go-basic.obo"  # Update path as needed
    
    if not os.path.exists(GO_OBO):
        print(f" File not found: {GO_OBO}")
        print("Please update the path to your go-basic.obo file")
    else:
        parser = GOGraphParser(GO_OBO)
        
        # Example: Get information about a GO term
        print("\n" + "="*80)
        print("EXAMPLE 1: Get term information")
        print("="*80)
        term = "GO:0003674"  # Molecular function root
        info = parser.get_term_info(term)
        if info:
            print(f"Term: {info['id']}")
            print(f"Name: {info['name']}")
            print(f"Namespace: {info['namespace']}")
        
        # Example: Get ancestors
        print("\n" + "="*80)
        print("EXAMPLE 2: Get ancestors of a term")
        print("="*80)
        test_term = "GO:0016791"  # phosphatase activity
        ancestors = parser.get_ancestors(test_term)
        print(f"Term: {test_term}")
        print(f"Number of ancestors: {len(ancestors)}")
        print(f"First 5 ancestors: {list(ancestors)[:5]}")
        
        # Example: Propagate terms (critical for predictions)
        print("\n" + "="*80)
        print("EXAMPLE 3: Propagate terms (add all ancestors)")
        print("="*80)
        original_terms = {"GO:0016791", "GO:0004518"}
        propagated_terms = parser.propagate_terms(original_terms)
        print(f"Original terms: {len(original_terms)}")
        print(f"After propagation: {len(propagated_terms)}")
        print(f"Added {len(propagated_terms) - len(original_terms)} ancestor terms")
        
        # Save parser for later use
        parser.save("go_parser.pkl")
        
        print("\n" + "="*80)
        print("GO PARSER READY!")
        print("You can now use this parser in your modeling pipeline")
        print("="*80)
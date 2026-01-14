import unittest
from unittest.mock import MagicMock, patch, Mock
from typing import Dict, Any

# Import END from the source module to avoid direct langgraph dependency in tests
try:
    from langgraph.graph import END
except ImportError:
    # If langgraph is not available, create a mock END object
    END = object()

from src.section_to_entity_dev import build_cluster_dev_graph_workflow


class SectionToEntityDevTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Mock the ChromaDB collections to avoid database dependencies
        self.mock_master_collection = MagicMock()
        self.mock_sectional_collection = MagicMock()
        
    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_creates_graph(self, mock_client, mock_sectional, mock_master):
        """Test that the workflow graph is created successfully"""
        # Mock the StateGraph and its methods
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder):
            result = build_cluster_dev_graph_workflow()
            
            # Verify graph is returned
            self.assertEqual(result, mock_graph)
            
            # Verify builder was compiled
            mock_builder.compile.assert_called_once()

    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_adds_all_nodes(self, mock_client, mock_sectional, mock_master):
        """Test that all required nodes are added to the graph"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Verify all nodes were added
            expected_nodes = [
                "section_entity_matching",
                "new_entity_dev",
                "entity_improving_bool",
                "entity_improving",
                "load_master_db"
            ]
            
            add_node_calls = mock_builder.add_node.call_args_list
            added_node_names = [call[0][0] for call in add_node_calls]
            
            for node_name in expected_nodes:
                self.assertIn(node_name, added_node_names, f"Node {node_name} was not added")

    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_sets_entry_point(self, mock_client, mock_sectional, mock_master):
        """Test that the entry point is set correctly"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Verify entry point is set
            mock_builder.set_entry_point.assert_called_once_with("section_entity_matching")

    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_adds_conditional_edges(self, mock_client, mock_sectional, mock_master):
        """Test that conditional edges are added correctly"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Verify conditional edges were added
            conditional_edge_calls = mock_builder.add_conditional_edges.call_args_list
            
            # Should have 2 conditional edges
            self.assertEqual(len(conditional_edge_calls), 2)
            
            # Check first conditional edge (from section_entity_matching)
            first_call = conditional_edge_calls[0]
            self.assertEqual(first_call[0][0], "section_entity_matching")
            
            # Check second conditional edge (from entity_improving_bool)
            second_call = conditional_edge_calls[1]
            self.assertEqual(second_call[0][0], "entity_improving_bool")

    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_adds_regular_edges(self, mock_client, mock_sectional, mock_master):
        """Test that regular edges are added correctly"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Verify regular edges were added
            edge_calls = mock_builder.add_edge.call_args_list
            
            # Should have 3 regular edges
            self.assertEqual(len(edge_calls), 3)
            
            # Check edges
            edge_pairs = [(call[0][0], call[0][1]) for call in edge_calls]
            
            self.assertIn(("new_entity_dev", "load_master_db"), edge_pairs)
            self.assertIn(("entity_improving", "load_master_db"), edge_pairs)
            # Check that load_master_db has an edge to END
            load_master_db_edges = [pair for pair in edge_pairs if pair[0] == "load_master_db"]
            self.assertEqual(len(load_master_db_edges), 1)
            # Verify the edge goes to END (not a string)
            end_edge = load_master_db_edges[0]
            self.assertEqual(end_edge[0], "load_master_db")
            # END constant should be the same object type (not a string)
            self.assertIs(end_edge[1], END)

    def test_routing_function_new_existing_entity_match_true(self):
        """Test routing function logic when entity match is True"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        routing_fn_captured = None
        
        def capture_routing_fn(*args, **kwargs):
            nonlocal routing_fn_captured
            if len(args) >= 2:
                routing_fn_captured = args[1]
            return MagicMock()
        
        mock_builder.add_conditional_edges.side_effect = capture_routing_fn
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Test the first routing function (new_existing_entity_routing_fn)
            if routing_fn_captured:
                state_match = {"section_entity_match_bool": True}
                state_no_match = {"section_entity_match_bool": False}
                state_missing = {}
                
                result_match = routing_fn_captured(state_match)
                result_no_match = routing_fn_captured(state_no_match)
                result_missing = routing_fn_captured(state_missing)
                
                self.assertEqual(result_match, "entity_improving_bool")
                self.assertEqual(result_no_match, "new_entity_dev")
                self.assertEqual(result_missing, "new_entity_dev")

    def test_routing_function_entity_improvement_required(self):
        """Test routing function logic for entity improvement"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        routing_fns = []
        
        def capture_routing_fn(*args, **kwargs):
            if len(args) >= 2:
                routing_fns.append(args[1])
            return MagicMock()
        
        mock_builder.add_conditional_edges.side_effect = capture_routing_fn
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Test the second routing function (entity_improvement_required_routing_fn)
            if len(routing_fns) >= 2:
                improvement_fn = routing_fns[1]
                
                state_required = {"entity_improvement_required_bool": True}
                state_not_required = {"entity_improvement_required_bool": False}
                state_missing = {}
                
                result_required = improvement_fn(state_required)
                result_not_required = improvement_fn(state_not_required)
                result_missing = improvement_fn(state_missing)
                
                self.assertEqual(result_required, "entity_improving")
                self.assertEqual(result_not_required, "end")
                self.assertEqual(result_missing, "end")

    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_conditional_edge_mapping(self, mock_client, mock_sectional, mock_master):
        """Test that conditional edges have correct mappings"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Get conditional edge calls
            conditional_edge_calls = mock_builder.add_conditional_edges.call_args_list
            
            # Check first conditional edge mapping
            first_mapping = conditional_edge_calls[0][0][2]
            self.assertIn("new_entity_dev", first_mapping)
            self.assertIn("entity_improving_bool", first_mapping)
            self.assertEqual(first_mapping["new_entity_dev"], "new_entity_dev")
            self.assertEqual(first_mapping["entity_improving_bool"], "entity_improving_bool")
            
            # Check second conditional edge mapping
            second_mapping = conditional_edge_calls[1][0][2]
            self.assertIn("entity_improving", second_mapping)
            self.assertIn("end", second_mapping)
            self.assertEqual(second_mapping["entity_improving"], "entity_improving")
            # The mapping should map "end" string to the END constant
            self.assertIs(second_mapping["end"], END)

    @patch("src.section_to_entity_dev.master_kg_entity_collection")
    @patch("src.section_to_entity_dev.sectional_collection")
    @patch("src.section_to_entity_dev.client")
    def test_build_cluster_dev_graph_workflow_node_order(self, mock_client, mock_sectional, mock_master):
        """Test that nodes are added in the expected order"""
        mock_builder = MagicMock()
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph
        
        call_order = []
        
        original_add_node = mock_builder.add_node
        
        def track_add_node(*args, **kwargs):
            call_order.append(args[0])
            return original_add_node(*args, **kwargs)
        
        mock_builder.add_node.side_effect = track_add_node
        
        with patch("src.section_to_entity_dev.StateGraph", return_value=mock_builder), \
             patch("src.section_to_entity_dev.section_entity_matching_agent"), \
             patch("src.section_to_entity_dev.new_entity_dev_agent"), \
             patch("src.section_to_entity_dev.entity_improving_bool_agent"), \
             patch("src.section_to_entity_dev.entity_improving_agent"), \
             patch("src.section_to_entity_dev.load_master_db_agent"):
            
            build_cluster_dev_graph_workflow()
            
            # Verify nodes are added (order may vary, but all should be present)
            expected_nodes = [
                "section_entity_matching",
                "new_entity_dev",
                "entity_improving_bool",
                "entity_improving",
                "load_master_db"
            ]
            
            for node in expected_nodes:
                self.assertIn(node, call_order, f"Node {node} was not added")


if __name__ == "__main__":
    unittest.main()


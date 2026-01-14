import os
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import asyncio

from src.emedding_dm import embed_data_models_async


class EmbeddingDmTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_embed_data_models_async_success(self):
        """Test successful embedding of data models"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            # Create dummy proto files
            proto_file1 = os.path.join(form_proto_dm_dir_path, "form_001.proto")
            proto_file2 = os.path.join(form_proto_dm_dir_path, "form_002.proto")
            
            proto_content1 = 'message ApplicantInfo { string name = 1; }'
            proto_content2 = 'message BusinessInfo { string company = 1; }'
            
            with open(proto_file1, "w") as f:
                f.write(proto_content1)
            with open(proto_file2, "w") as f:
                f.write(proto_content2)

            # Mock proto messages extraction
            mock_proto_dict1 = {"ApplicantInfo": proto_content1}
            mock_proto_dict2 = {"BusinessInfo": proto_content2}
            
            # Mock LLM responses for sectional descriptions
            mock_llm_response1 = "Description of applicant information"
            mock_llm_response2 = "Description of business information"
            
            # Mock embeddings
            mock_embeddings1 = [0.1, 0.2, 0.3]
            mock_embeddings2 = [0.4, 0.5, 0.6]
            
            # Mock random IDs
            mock_id1 = "12345678"
            mock_id2 = "87654321"

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            with patch("src.emedding_dm.extract_proto_messages") as mock_extract, \
                 patch("src.emedding_dm.prompt_for_proto_sectional_dm") as mock_prompt, \
                 patch("src.emedding_dm.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("src.emedding_dm.call_openrouter_embeddings_async", new_callable=AsyncMock) as mock_embeddings, \
                 patch("src.emedding_dm.generate_random_id") as mock_gen_id, \
                 patch("src.emedding_dm.collection", mock_collection):
                
                # Setup mocks
                def extract_side_effect(content):
                    if "ApplicantInfo" in content:
                        return mock_proto_dict1
                    return mock_proto_dict2
                
                mock_extract.side_effect = extract_side_effect
                mock_prompt.return_value = [{"role": "system", "content": "test"}]
                
                # Mock LLM to return different responses based on call order
                llm_responses = [mock_llm_response1, mock_llm_response2]
                async def llm_side_effect(*args, **kwargs):
                    return llm_responses.pop(0) if llm_responses else mock_llm_response1
                
                mock_llm.side_effect = llm_side_effect
                
                # Mock embeddings
                embedding_responses = [[mock_embeddings1], [mock_embeddings2]]
                async def embeddings_side_effect(*args, **kwargs):
                    return embedding_responses.pop(0) if embedding_responses else [mock_embeddings1]
                
                mock_embeddings.side_effect = embeddings_side_effect
                
                # Mock random ID generation
                id_responses = [mock_id1, mock_id2]
                mock_gen_id.side_effect = lambda: id_responses.pop(0) if id_responses else mock_id1

                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify collection.add was called
                self.assertEqual(mock_collection.add.call_count, 2)

        asyncio.run(run_test())

    def test_embed_data_models_async_single_page(self):
        """Test embedding with a single proto file"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            proto_file = os.path.join(form_proto_dm_dir_path, "form_001.proto")
            proto_content = 'message TestMessage { string field = 1; }'
            
            with open(proto_file, "w") as f:
                f.write(proto_content)

            mock_proto_dict = {"TestMessage": proto_content}
            mock_llm_response = "Test description"
            mock_embeddings = [0.1, 0.2, 0.3]
            mock_id = "12345678"

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            with patch("src.emedding_dm.extract_proto_messages", return_value=mock_proto_dict), \
                 patch("src.emedding_dm.prompt_for_proto_sectional_dm", return_value=[{"role": "system", "content": "test"}]), \
                 patch("src.emedding_dm.call_openrouter_llm_async", new_callable=AsyncMock, return_value=mock_llm_response), \
                 patch("src.emedding_dm.call_openrouter_embeddings_async", new_callable=AsyncMock, return_value=[mock_embeddings]), \
                 patch("src.emedding_dm.generate_random_id", return_value=mock_id), \
                 patch("src.emedding_dm.collection", mock_collection):
                
                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify collection.add was called once
                mock_collection.add.assert_called_once()
                
                # Verify the call arguments
                call_args = mock_collection.add.call_args
                self.assertIn("documents", call_args.kwargs)
                self.assertIn("embeddings", call_args.kwargs)
                self.assertIn("ids", call_args.kwargs)
                self.assertIn("metadatas", call_args.kwargs)
                
                # Verify metadata structure
                metadatas = call_args.kwargs["metadatas"]
                self.assertEqual(len(metadatas), 1)
                self.assertIn("sectional_headings", metadatas[0])
                self.assertIn("sectional_dm", metadatas[0])
                self.assertIn("page_proto_dm_path", metadatas[0])

        asyncio.run(run_test())

    def test_embed_data_models_async_empty_directory(self):
        """Test embedding with empty directory"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "empty_proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            with patch("src.emedding_dm.collection", mock_collection):
                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify collection.add was never called
                mock_collection.add.assert_not_called()

        asyncio.run(run_test())

    def test_embed_data_models_async_llm_error_handled(self):
        """Test that LLM errors are caught and handled gracefully"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            proto_file = os.path.join(form_proto_dm_dir_path, "form_001.proto")
            proto_content = 'message TestMessage { string field = 1; }'
            
            with open(proto_file, "w") as f:
                f.write(proto_content)

            mock_proto_dict = {"TestMessage": proto_content}
            mock_embeddings = [0.1, 0.2, 0.3]
            mock_id = "12345678"

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            with patch("src.emedding_dm.extract_proto_messages", return_value=mock_proto_dict), \
                 patch("src.emedding_dm.prompt_for_proto_sectional_dm", return_value=[{"role": "system", "content": "test"}]), \
                 patch("src.emedding_dm.call_openrouter_llm_async", new_callable=AsyncMock, side_effect=Exception("LLM error")), \
                 patch("src.emedding_dm.call_openrouter_embeddings_async", new_callable=AsyncMock, return_value=[[mock_embeddings]]), \
                 patch("src.emedding_dm.generate_random_id", return_value=mock_id), \
                 patch("src.emedding_dm.collection", mock_collection), \
                 patch("builtins.print") as mock_print:
                
                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify error was printed
                mock_print.assert_called()
                self.assertIn("Error getting sectional description", str(mock_print.call_args_list))
                
                # Verify collection.add was still called with empty string for failed LLM call
                mock_collection.add.assert_called_once()
                call_args = mock_collection.add.call_args
                self.assertEqual(call_args.kwargs["documents"], [""])

        asyncio.run(run_test())

    def test_embed_data_models_async_page_processing_error_handled(self):
        """Test that page processing errors are caught and handled gracefully"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            proto_file = os.path.join(form_proto_dm_dir_path, "form_001.proto")
            proto_content = 'message TestMessage { string field = 1; }'
            
            with open(proto_file, "w") as f:
                f.write(proto_content)

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            with patch("src.emedding_dm.extract_proto_messages", side_effect=Exception("Extraction error")), \
                 patch("src.emedding_dm.collection", mock_collection), \
                 patch("builtins.print") as mock_print:
                
                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify error was printed
                mock_print.assert_called()
                self.assertIn("Error processing page", str(mock_print.call_args_list))
                
                # Verify collection.add was not called for failed page
                mock_collection.add.assert_not_called()

        asyncio.run(run_test())

    def test_embed_data_models_async_multiple_messages_per_page(self):
        """Test embedding with multiple proto messages in a single page"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            proto_file = os.path.join(form_proto_dm_dir_path, "form_001.proto")
            proto_content = 'message Message1 { string field1 = 1; } message Message2 { string field2 = 1; }'
            
            with open(proto_file, "w") as f:
                f.write(proto_content)

            mock_proto_dict = {
                "Message1": "message Message1 { string field1 = 1; }",
                "Message2": "message Message2 { string field2 = 1; }"
            }
            mock_llm_responses = ["Description 1", "Description 2"]
            mock_embeddings_list = [[0.1, 0.2], [0.3, 0.4]]
            mock_ids = ["11111111", "22222222"]

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            with patch("src.emedding_dm.extract_proto_messages", return_value=mock_proto_dict), \
                 patch("src.emedding_dm.prompt_for_proto_sectional_dm", return_value=[{"role": "system", "content": "test"}]), \
                 patch("src.emedding_dm.call_openrouter_llm_async", new_callable=AsyncMock) as mock_llm, \
                 patch("src.emedding_dm.call_openrouter_embeddings_async", new_callable=AsyncMock) as mock_embeddings, \
                 patch("src.emedding_dm.generate_random_id") as mock_gen_id, \
                 patch("src.emedding_dm.collection", mock_collection):
                
                # Setup side effects
                llm_responses = mock_llm_responses.copy()
                async def llm_side_effect(*args, **kwargs):
                    return llm_responses.pop(0) if llm_responses else mock_llm_responses[0]
                mock_llm.side_effect = llm_side_effect
                
                embeddings_responses = [mock_embeddings_list.copy()]
                async def embeddings_side_effect(*args, **kwargs):
                    return embeddings_responses.pop(0) if embeddings_responses else mock_embeddings_list[0]
                mock_embeddings.side_effect = embeddings_side_effect
                
                id_responses = mock_ids.copy()
                mock_gen_id.side_effect = lambda: id_responses.pop(0) if id_responses else mock_ids[0]

                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify collection.add was called
                mock_collection.add.assert_called_once()
                
                # Verify metadata has correct number of entries
                call_args = mock_collection.add.call_args
                metadatas = call_args.kwargs["metadatas"]
                self.assertEqual(len(metadatas), 2)
                self.assertEqual(len(call_args.kwargs["ids"]), 2)
                self.assertEqual(len(call_args.kwargs["documents"]), 2)
                self.assertEqual(len(call_args.kwargs["embeddings"]), 2)

        asyncio.run(run_test())

    def test_embed_data_models_async_sorts_proto_files(self):
        """Test that proto files are processed in sorted order"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            # Create proto files in non-sorted order
            proto_files = [
                ("form_003.proto", "message C { string field = 1; }"),
                ("form_001.proto", "message A { string field = 1; }"),
                ("form_002.proto", "message B { string field = 1; }"),
            ]
            
            for filename, content in proto_files:
                filepath = os.path.join(form_proto_dm_dir_path, filename)
                with open(filepath, "w") as f:
                    f.write(content)

            mock_proto_dict = {"Test": "message Test { string field = 1; }"}
            mock_llm_response = "Test description"
            mock_embeddings = [0.1, 0.2, 0.3]
            mock_id = "12345678"

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            processed_files = []

            def extract_side_effect(content):
                # Track which file is being processed
                import inspect
                frame = inspect.currentframe()
                # Get the caller's local variables to find the file path
                # This is a bit hacky, but we can track via the content
                if "message A" in content:
                    processed_files.append("form_001.proto")
                elif "message B" in content:
                    processed_files.append("form_002.proto")
                elif "message C" in content:
                    processed_files.append("form_003.proto")
                return mock_proto_dict

            with patch("src.emedding_dm.extract_proto_messages", side_effect=extract_side_effect), \
                 patch("src.emedding_dm.prompt_for_proto_sectional_dm", return_value=[{"role": "system", "content": "test"}]), \
                 patch("src.emedding_dm.call_openrouter_llm_async", new_callable=AsyncMock, return_value=mock_llm_response), \
                 patch("src.emedding_dm.call_openrouter_embeddings_async", new_callable=AsyncMock, return_value=[[mock_embeddings]]), \
                 patch("src.emedding_dm.generate_random_id", return_value=mock_id), \
                 patch("src.emedding_dm.collection", mock_collection):
                
                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify all files were processed
                self.assertEqual(len(processed_files), 3)
                # Verify they were processed in sorted order
                self.assertEqual(processed_files, ["form_001.proto", "form_002.proto", "form_003.proto"])

        asyncio.run(run_test())

    def test_embed_data_models_async_skips_none_results(self):
        """Test that None results from failed pages are skipped"""
        async def run_test():
            form_proto_dm_dir_path = os.path.join(self.temp_dir, "proto_dm")
            os.makedirs(form_proto_dm_dir_path, exist_ok=True)
            
            proto_file1 = os.path.join(form_proto_dm_dir_path, "form_001.proto")
            proto_file2 = os.path.join(form_proto_dm_dir_path, "form_002.proto")
            
            with open(proto_file1, "w") as f:
                f.write("message Test1 { string field = 1; }")
            with open(proto_file2, "w") as f:
                f.write("message Test2 { string field = 1; }")

            mock_proto_dict = {"Test": "message Test { string field = 1; }"}
            mock_llm_response = "Test description"
            mock_embeddings = [0.1, 0.2, 0.3]
            mock_id = "12345678"

            mock_collection = MagicMock()
            mock_collection.add = MagicMock()

            call_count = 0
            def extract_side_effect(content):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("First file error")
                return mock_proto_dict

            with patch("src.emedding_dm.extract_proto_messages", side_effect=extract_side_effect), \
                 patch("src.emedding_dm.prompt_for_proto_sectional_dm", return_value=[{"role": "system", "content": "test"}]), \
                 patch("src.emedding_dm.call_openrouter_llm_async", new_callable=AsyncMock, return_value=mock_llm_response), \
                 patch("src.emedding_dm.call_openrouter_embeddings_async", new_callable=AsyncMock, return_value=[[mock_embeddings]]), \
                 patch("src.emedding_dm.generate_random_id", return_value=mock_id), \
                 patch("src.emedding_dm.collection", mock_collection), \
                 patch("builtins.print"):
                
                await embed_data_models_async(form_proto_dm_dir_path)

                # Verify collection.add was called only once (for the successful page)
                self.assertEqual(mock_collection.add.call_count, 1)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

